from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Set, Tuple

from .adapters import AdapterRegistry
from .autonomy.control import AutonomyController, ControlSignal
from .context import ChallengeContext, ChallengeMetadata, build_context
from .deduplication import fingerprint_action, fingerprint_state
from .hypothesis_engine import HypothesisBoard
from .journal import JournalEvent, JournalEventKind, RuntimeJournal
from .kernel import PipelineResult, TrustKernel
from .llm_boundary import ReasoningSource
from .models import ControlDecision, FlagCandidate, RelevantState, TestSpecification
from .planner import ActionPlanner, ActionProposal, PlannerDiagnostics
from .proposals import ActionSuggestion, ProposalRejected, validate_hypothesis_suggestion


class LoopOutcome(str, Enum):
    """Deliberately does NOT include an 'IMPOSSIBLE' value.

    A tool/environment/auth/network failure only ever produces UNRESOLVES/BLOCKS_TEST on the one
    hypothesis it touched (Phase 2 guarantee); it is never grounds for declaring the whole run
    impossible. The loop can only report that it verified something, ran out of proposals, ran out
    of budget, or is blocked on prerequisites nothing in this run can satisfy.
    """

    VERIFIED = "VERIFIED"
    BLOCKED_NO_ACTIONS = "BLOCKED_NO_ACTIONS"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    BLOCKED_PREREQUISITES = "BLOCKED_PREREQUISITES"
    TIMEOUT = "TIMEOUT"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class LoopResult:
    outcome: LoopOutcome
    actions_taken: int
    context: ChallengeContext
    pipeline_results: Tuple[PipelineResult, ...]


@dataclass
class ReasoningLoop:
    """The controlled orchestration loop.

    It calls ``TrustKernel.process()`` for every action and never constructs ``Evidence``,
    ``Hypothesis`` (beyond seeding OPEN ones), or ``FlagCandidate`` state on its own. State
    (``HypothesisBoard``, completed-action fingerprints, satisfied prerequisites, current
    ``RelevantState``) persists across iterations on ``self`` -- there is no "restart reasoning
    from scratch" between actions.
    """

    metadata: ChallengeMetadata
    kernel: TrustKernel
    adapters: AdapterRegistry
    planner: ActionPlanner
    reasoning_source: ReasoningSource
    journal: RuntimeJournal
    run_id: str
    clock: Callable[[], datetime]
    board: HypothesisBoard = field(default_factory=HypothesisBoard)
    satisfied_prerequisites: Set[str] = field(default_factory=set)
    trusted_sources_for_disproof: dict[str, TestSpecification] = field(default_factory=dict)
    controller: AutonomyController | None = None
    _completed_fingerprints: Set[Tuple[str, str]] = field(default_factory=set, init=False)
    _pipeline_results: list = field(default_factory=list, init=False)
    _action_ids: itertools.count = field(default_factory=lambda: itertools.count(1), init=False)

    def run(self, current_state: RelevantState, *, max_actions: int) -> LoopResult:
        for _ in range(max_actions):
            context = self._build_context()
            if context.is_verified():
                return self._finish(LoopOutcome.VERIFIED, context)

            controlled = self._before_iteration(context)
            if controlled is not None:
                return self._finish(controlled, context)

            self._seed_hypotheses(context)

            diagnostics = self._select_next(context, current_state)
            if not diagnostics.proposals:
                if diagnostics.blocked_only_by_prerequisites:
                    return self._finish(LoopOutcome.BLOCKED_PREREQUISITES, context)
                return self._finish(LoopOutcome.BLOCKED_NO_ACTIONS, context)
            proposal = diagnostics.proposals[0]

            controlled = self._before_action(proposal, current_state)
            if controlled is not None:
                return self._finish(controlled, context)
            current_state = self._execute_one(proposal, current_state)

        context = self._build_context()
        if context.is_verified():
            return self._finish(LoopOutcome.VERIFIED, context)
        if self.controller is not None and self.controller.deadline_expired():
            return self._finish(LoopOutcome.TIMEOUT, context)
        return self._finish(LoopOutcome.BUDGET_EXHAUSTED, context)

    def _before_iteration(self, context: ChallengeContext) -> LoopOutcome | None:
        if self.controller is None:
            return None
        return self._outcome_for_signal(self.controller.before_iteration(context))

    def _before_action(
        self, proposal: ActionProposal, current_state: RelevantState
    ) -> LoopOutcome | None:
        if self.controller is None:
            return None
        return self._outcome_for_signal(
            self.controller.before_action(proposal, current_state)
        )

    @staticmethod
    def _outcome_for_signal(signal: ControlSignal) -> LoopOutcome | None:
        if signal is ControlSignal.CONTINUE:
            return None
        if signal is ControlSignal.TIMEOUT:
            return LoopOutcome.TIMEOUT
        if signal is ControlSignal.EXHAUSTED:
            return LoopOutcome.BUDGET_EXHAUSTED
        return LoopOutcome.BLOCKED_PREREQUISITES

    def _finish(self, outcome: LoopOutcome, context: ChallengeContext) -> LoopResult:
        self.journal.append(
            JournalEvent(
                self.run_id,
                JournalEventKind.CONTROL_DECISION,
                self.clock(),
                {"outcome": outcome.value, "actions_taken": len(self._pipeline_results)},
            )
        )
        return LoopResult(
            outcome=outcome,
            actions_taken=len(self._pipeline_results),
            context=context,
            pipeline_results=tuple(self._pipeline_results),
        )

    def _build_context(self) -> ChallengeContext:
        return build_context(self.metadata, self.kernel, self.board)

    def _seed_hypotheses(self, context: ChallengeContext) -> None:
        """Seed any newly-proposed hypotheses onto the board via the authoritative
        ``board.propose_hypothesis`` (OPEN only).

        This is the one additive Phase 4 hook: the reasoning source (e.g. the specialist brain) may
        propose hypotheses, and they enter the board here -- validated, de-duplicated by id, and
        never with a terminal status. ``ScriptedReasoningSource.suggest_hypotheses`` returns ``()``
        by default, so every pre-existing Phase 3 loop run is unaffected.
        """
        existing = {h.hypothesis_id for h in self.board.all_hypotheses()}
        for suggestion in self.reasoning_source.suggest_hypotheses(context):
            if suggestion.hypothesis_id in existing:
                continue
            try:
                validate_hypothesis_suggestion(suggestion)
            except ProposalRejected:
                continue
            self.board.propose_hypothesis(
                suggestion.hypothesis_id,
                suggestion.statement,
                mechanism=suggestion.mechanism,
                technique=suggestion.technique,
            )
            existing.add(suggestion.hypothesis_id)
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.HYPOTHESIS_PROPOSED,
                    self.clock(),
                    {
                        "hypothesis_id": suggestion.hypothesis_id,
                        "mechanism": suggestion.mechanism,
                        "technique": suggestion.technique,
                    },
                )
            )

    def _select_next(
        self, context: ChallengeContext, current_state: RelevantState
    ) -> PlannerDiagnostics:
        suggestions: Tuple[ActionSuggestion, ...] = self.reasoning_source.suggest_actions(context)
        if self.controller is not None:
            self.controller.observe_suggestions(suggestions, current_state)
        diagnostics = self.planner.propose_with_diagnostics(
            context,
            self.board,
            suggestions,
            completed_fingerprints=self._completed_fingerprints,
            state_before=current_state,
            satisfied_prerequisites=self.satisfied_prerequisites,
        )
        if self.controller is not None:
            self.controller.observe_planner(diagnostics)
        self.journal.append(
            JournalEvent(
                self.run_id,
                JournalEventKind.PLANNER_DECISION,
                self.clock(),
                {
                    "suggestions": len(suggestions),
                    "valid_proposals": len(diagnostics.proposals),
                    "selected": diagnostics.proposals[0].objective
                    if diagnostics.proposals
                    else None,
                    "blocked_only_by_prerequisites": diagnostics.blocked_only_by_prerequisites,
                    "duplicate_rejections": diagnostics.duplicate_rejections,
                    "invalid_rejections": diagnostics.invalid_rejections,
                    "prerequisite_rejections": diagnostics.prerequisite_rejections,
                },
            )
        )
        if suggestions and not diagnostics.proposals:
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.DEDUPLICATION_REJECTED,
                    self.clock(),
                    {"proposal_count": len(suggestions), "reason": "planner rejected all proposals"},
                )
            )
        return diagnostics

    def _execute_one(
        self, proposal: ActionProposal, current_state: RelevantState
    ) -> RelevantState:
        action_id = f"a{next(self._action_ids)}"
        action = proposal.to_action(action_id, current_state)

        self.journal.append(
            JournalEvent(
                self.run_id,
                JournalEventKind.ACTION_PROPOSED,
                self.clock(),
                {"action_id": action_id, "tool": action.tool, "objective": action.objective},
            )
        )

        spec = self.trusted_sources_for_disproof.get(proposal.hypothesis_id)
        # A candidate submission is a verification action, not another discriminating test of the
        # mechanism. Re-applying the analysis TestSpecification to a separate verifier response
        # can incorrectly demote a previously SUPPORTED hypothesis to UNRESOLVED. Candidate
        # verification remains entirely in the Phase 2 VerificationController below.
        if spec is not None and not proposal.candidate_flag:
            self.kernel.register_test(action, spec)

        execution = self.adapters.execute(action)
        deadline_expired = bool(
            self.controller is not None and self.controller.deadline_expired()
        )
        self.journal.append(
            JournalEvent(
                self.run_id,
                JournalEventKind.ACTION_EXECUTED,
                self.clock(),
                {"action_id": action_id, "tool": execution.tool},
            )
        )

        hypothesis = self.board.get(proposal.hypothesis_id)

        candidate = None
        candidate_evidence_ids: Tuple[str, ...] = ()
        verifier = ""
        if proposal.candidate_flag and not deadline_expired:
            # Advisory only: the LLM/planner may *name* a candidate to try, but the kernel's
            # VerificationController independently decides -- from prior evidence already bound to
            # this hypothesis -- whether it is actually accepted. Naming a candidate here can never
            # itself verify it. A submission attempt requires at least one existing evidence record
            # (Phase 2's FlagAttemptRegistry rejects an empty evidence set outright); if none exists
            # yet, this action just runs as a normal probe and no candidate is attached this round.
            existing_evidence_ids = tuple(
                evidence.evidence_id
                for evidence in self.kernel.evidence.records
                if proposal.hypothesis_id in evidence.affected_hypotheses
                and self._evidence_is_bound_to(evidence, proposal.candidate_flag)
            )
            if existing_evidence_ids:
                candidate = FlagCandidate(proposal.candidate_flag, proposal.hypothesis_id)
                candidate_evidence_ids = existing_evidence_ids
                verifier = action.target
                self.journal.append(
                    JournalEvent(
                        self.run_id,
                        JournalEventKind.CANDIDATE_CREATED,
                        self.clock(),
                        {
                            "hypothesis_id": proposal.hypothesis_id,
                            "candidate": proposal.candidate_flag,
                            "evidence_ids": existing_evidence_ids,
                        },
                    )
                )
                self.journal.append(
                    JournalEvent(
                        self.run_id,
                        JournalEventKind.VERIFICATION_ATTEMPTED,
                        self.clock(),
                        {"hypothesis_id": proposal.hypothesis_id, "verifier": verifier},
                    )
                )

        result = self.kernel.process(
            action=action,
            execution=execution,
            hypothesis=hypothesis,
            observed_at=self.clock(),
            source=action.target,
            candidate=candidate,
            candidate_evidence_ids=candidate_evidence_ids,
            verifier=verifier,
        )
        self._pipeline_results.append(result)

        if result.decision is not ControlDecision.DUPLICATE:
            self._completed_fingerprints.add(
                (fingerprint_action(action), fingerprint_state(current_state))
            )

        if result.observation is not None:
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.RESULT_CLASSIFIED,
                    self.clock(),
                    {
                        "action_id": action_id,
                        "result_class": result.classification.result_class.value
                        if result.classification
                        else None,
                    },
                )
            )
        if result.evidence is not None:
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.EVIDENCE_RECORDED,
                    self.clock(),
                    {"action_id": action_id, "evidence_id": result.evidence.evidence_id},
                )
            )
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.EVIDENCE_IMPACT,
                    self.clock(),
                    {
                        "action_id": action_id,
                        "hypothesis_id": result.hypothesis.hypothesis_id,
                        "impact": result.impact.value,
                    },
                )
            )
            self.board.record(result)
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.HYPOTHESIS_TRANSITIONED,
                    self.clock(),
                    {
                        "hypothesis_id": result.hypothesis.hypothesis_id,
                        "status": result.hypothesis.status.value,
                        "impact": result.impact.value,
                    },
                )
            )
            self._close_low_value_branch(result)

        if result.verification is not None:
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.VERIFICATION_COMPLETED,
                    self.clock(),
                    {
                        "candidate": result.verification.candidate.value,
                        "status": result.verification.candidate.verification_status.value,
                        "decision": result.verification.decision.value,
                    },
                )
            )
            if result.decision is ControlDecision.STOP:
                self.journal.append(
                    JournalEvent(
                        self.run_id,
                        JournalEventKind.STOP_REACHED,
                        self.clock(),
                        {"action_id": action_id, "reason": result.verification.reason},
                    )
                )

        if self.controller is None:
            return current_state
        update = self.controller.after_result(proposal, result, current_state)
        self.satisfied_prerequisites.difference_update(update.remove_prerequisites)
        self.satisfied_prerequisites.update(update.add_prerequisites)
        if update.state != current_state:
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.STATE_CHANGED,
                    self.clock(),
                    {
                        "from_revision": current_state.environment.revision,
                        "to_revision": update.state.environment.revision,
                        "added_prerequisites": update.add_prerequisites,
                        "removed_prerequisites": update.remove_prerequisites,
                    },
                )
            )
        return update.state

    @staticmethod
    def _evidence_is_bound_to(evidence, candidate_value: str) -> bool:
        """Mirrors FlagAttemptRegistry.check_and_record's own binding rule.

        Filtering with this exact rule *before* calling kernel.process() means an LLM's wrong
        guess at a candidate value degrades to "run this as a normal probe, no candidate attached"
        instead of raising ValueError out of the kernel and crashing the loop.
        """
        import re

        execution = evidence.observation.execution
        output = "\n".join((execution.stdout, execution.response_body))
        pattern = rf"(?<![\w{{]){re.escape(candidate_value)}(?![\w}}])"
        if re.search(pattern, output, flags=re.UNICODE):
            return True
        candidate_fields = {
            execution.metadata.get("verified_candidate"),
            execution.metadata.get("submitted_candidate"),
        }
        return candidate_value in candidate_fields

    def _close_low_value_branch(self, result: PipelineResult) -> None:
        """Anti-loop: repeatedly-unresolved/blocked hypotheses get deprioritized, not disproven."""
        from .models import HypothesisImpact

        if result.impact not in {HypothesisImpact.UNRESOLVES, HypothesisImpact.BLOCKS_TEST}:
            return
        hypothesis_id = result.hypothesis.hypothesis_id
        unresolved_count = len(result.hypothesis.unresolved_evidence)
        if unresolved_count >= 3:
            self.board.set_priority(hypothesis_id, 0)
            self.journal.append(
                JournalEvent(
                    self.run_id,
                    JournalEventKind.DEAD_END_CLOSED,
                    self.clock(),
                    {
                        "hypothesis_id": hypothesis_id,
                        "reason": "three unresolved or blocked observations without progress",
                    },
                )
            )
