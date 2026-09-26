"""Knowledge -> Hypothesis integration as an additive, well-behaved reasoning source.

This wraps the frozen specialist brain and implements the exact Phase 3 ``ReasoningSource``
Protocol (``suggest_hypotheses`` / ``suggest_actions`` / ``interpret``) that ``ReasoningLoop``
already consumes. Retrieved knowledge is allowed to produce **typed candidate hypotheses
only** (plus the standard discriminating test for the retrieved technique). Everything then
flows through the existing pipeline unchanged:

    candidate -> hypothesis validation -> planner -> trusted execution -> classification ->
    evidence -> impact -> verification -> STOP

The source never creates evidence, verifies a flag, executes an action, bypasses the planner,
or terminates solving. It only proposes; the kernel/planner/verifier remain the authorities.

Performance-first escalation (simple deterministic budgets/thresholds, no utility framework):
  1. Fast path: on each iteration, if the frozen brain already proposes an actionable step
     (or a knowledge branch is already in progress), do NOTHING extra — no retrieval.
  2. Escalate only when the current branch stalls (no actionable proposal from brain AND no
     usable knowledge branch yet) and the retrieval budget remains.
  3. On escalation: ONE targeted retrieval, generate a small number of candidate hypotheses
     (<= max_candidates), each with its standard discriminating test.
  4. If retrieval yields nothing usable, mark knowledge exhausted and stop retrieving.
  5. Once the kernel verifies a flag, the loop stops immediately (unchanged).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import quote

from ctf_agent.context import ChallengeContext, FactState
from ctf_agent.proposals import ActionSuggestion, HypothesisSuggestion
from ctf_agent.specialists.base import (
    CandidateAction,
    SpecialistContext,
    build_submit_actions,
)

from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery


@dataclass
class KnowledgeMetrics:
    retrieval_calls: int = 0
    retrieved_records: int = 0
    unnecessary_retrievals: int = 0
    knowledge_hypotheses: int = 0
    escalations: int = 0
    knowledge_exhausted: bool = False


@dataclass(frozen=True)
class _WebTest:
    hypothesis_id: str
    statement: str
    mechanism: str
    technique: str
    param: str
    payload: str
    expected_observation: str


# Minimal deterministic technique -> standard discriminating web test table. This encodes the
# canonical first test for a retrieved technique (the same test a specialist would use), keyed by
# the retrieval layer's technique_id. It is intentionally tiny — not a utility/optimization engine.
_WEB_TESTS: Dict[str, _WebTest] = {
    "ssti": _WebTest(
        "web-ssti",
        "a server-side template may evaluate injected expressions in the name parameter",
        "ssti",
        "Server-Side Template Injection",
        "name",
        "{{7*7}}",
        "the template evaluates the expression (e.g. 49 / EVAL=49)",
    ),
    "sql-injection": _WebTest(
        "web-sqli",
        "the id parameter may be injectable, expanding or leaking rows",
        "sqli",
        "SQL Injection",
        "id",
        "1' OR '1'='1",
        "a syntax perturbation changes the response or leaks extra rows",
    ),
}


class KnowledgeAugmentedReasoningSource:
    def __init__(
        self,
        brain,
        retriever: Optional[KnowledgeRetriever],
        *,
        available_tools: Tuple[str, ...] = (),
        verifier_tool: str = "",
        flag_format: str = "",
        max_retrievals: int = 2,
        max_candidates: int = 2,
        event_sink: Optional[Callable[[str, dict], None]] = None,
    ) -> None:
        self.brain = brain
        self.retriever = retriever
        self.available_tools = available_tools
        self.verifier_tool = verifier_tool
        self.flag_format = flag_format
        self.max_retrievals = max_retrievals
        self.max_candidates = max_candidates
        self.metrics = KnowledgeMetrics()
        self._event_sink = event_sink
        self._knowledge_hypotheses: Dict[str, HypothesisSuggestion] = {}
        self._knowledge_probes: List[CandidateAction] = []
        self._cache_key: Optional[int] = None
        self._cache: Optional[Tuple[Tuple[HypothesisSuggestion, ...], Tuple[ActionSuggestion, ...]]] = None

    # -- Protocol ------------------------------------------------------------------------
    def suggest_hypotheses(self, context: ChallengeContext) -> Tuple[HypothesisSuggestion, ...]:
        base = self.brain.suggest_hypotheses(context)
        extra, _actions = self._knowledge_for(context)
        base_ids = {h.hypothesis_id for h in base}
        return base + tuple(h for h in extra if h.hypothesis_id not in base_ids)

    def suggest_actions(self, context: ChallengeContext) -> Tuple[ActionSuggestion, ...]:
        base = self.brain.suggest_actions(context)
        _hyps, extra = self._knowledge_for(context)
        return base + extra

    def interpret(self, context: ChallengeContext):
        return self.brain.interpret(context)

    # -- Knowledge computation (once per context object) ---------------------------------
    def _knowledge_for(
        self, context: ChallengeContext
    ) -> Tuple[Tuple[HypothesisSuggestion, ...], Tuple[ActionSuggestion, ...]]:
        if self._cache_key == id(context) and self._cache is not None:
            return self._cache
        result = self._compute(context)
        self._cache_key = id(context)
        self._cache = result
        return result

    def _compute(
        self, context: ChallengeContext
    ) -> Tuple[Tuple[HypothesisSuggestion, ...], Tuple[ActionSuggestion, ...]]:
        spec_ctx = SpecialistContext(challenge=context, available_tools=self.available_tools)
        knowledge_actions = self._current_knowledge_actions(spec_ctx)
        brain_actions = self.brain.suggest_actions(context)

        # Fast path: brain productive or a knowledge branch already actionable -> no retrieval.
        stalled = not brain_actions and not knowledge_actions
        if (
            stalled
            and self.retriever is not None
            and not self.metrics.knowledge_exhausted
            and self.metrics.retrieval_calls < self.max_retrievals
        ):
            self._escalate_retrieve(context)
            knowledge_actions = self._current_knowledge_actions(spec_ctx)

        return tuple(self._knowledge_hypotheses.values()), knowledge_actions

    def _current_knowledge_actions(
        self, spec_ctx: SpecialistContext
    ) -> Tuple[ActionSuggestion, ...]:
        actions: List[ActionSuggestion] = []
        # Discriminating probes for knowledge hypotheses that have NOT yet been tested. Once a probe
        # has produced evidence we stop re-emitting it: re-running is pointless and re-proposing a
        # now-duplicate action would only add anti-spray churn. Submit actions (below) take over
        # once the hypothesis is SUPPORTED.
        for probe in self._knowledge_probes:
            state = _hypothesis_state(spec_ctx, probe.hypothesis_id)
            already_tested = bool(spec_ctx.evidence_result_classes(probe.hypothesis_id))
            if state != FactState.DISPROVEN.value and not already_tested:
                actions.append(_to_action_suggestion(probe))
        # Submit actions once evidence SUPPORTS a knowledge hypothesis (frozen helper reuse).
        for submit in build_submit_actions(tuple(self._knowledge_probes), spec_ctx):
            actions.append(_to_action_suggestion(submit))
        return tuple(actions)

    def _escalate_retrieve(self, context: ChallengeContext) -> None:
        self.metrics.escalations += 1
        self.metrics.retrieval_calls += 1
        query = self._build_query(context)
        results = self.retriever.retrieve(query, k=max(self.max_candidates, 3))
        self.metrics.retrieved_records += len(results)
        self._emit("knowledge_retrieval", {"query_category": query.category, "hits": len(results)})

        base_url = context.metadata.urls[0] if context.metadata.urls else ""
        probe_tool = self._probe_tool()
        usable = 0
        # Surface up to max_candidates DISTINCT candidate mechanisms across the retrieved records.
        # Retrieved records (especially a technique taxonomy) may name several applicable
        # mechanisms; we register each as its own typed candidate hypothesis so the solver can run
        # the cheapest discriminating tests and let EVIDENCE decide which one holds. We do not pick
        # a single winner heuristically.
        for result in results:
            if usable >= self.max_candidates:
                break
            for technique in result.record.techniques:
                if usable >= self.max_candidates:
                    break
                test = _WEB_TESTS.get(technique.technique_id)
                if test is None or not base_url or not probe_tool:
                    continue
                if test.hypothesis_id in self._knowledge_hypotheses:
                    continue
                self._register_candidate(test, base_url, probe_tool, result.record.record_id)
                usable += 1

        if usable == 0:
            # Retrieval produced nothing this integration can turn into a discriminating test.
            self.metrics.unnecessary_retrievals += 1
            if self.metrics.retrieval_calls >= self.max_retrievals:
                self.metrics.knowledge_exhausted = True
            self._emit("knowledge_unusable", {"query_category": query.category})

    def _register_candidate(
        self, test: _WebTest, base_url: str, probe_tool: str, source_record: str
    ) -> None:
        self._knowledge_hypotheses[test.hypothesis_id] = HypothesisSuggestion(
            hypothesis_id=test.hypothesis_id,
            statement=test.statement,
            mechanism=test.mechanism,
            technique=test.technique,
            rationale=f"typed candidate hypothesis derived from retrieved knowledge {source_record}",
        )
        target = f"{base_url}?{test.param}={quote(test.payload)}"
        self._knowledge_probes.append(
            CandidateAction(
                hypothesis_id=test.hypothesis_id,
                objective=f"knowledge-derived discriminating test for {test.technique}",
                tool=probe_tool,
                target=target,
                input_data=None,
                relevant_parameters={},
                prerequisites=(),
                expected_observation=test.expected_observation,
                estimated_cost=1,
                candidate_flag="",
                reasoning="external knowledge named this mechanism; propose its standard cheapest "
                "discriminating test (execution/classification/verification remain the kernel's)",
            )
        )
        self.metrics.knowledge_hypotheses += 1
        self._emit("knowledge_hypothesis", {"hypothesis_id": test.hypothesis_id})

    def _build_query(self, context: ChallengeContext) -> RetrievalQuery:
        meta = context.metadata
        text = " ".join(p for p in (meta.name, meta.description, " ".join(meta.hints)) if p)
        return RetrievalQuery(text=text, category=meta.category or "", keywords=())

    def _probe_tool(self) -> str:
        for name in self.available_tools:
            if name and name != self.verifier_tool:
                return name
        return ""

    def _emit(self, kind: str, payload: dict) -> None:
        if self._event_sink is not None:
            self._event_sink(kind, payload)


def _hypothesis_state(spec_ctx: SpecialistContext, hypothesis_id: str) -> str:
    for view in spec_ctx.challenge.hypothesis_views():
        if view.hypothesis.hypothesis_id == hypothesis_id:
            return view.state.value
    return FactState.PLAUSIBLE.value


def _to_action_suggestion(action: CandidateAction) -> ActionSuggestion:
    return ActionSuggestion(
        hypothesis_id=action.hypothesis_id,
        objective=action.objective,
        tool=action.tool,
        target=action.target,
        input_data=action.input_data,
        relevant_parameters=action.relevant_parameters or {},
        prerequisites=action.prerequisites,
        expected_observation=action.expected_observation,
        rationale=action.reasoning,
        candidate_flag=action.candidate_flag,
    )
