from __future__ import annotations

from typing import Any, Callable, Mapping, Tuple

from ..context import ChallengeContext, FactState
from ..proposals import ActionSuggestion, HypothesisSuggestion, InterpretationNote
from .base import (
    SpecialistAnalysis,
    SpecialistContext,
    analysis_to_suggestions,
    current_hypothesis_state,
    validate_specialist_analysis,
)
from .registry import SpecialistRegistry
from .selection import SpecialistSelection


_FACT_STATE_RANK = {
    FactState.SUPPORTED.value: 0,
    FactState.PLAUSIBLE.value: 1,
    FactState.UNRESOLVED.value: 2,
    FactState.BLOCKED.value: 3,
}


class SpecialistReasoningSource:
    """The Strategic Brain's specialist-consulting reasoning source.

    Implements the Phase 3 ``ReasoningSource`` Protocol so it drops into ``ReasoningLoop`` as the
    ``reasoning_source`` with no other wiring. On each call it:
      1. selects the relevant specialists (not all of them),
      2. runs their ``analyze`` (advisory, side-effect-free),
      3. validates each analysis structurally (rejecting any authority violation),
      4. converts survivors into Phase 3 ``HypothesisSuggestion``/``ActionSuggestion`` objects,
      5. resolves conflicts by ordering (submit-first, then evidence-state, relevance, cost) --
         but the Phase 3 planner remains the authority on what actually runs.

    It never executes a tool, never touches kernel/evidence state, and never verifies a flag.
    """

    def __init__(
        self,
        registry: SpecialistRegistry,
        *,
        available_tools: Tuple[str, ...] = (),
        memory: object = None,
        invocation_guard: Callable[[str], bool] | None = None,
        event_sink: Callable[[str, Mapping[str, Any]], None] | None = None,
    ) -> None:
        self._registry = registry
        self._available_tools = available_tools
        self._memory = memory
        self._invocation_guard = invocation_guard
        self._event_sink = event_sink
        self.last_selection: SpecialistSelection | None = None
        self.last_analyses: Tuple[SpecialistAnalysis, ...] = ()
        self.selection_history: list[SpecialistSelection] = []
        self.analysis_history: list[Tuple[SpecialistAnalysis, ...]] = []
        self.invocation_count = 0
        self.proposal_count = 0
        self._cached_context: ChallengeContext | None = None
        self._cached_result: Tuple[SpecialistContext, Tuple[SpecialistAnalysis, ...]] | None = None

    def _specialist_context(self, context: ChallengeContext) -> SpecialistContext:
        return SpecialistContext(
            challenge=context, available_tools=self._available_tools, memory=self._memory
        )

    def _analyze(
        self, context: ChallengeContext
    ) -> Tuple[SpecialistContext, Tuple[SpecialistAnalysis, ...]]:
        # ReasoningLoop asks for hypotheses then actions with the SAME context object. Cache that
        # batch so specialists are invoked once per iteration, not twice.
        if self._cached_context is context and self._cached_result is not None:
            return self._cached_result

        specialist_context = self._specialist_context(context)
        selection = self._registry.select(specialist_context)
        self.last_selection = selection
        self.selection_history.append(selection)
        self._emit(
            "specialist_selected",
            {
                "selected": tuple(s.name for s in selection.selected),
                "scored": selection.scored,
            },
        )
        analyses: list[SpecialistAnalysis] = []
        for specialist in selection.selected:
            if self._invocation_guard is not None and not self._invocation_guard(specialist.name):
                break
            self.invocation_count += 1
            self._emit("specialist_invoked", {"specialist": specialist.name})
            analysis = specialist.analyze(specialist_context)
            try:
                validate_specialist_analysis(analysis)
            except Exception:
                # Invalid/authority-violating specialist output is dropped before it can become a
                # proposal. The planner and kernel never see it.
                continue
            analyses.append(analysis)
            self._emit(
                "specialist_proposal",
                {
                    "specialist": analysis.specialist,
                    "hypotheses": tuple(h.hypothesis_id for h in analysis.hypotheses),
                    "actions": tuple(a.objective for a in analysis.candidate_actions),
                    "memory_refs": analysis.relevant_memory_refs,
                },
            )
        self.last_analyses = tuple(analyses)
        self.analysis_history.append(self.last_analyses)
        result = (specialist_context, self.last_analyses)
        self._cached_context = context
        self._cached_result = result
        return result

    def suggest_hypotheses(self, context: ChallengeContext) -> Tuple[HypothesisSuggestion, ...]:
        _specialist_context, analyses = self._analyze(context)
        seen: set[str] = set()
        out: list[HypothesisSuggestion] = []
        for analysis in analyses:
            hypotheses, _actions = analysis_to_suggestions(analysis)
            for hypothesis in hypotheses:
                if hypothesis.hypothesis_id in seen:
                    continue
                seen.add(hypothesis.hypothesis_id)
                out.append(hypothesis)
        return tuple(out)

    def suggest_actions(self, context: ChallengeContext) -> Tuple[ActionSuggestion, ...]:
        specialist_context, analyses = self._analyze(context)
        # Collect (relevance, action) across specialists, de-duplicating identical proposals.
        collected: list[Tuple[float, ActionSuggestion]] = []
        seen: set[Tuple[str, str, str, str, str]] = set()
        for analysis in analyses:
            _hypotheses, actions = analysis_to_suggestions(analysis)
            for action in actions:
                identity = (
                    action.hypothesis_id,
                    action.objective,
                    action.tool,
                    action.target,
                    str(action.input_data),
                )
                if identity in seen:
                    continue
                seen.add(identity)
                collected.append((analysis.relevance, action))
        collected.sort(key=lambda item: self._action_sort_key(item[0], item[1], specialist_context))
        self.proposal_count += len(collected)
        return tuple(action for _relevance, action in collected)

    def interpret(self, context: ChallengeContext) -> Tuple[InterpretationNote, ...]:
        _specialist_context, analyses = self._analyze(context)
        notes: list[InterpretationNote] = []
        for analysis in analyses:
            for hypothesis in analysis.hypotheses:
                for observation in analysis.observations:
                    notes.append(InterpretationNote(hypothesis.hypothesis_id, observation))
                    break  # one interpretation note per hypothesis is enough for the audit trail
        return tuple(notes)

    def _emit(self, kind: str, payload: Mapping[str, Any]) -> None:
        if self._event_sink is not None:
            self._event_sink(kind, payload)

    def _action_sort_key(
        self, relevance: float, action: ActionSuggestion, specialist_context: SpecialistContext
    ) -> Tuple[int, int, float, int, str]:
        # Conflict-resolution ORDERING only (a tie-break hint). The planner re-ranks by
        # cheapest-discriminating-test-first over current evidence and remains the authority.
        is_submit = 0 if action.candidate_flag else 1
        state = current_hypothesis_state(specialist_context, action.hypothesis_id)
        state_rank = _FACT_STATE_RANK.get(state, 4)
        cost_proxy = 3 if action.prerequisites else 1
        return (is_submit, state_rank, -relevance, cost_proxy, action.objective)
