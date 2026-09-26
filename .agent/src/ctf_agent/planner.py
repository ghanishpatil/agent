from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Set, Tuple

from .adapters import AdapterRegistry
from .context import ChallengeContext
from .deduplication import fingerprint_action
from .hypothesis_engine import HypothesisBoard
from .memory_retrieval import AdvisoryMemory, MemoryQuery
from .models import Action, ControlDecision, HypothesisStatus, RelevantState
from .proposals import ActionSuggestion, ProposalRejected, validate_action_suggestion


@dataclass(frozen=True)
class PlannerDiagnostics:
    """Distinguishes 'nothing left to try' from 'things exist but prerequisites unmet'.

    ``blocked_only_by_prerequisites`` is True only when ``proposals`` is empty AND every
    suggestion that was otherwise valid (named an open hypothesis, passed adapter validation,
    not a duplicate) was rejected solely because its prerequisites were not yet satisfied. If
    there were zero valid suggestions to begin with (e.g. no open hypotheses, or all suggestions
    invalid/duplicates), this is False and the loop should report BLOCKED_NO_ACTIONS instead.
    """

    proposals: Tuple["ActionProposal", ...]
    blocked_only_by_prerequisites: bool
    duplicate_rejections: int = 0
    invalid_rejections: int = 0
    prerequisite_rejections: int = 0


@dataclass(frozen=True)
class ActionProposal:
    """A ranked, validated candidate action, not yet executed."""

    hypothesis_id: str
    objective: str
    tool: str
    target: str
    input_data: object
    relevant_parameters: Mapping[str, object]
    prerequisites: Tuple[str, ...]
    expected_observation: str
    cost_hint: int  # 1 (cheap) .. 5 (expensive)
    reversible: bool
    score: int
    rationale: str
    candidate_flag: str = ""

    def to_action(self, action_id: str, state_before: RelevantState) -> Action:
        return Action(
            action_id=action_id,
            objective=self.objective,
            tool=self.tool,
            target=self.target,
            input_data=self.input_data,
            relevant_parameters=self.relevant_parameters,
            prerequisites=self.prerequisites,
            state_before=state_before,
        )


class ActionPlanner:
    """Evidence-aware planner. Proposes and ranks actions; never executes or mutates state.

    Cheapest-discriminating-test-first is implemented as a simple deterministic score, not a
    utility integral: an action that could discriminate multiple still-open hypotheses ranks
    above one that only tests a single hypothesis, which ranks above everything else; ties are
    broken by lower cost, then by reversibility.
    """

    def __init__(
        self,
        adapters: AdapterRegistry,
        memory: AdvisoryMemory | None = None,
    ) -> None:
        self._adapters = adapters
        self._memory = memory

    def propose(
        self,
        context: ChallengeContext,
        board: HypothesisBoard,
        suggestions: Tuple[ActionSuggestion, ...],
        *,
        completed_fingerprints: Set[Tuple[str, str]],
        state_before: RelevantState,
        satisfied_prerequisites: Set[str] = frozenset(),
    ) -> Tuple[ActionProposal, ...]:
        result = self.propose_with_diagnostics(
            context,
            board,
            suggestions,
            completed_fingerprints=completed_fingerprints,
            state_before=state_before,
            satisfied_prerequisites=satisfied_prerequisites,
        )
        return result.proposals

    def propose_with_diagnostics(
        self,
        context: ChallengeContext,
        board: HypothesisBoard,
        suggestions: Tuple[ActionSuggestion, ...],
        *,
        completed_fingerprints: Set[Tuple[str, str]],
        state_before: RelevantState,
        satisfied_prerequisites: Set[str] = frozenset(),
    ) -> "PlannerDiagnostics":
        if context.is_verified():
            return PlannerDiagnostics((), False)

        open_hypothesis_ids = {h.hypothesis_id for h in board.open_hypotheses()}
        # A SUPPORTED hypothesis is no longer "open" for further discriminating testing, but a
        # submission attempt (a suggestion carrying candidate_flag) is a distinct, final action --
        # not more testing of an already-resolved question -- so it remains proposable even though
        # the hypothesis itself is terminal. DISPROVEN hypotheses get no such exception: there is
        # nothing left worth submitting for a mechanism the evidence has already ruled out.
        submittable_hypothesis_ids = {
            h.hypothesis_id for h in board.all_hypotheses() if h.status is HypothesisStatus.SUPPORTED
        }
        if not open_hypothesis_ids and not submittable_hypothesis_ids:
            return PlannerDiagnostics((), False)

        proposals: list[ActionProposal] = []
        blocked_only_by_prerequisites = False
        duplicate_rejections = 0
        invalid_rejections = 0
        prerequisite_rejections = 0
        for suggestion in suggestions:
            proposal = self._to_proposal(
                suggestion, open_hypothesis_ids, submittable_hypothesis_ids
            )
            if proposal is None:
                invalid_rejections += 1
                continue
            if self._is_duplicate(proposal, state_before, completed_fingerprints):
                duplicate_rejections += 1
                continue
            if not self._prerequisites_met(proposal, satisfied_prerequisites):
                blocked_only_by_prerequisites = True
                prerequisite_rejections += 1
                continue
            proposals.append(proposal)

        ranked = tuple(sorted(proposals, key=self._rank_key, reverse=True))
        return PlannerDiagnostics(
            ranked,
            blocked_only_by_prerequisites and not ranked,
            duplicate_rejections=duplicate_rejections,
            invalid_rejections=invalid_rejections,
            prerequisite_rejections=prerequisite_rejections,
        )

    def _to_proposal(
        self,
        suggestion: ActionSuggestion,
        open_hypothesis_ids: Set[str],
        submittable_hypothesis_ids: Set[str] = frozenset(),
    ) -> ActionProposal | None:
        is_submission_of_a_supported_hypothesis = (
            bool(suggestion.candidate_flag)
            and suggestion.hypothesis_id in submittable_hypothesis_ids
        )
        if (
            suggestion.hypothesis_id not in open_hypothesis_ids
            and not is_submission_of_a_supported_hypothesis
        ):
            return None
        try:
            validate_action_suggestion(suggestion, self._adapters)
        except ProposalRejected:
            return None

        cost_hint = self._cost_hint(suggestion)
        score = self._score(suggestion, open_hypothesis_ids)
        return ActionProposal(
            hypothesis_id=suggestion.hypothesis_id,
            objective=suggestion.objective,
            tool=suggestion.tool,
            target=suggestion.target,
            input_data=suggestion.input_data,
            relevant_parameters=dict(suggestion.relevant_parameters or {}),
            prerequisites=suggestion.prerequisites,
            expected_observation=suggestion.expected_observation,
            cost_hint=cost_hint,
            reversible=cost_hint <= 2,
            score=score,
            rationale=suggestion.rationale,
            candidate_flag=suggestion.candidate_flag,
        )

    def _cost_hint(self, suggestion: ActionSuggestion) -> int:
        """A simple deterministic heuristic, not elaborate math.

        A read-only file/analysis probe with no side effects is cheap; anything with prerequisites
        (setup already required) or a state-changing objective is treated as more expensive.
        """
        if suggestion.prerequisites:
            return 3
        if "state_changed" in str(suggestion.relevant_parameters or "").lower():
            return 4
        return 1

    def _score(self, suggestion: ActionSuggestion, open_hypothesis_ids: Set[str]) -> int:
        discriminates = 1 if suggestion.expected_observation else 0
        # Bucket 3 if the proposal names a hypothesis AND there are >=2 open hypotheses overall
        # (meaning picking this test also narrows the field by ruling competitors out later).
        if discriminates and len(open_hypothesis_ids) >= 2:
            information_gain_bucket = 3
        elif discriminates:
            information_gain_bucket = 2
        else:
            information_gain_bucket = 1
        return information_gain_bucket * 10 - self._cost_hint(suggestion)

    def _rank_key(self, proposal: ActionProposal) -> tuple[int, int, int]:
        return (proposal.score, -proposal.cost_hint, int(proposal.reversible))

    def _is_duplicate(
        self,
        proposal: ActionProposal,
        state_before: RelevantState,
        completed_fingerprints: Set[Tuple[str, str]],
    ) -> bool:
        probe_action = proposal.to_action("probe", state_before)
        fingerprint = fingerprint_action(probe_action)
        from .deduplication import fingerprint_state

        identity = (fingerprint, fingerprint_state(state_before))
        return identity in completed_fingerprints

    def _prerequisites_met(
        self, proposal: ActionProposal, satisfied_prerequisites: Set[str]
    ) -> bool:
        if not proposal.prerequisites:
            return True
        return all(prereq in satisfied_prerequisites for prereq in proposal.prerequisites)

    def retrieve_advisory_hints(self, category: str, keywords: Tuple[str, ...]):
        if self._memory is None:
            return None
        return self._memory.retrieve(MemoryQuery(category=category, keywords=keywords))
