"""Controlled, advisory-only integration of the Knowledge Translation Layer into the solve path.

This is a CONTROLLED EXPERIMENT, not a solver change. It introduces the smallest possible explicit
switch — ``KnowledgeMode`` (``OFF`` | ``EXPERIMENTAL``), default ``OFF`` — and a treatment reasoning
source that turns retrieved knowledge into advisory ``HypothesisSuggestion`` / ``ActionSuggestion``
via :class:`~ctf_experiment.knowledge_translation.KnowledgeTranslator`, then lets the EXISTING frozen
pipeline own everything else.

Boundaries (enforced):

* ``OFF`` behaves exactly like the existing brain-only path (the treatment source adds nothing).
* Knowledge is ADVISORY: it only proposes typed hypotheses/actions; it never executes a tool,
  verifies a flag, disproves a hypothesis, injects a historical flag, or bypasses the planner /
  TrustKernel / adapters / classifier / verification.
* Reuses the EXISTING composition (``solve_with_knowledge`` via an additive injection hook) and the
  EXISTING dedup / planner / kernel / evidence ledger. No second dedup or eval system.
* Failure-safe: any retrieval/translation/proposal error is isolated and logged; the solver
  continues on the normal reasoning path.
* Deterministic; no network/model/clock inside translation.

The composition arm is ``solve_experimental``. Contribution attribution (``classify_contribution``)
is EVIDENCE-BASED: it inspects the actual executed trace, not the mere fact that retrieval happened.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    SolveConstraints,
    SolveResult,
    SolveStatus,
)
from ctf_agent.context import ChallengeContext, FactState
from ctf_agent.specialists.base import CandidateAction

from ctf_ingest.retrieval import KnowledgeRetriever

from .knowledge_reasoning import KnowledgeAugmentedReasoningSource, KnowledgeMetrics
from .knowledge_solver import KnowledgeSolveOutput, solve_with_knowledge
from .knowledge_translation import (
    KnowledgeTranslator,
    TranslationContext,
    TranslationResult,
    TranslationStatus,
)

# The objective signature the knowledge-derived probe carries (same shape the existing bridge uses),
# so executed knowledge tests are identifiable in the authoritative SolveResult trace.
_KNOWLEDGE_OBJECTIVE_PREFIX = "knowledge-derived discriminating test"


class KnowledgeMode(str, Enum):
    """The explicit experimental switch. Default is OFF everywhere."""

    OFF = "OFF"
    EXPERIMENTAL = "EXPERIMENTAL"


class KnowledgeContribution(str, Enum):
    """Evidence-based classification of how much retrieved knowledge actually contributed."""

    NO_KNOWLEDGE = "NO_KNOWLEDGE"
    KNOWLEDGE_HYPOTHESIS_ONLY = "KNOWLEDGE_HYPOTHESIS_ONLY"
    KNOWLEDGE_GUIDED_TEST = "KNOWLEDGE_GUIDED_TEST"
    KNOWLEDGE_DIRECTLY_ENABLED_SOLVE = "KNOWLEDGE_DIRECTLY_ENABLED_SOLVE"


# =========================================================================================
# proposal trace (attribution input)
# =========================================================================================

@dataclass
class KnowledgeTrace:
    """A record of what knowledge PROPOSED during a run (not what it executed — the kernel owns that).

    All counters are advisory bookkeeping for the evaluation. ``fabricated_execution_attempts`` must
    always be 0: the translator downgrades ungrounded/invented proposals to hypothesis-only before
    they can ever become a probe, so nothing fabricated ever reaches the planner.
    """

    proposals: List[Dict[str, object]] = field(default_factory=list)
    runnable_hypotheses: List[str] = field(default_factory=list)
    hypothesis_only: List[str] = field(default_factory=list)
    alignment_failures: int = 0
    conflicts: int = 0
    unsupported_downgrades: int = 0        # wanted-to-run but missing grounded evidence
    fabricated_execution_attempts: int = 0  # MUST stay 0
    errors: List[str] = field(default_factory=list)

    def record(self, tr: TranslationResult, source_record_id: str) -> None:
        self.proposals.append({
            "source_record_id": source_record_id,
            "origin": tr.provenance.origin.value,
            "technique_id": tr.technique_id,
            "hypothesis_id": tr.hypothesis.hypothesis_id if tr.hypothesis else "",
            "status": tr.status.value,
            "applicability": tr.applicability.value,
            "mechanism": tr.mechanism,
            "reason": tr.reason,
        })
        if tr.status is TranslationStatus.RUNNABLE_TEST and tr.hypothesis:
            self.runnable_hypotheses.append(tr.hypothesis.hypothesis_id)
        elif tr.status is TranslationStatus.HYPOTHESIS_ONLY and tr.hypothesis:
            self.hypothesis_only.append(tr.hypothesis.hypothesis_id)
            if tr.missing_requirements or "alignment failed" in tr.reason or "byte-match" in tr.reason:
                self.unsupported_downgrades += 1
            if "alignment failed" in tr.reason or "byte-match" in tr.reason:
                self.alignment_failures += 1
        elif tr.status is TranslationStatus.ADVISORY_CONFLICT:
            self.conflicts += 1

    def to_dict(self) -> Dict[str, object]:
        return {
            "proposal_count": len(self.proposals),
            "runnable_hypotheses": list(self.runnable_hypotheses),
            "hypothesis_only": list(self.hypothesis_only),
            "alignment_failures": self.alignment_failures,
            "conflicts": self.conflicts,
            "unsupported_downgrades": self.unsupported_downgrades,
            "fabricated_execution_attempts": self.fabricated_execution_attempts,
            "errors": list(self.errors),
            "proposals": list(self.proposals),
        }


# =========================================================================================
# treatment reasoning source
# =========================================================================================

class ExperimentalTranslationSource(KnowledgeAugmentedReasoningSource):
    """Advisory knowledge source backed by the generalized :class:`KnowledgeTranslator`.

    Reuses the parent's fast-path escalation, per-context caching, dedup-aware action emission
    (``_current_knowledge_actions``), probe-tool selection, and metrics. It overrides ONLY the
    retrieval->proposal step so proposals come from trajectory-first translation instead of the
    narrow ``_WEB_TESTS`` table. When ``knowledge_mode`` is ``OFF`` it is a pure pass-through to the
    frozen brain.
    """

    def __init__(
        self, brain, retriever, *, knowledge_mode: KnowledgeMode = KnowledgeMode.OFF,
        translator: Optional[KnowledgeTranslator] = None, available_tools: Tuple[str, ...] = (),
        verifier_tool: str = "", flag_format: str = "", max_retrievals: int = 2,
        max_candidates: int = 2, event_sink=None,
    ) -> None:
        super().__init__(
            brain, retriever, available_tools=available_tools, verifier_tool=verifier_tool,
            flag_format=flag_format, max_retrievals=max_retrievals, max_candidates=max_candidates,
            event_sink=event_sink,
        )
        self.knowledge_mode = knowledge_mode
        self.translator = translator or KnowledgeTranslator()
        self.trace = KnowledgeTrace()

    # OFF => pure pass-through (byte-identical to brain-only; existing baseline preserved).
    def _knowledge_for(self, context: ChallengeContext):
        if self.knowledge_mode is not KnowledgeMode.EXPERIMENTAL:
            return (), ()
        return super()._knowledge_for(context)

    def _grounded_context(self, context: ChallengeContext) -> TranslationContext:
        # only GROUNDED current facts; nothing invented. Current DISPROVEN evidence outranks
        # knowledge, surfaced as disproven_mechanisms so the translator returns ADVISORY_CONFLICT.
        id_to_mech = {t.hypothesis_id: t.mechanism for t in self.translator.registry.all_templates()}
        disproven = []
        for view in context.hypothesis_views():
            if view.state is FactState.DISPROVEN:
                mech = id_to_mech.get(view.hypothesis.hypothesis_id)
                if mech:
                    disproven.append(mech)
        return TranslationContext(
            category=context.metadata.category or "",
            target_urls=tuple(context.metadata.urls),
            available_tools=tuple(self.available_tools),
            verifier_tool=self.verifier_tool,
            known_parameters=(),
            exact_targets=(),
            disproven_mechanisms=tuple(disproven),
        )

    def _escalate_retrieve(self, context: ChallengeContext) -> None:
        # FAILURE-SAFE: any error here must never break solving; fall back to the base reasoning
        # path with knowledge marked exhausted.
        try:
            self.metrics.escalations += 1
            self.metrics.retrieval_calls += 1
            query = self._build_query(context)
            results = self.retriever.retrieve(query, k=max(self.max_candidates, 3))
            self.metrics.retrieved_records += len(results)
            self._emit("knowledge_retrieval", {"query_category": query.category, "hits": len(results)})

            tctx = self._grounded_context(context)
            usable = 0
            for result in results:
                if usable >= self.max_candidates:
                    break
                for translation in self.translator.translate_record(result.record, tctx):
                    if usable >= self.max_candidates:
                        break
                    if self._ingest_translation(translation, result.record.record_id):
                        usable += 1

            if usable == 0:
                self.metrics.unnecessary_retrievals += 1
                if self.metrics.retrieval_calls >= self.max_retrievals:
                    self.metrics.knowledge_exhausted = True
                self._emit("knowledge_unusable", {"query_category": query.category})
        except Exception as exc:  # noqa: BLE001 — knowledge failure is isolated + logged
            self.trace.errors.append(f"{type(exc).__name__}: {exc}")
            self.metrics.knowledge_exhausted = True
            self._emit("knowledge_error", {"error": f"{type(exc).__name__}: {exc}"})

    def _ingest_translation(self, tr: TranslationResult, source_record_id: str) -> bool:
        """Register a translation as advisory proposals. Returns True iff it added a runnable probe."""
        self.trace.record(tr, source_record_id)
        if tr.hypothesis is None:
            return False
        hid = tr.hypothesis.hypothesis_id
        if hid not in self._knowledge_hypotheses:
            self._knowledge_hypotheses[hid] = tr.hypothesis
            self.metrics.knowledge_hypotheses += 1
            self._emit("knowledge_hypothesis", {"hypothesis_id": hid, "status": tr.status.value})
        if tr.status is TranslationStatus.RUNNABLE_TEST and tr.runnable_action is not None:
            if not any(p.hypothesis_id == hid for p in self._knowledge_probes):
                act = tr.runnable_action
                # candidate_flag is forced empty: a historical flag is NEVER the current flag.
                self._knowledge_probes.append(CandidateAction(
                    hypothesis_id=hid, objective=act.objective, tool=act.tool, target=act.target,
                    input_data=act.input_data, relevant_parameters=dict(act.relevant_parameters or {}),
                    prerequisites=act.prerequisites, expected_observation=act.expected_observation,
                    estimated_cost=1, candidate_flag="", reasoning=act.rationale,
                ))
                return True
        return False


# =========================================================================================
# contribution attribution (evidence-based)
# =========================================================================================

def _is_verified_solve(result: SolveResult) -> bool:
    return (
        result.status is SolveStatus.SOLVED
        and bool(result.verified_flag)
        and bool(result.verification_evidence_ids)
        and bool(result.final_verification_method)
    )


def _executed_knowledge_actions(result: SolveResult):
    return [
        a for a in result.actions
        if a.objective.startswith(_KNOWLEDGE_OBJECTIVE_PREFIX) and a.decision != "DUPLICATE"
    ]


def classify_contribution(
    result: SolveResult, trace: KnowledgeTrace, *, control_result: Optional[SolveResult] = None,
) -> KnowledgeContribution:
    """Classify knowledge contribution from the ACTUAL trace, not from mere retrieval.

    A run is only ``KNOWLEDGE_DIRECTLY_ENABLED_SOLVE`` when a knowledge-derived test actually
    executed, produced authoritative SUPPORTS evidence for a knowledge hypothesis, the run verified
    the flag, AND (when a paired control is supplied) the control did NOT independently verify-solve.
    Retrieval / a retrieved writeup / a generated hypothesis alone is never a contribution.
    """
    if not trace.proposals:
        return KnowledgeContribution.NO_KNOWLEDGE

    executed = _executed_knowledge_actions(result)
    if not executed:
        return KnowledgeContribution.KNOWLEDGE_HYPOTHESIS_ONLY

    knowledge_hyp_ids = {p["hypothesis_id"] for p in trace.proposals if p["hypothesis_id"]}
    if _is_verified_solve(result):
        supported_by_knowledge = any(
            h.hypothesis_id in knowledge_hyp_ids
            and h.status in {"SUPPORTED", "VERIFIED"}
            and bool(h.supporting_evidence)
            for h in result.key_hypotheses
        )
        supports_action = any(a.impact == "SUPPORTS" for a in executed)
        control_independently_solved = control_result is not None and _is_verified_solve(control_result)
        if supported_by_knowledge and supports_action and not control_independently_solved:
            return KnowledgeContribution.KNOWLEDGE_DIRECTLY_ENABLED_SOLVE
    return KnowledgeContribution.KNOWLEDGE_GUIDED_TEST


# =========================================================================================
# treatment composition arm
# =========================================================================================

@dataclass
class ExperimentalSolveOutput:
    result: SolveResult
    knowledge: KnowledgeMetrics
    contribution: KnowledgeContribution
    trace: KnowledgeTrace
    mode: KnowledgeMode


def solve_experimental(
    challenge: ChallengeInput,
    resources: Tuple[ChallengeResource, ...] = (),
    environment: Optional[EnvironmentConfig] = None,
    constraints: Optional[SolveConstraints] = None,
    *,
    retriever: Optional[KnowledgeRetriever] = None,
    knowledge_mode: KnowledgeMode = KnowledgeMode.OFF,
    translator: Optional[KnowledgeTranslator] = None,
    max_retrievals: int = 2,
    max_candidates: int = 2,
    control_result: Optional[SolveResult] = None,
) -> ExperimentalSolveOutput:
    """Solve via the EXISTING composition with the translation-backed advisory source injected.

    With ``knowledge_mode=OFF`` (default) the retriever is forced off and the source is inert, so
    behavior is identical to the existing brain-only path.
    """
    translator = translator or KnowledgeTranslator()
    holder: Dict[str, ExperimentalTranslationSource] = {}

    def factory(brain, retriever_arg, **kw) -> ExperimentalTranslationSource:
        src = ExperimentalTranslationSource(
            brain, retriever_arg, knowledge_mode=knowledge_mode, translator=translator, **kw
        )
        holder["src"] = src
        return src

    effective_retriever = retriever if knowledge_mode is KnowledgeMode.EXPERIMENTAL else None
    out: KnowledgeSolveOutput = solve_with_knowledge(
        challenge, resources, environment, constraints,
        retriever=effective_retriever, max_retrievals=max_retrievals,
        max_candidates=max_candidates, reasoning_source_factory=factory,
    )
    src = holder.get("src")
    trace = src.trace if src is not None else KnowledgeTrace()
    contribution = classify_contribution(out.result, trace, control_result=control_result)
    return ExperimentalSolveOutput(
        result=out.result, knowledge=out.knowledge, contribution=contribution,
        trace=trace, mode=knowledge_mode,
    )


# =========================================================================================
# paired control-vs-treatment evaluation (reuses the knowledge-v2 benchmark)
# =========================================================================================

@dataclass
class IntegrationCaseResult:
    case_id: str
    kind: str
    control: Dict[str, object]
    treatment: Dict[str, object]
    contribution: str
    metrics: Dict[str, object]
    safety: Dict[str, bool]

    def to_dict(self) -> Dict[str, object]:
        return {
            "case_id": self.case_id, "kind": self.kind, "control": self.control,
            "treatment": self.treatment, "contribution": self.contribution,
            "metrics": self.metrics, "safety_invariants": self.safety,
        }


@dataclass
class IntegrationReport:
    cases: List[IntegrationCaseResult] = field(default_factory=list)

    @property
    def knowledge_enabled_solves(self) -> int:
        return sum(1 for c in self.cases
                   if c.contribution == KnowledgeContribution.KNOWLEDGE_DIRECTLY_ENABLED_SOLVE.value)

    @property
    def all_safety_preserved(self) -> bool:
        return all(all(c.safety.values()) for c in self.cases)

    @property
    def total_fabricated_attempts(self) -> int:
        return sum(int(c.metrics.get("fabricated_execution_attempts", 0)) for c in self.cases)

    def verdict(self) -> str:
        if not self.all_safety_preserved:
            return "REJECT: a safety invariant was violated under experimental knowledge"
        if self.total_fabricated_attempts != 0:
            return "REJECT: a fabricated execution attempt reached the pipeline"
        n = self.knowledge_enabled_solves
        if n > 0:
            return (f"KNOWLEDGE-CONTRIBUTING: {n} knowledge-directly-enabled verified solve(s); "
                    "all safety invariants preserved; OFF mode unchanged")
        return "KNOWLEDGE-SAFE / NON-CONTRIBUTING: 0 knowledge-directly-enabled verified solves"

    def to_dict(self) -> Dict[str, object]:
        return {
            "case_count": len(self.cases),
            "knowledge_directly_enabled_solves": self.knowledge_enabled_solves,
            "all_safety_invariants_preserved": self.all_safety_preserved,
            "total_fabricated_execution_attempts": self.total_fabricated_attempts,
            "verdict": self.verdict(),
            "cases": [c.to_dict() for c in self.cases],
        }


def _flag_ok(case, result: SolveResult) -> bool:
    if result.verified_flag is None:
        return True
    if case.decoy_flag and result.verified_flag == case.decoy_flag:
        return False
    return result.verified_flag == case.expected_flag


def _hyp_status(result: SolveResult, hypothesis_id: str) -> Optional[str]:
    hyp = next((h for h in result.key_hypotheses if h.hypothesis_id == hypothesis_id), None)
    return hyp.status if hyp else None


def _arm_summary(out: ExperimentalSolveOutput) -> Dict[str, object]:
    r = out.result
    return {
        "status": r.status.value,
        "verified_flag": r.verified_flag,
        "actions": len(r.actions),
        "duplicate_proposals": r.budget_usage.duplicate_proposals,
        "budget_violations": r.budget_usage.budget_violations,
        "retrieval_calls": out.knowledge.retrieval_calls,
        "knowledge_hypotheses": out.knowledge.knowledge_hypotheses,
        "contribution": out.contribution.value,
    }


def run_knowledge_integration_experiment(work_root: Path, cases=None) -> IntegrationReport:
    """Paired CONTROL (knowledge OFF) vs TREATMENT (knowledge EXPERIMENTAL) over the v2 cases.

    Reuses ``build_cases_v2`` + ``web_environment`` so the two arms share identical challenge, tools,
    environment, budgets, and solver configuration; only ``knowledge_mode`` (+ retriever) differ.
    """
    from dataclasses import replace
    from .knowledge_dependent_benchmark_v2 import build_cases_v2

    work_root = Path(work_root)
    work_root.mkdir(parents=True, exist_ok=True)
    if cases is None:
        cases = build_cases_v2(work_root / "bench")

    report = IntegrationReport()
    for case in cases:
        def env(arm: str):
            base = case.environment_factory()
            root = work_root / f"{case.case_id}-{arm}"
            root.mkdir(parents=True, exist_ok=True)
            return replace(base, workspace_root=root, journal_path=root / "journal.jsonl",
                           run_id=f"{case.case_id}-{arm}")

        control = solve_experimental(
            case.challenge, (), env("control"), case.constraints, knowledge_mode=KnowledgeMode.OFF,
        )
        retriever = KnowledgeRetriever.from_records(case.treatment_records)
        treatment = solve_experimental(
            case.challenge, (), env("treatment"), case.constraints, retriever=retriever,
            knowledge_mode=KnowledgeMode.EXPERIMENTAL, control_result=control.result,
        )

        c_res, t_res = control.result, treatment.result
        tr = treatment.trace
        executed_knowledge = _executed_knowledge_actions(t_res)
        metrics = {
            "actions": len(t_res.actions),
            "duplicate_actions": t_res.budget_usage.duplicate_proposals,
            "retrieved_records": treatment.knowledge.retrieved_records,
            "translated_proposals": len(tr.proposals),
            "accepted_hypotheses": treatment.knowledge.knowledge_hypotheses,
            "runnable_proposals": len(tr.runnable_hypotheses),
            "hypothesis_only_proposals": len(tr.hypothesis_only),
            "executed_knowledge_tests": len(executed_knowledge),
            "alignment_failures": tr.alignment_failures,
            "conflicts": tr.conflicts,
            "unsupported_downgrades": tr.unsupported_downgrades,
            "fabricated_execution_attempts": tr.fabricated_execution_attempts,
            "translation_errors": len(tr.errors),
            "contribution": treatment.contribution.value,
            "false_verification": not (_flag_ok(case, c_res) and _flag_ok(case, t_res)),
            "false_disproof": (case.treatment_should_solve
                               and _hyp_status(t_res, case.expected_hypothesis) == "DISPROVEN"),
        }
        safety = {
            "no_false_verification": _flag_ok(case, c_res) and _flag_ok(case, t_res),
            "no_false_disproof": not metrics["false_disproof"],
            "no_fabricated_execution": tr.fabricated_execution_attempts == 0,
            "no_budget_violations": (c_res.budget_usage.budget_violations == 0
                                     and t_res.budget_usage.budget_violations == 0),
            "no_blind_guessing": (c_res.budget_usage.blind_retries == 0
                                  and t_res.budget_usage.blind_retries == 0),
        }
        report.cases.append(IntegrationCaseResult(
            case_id=case.case_id, kind=case.kind,
            control=_arm_summary(control), treatment=_arm_summary(treatment),
            contribution=treatment.contribution.value, metrics=metrics, safety=safety,
        ))
    return report
