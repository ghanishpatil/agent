from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from ..context import ChallengeContext, FactState
from ..proposals import ActionSuggestion, HypothesisSuggestion, InterpretationNote
from ..specialists import SpecialistReasoningSource
from .contracts import CandidateVerifierRoute


class RoutedReasoningSource:
    """Phase 5 wrapper that routes candidate submissions to an explicit trusted verifier.

    Non-candidate hypotheses/actions pass through unchanged. This wrapper cannot execute or verify;
    it only produces another typed ActionSuggestion that still crosses planner, adapter, evidence
    binding, and the Phase 2 VerificationController.
    """

    def __init__(
        self,
        source: SpecialistReasoningSource,
        route: CandidateVerifierRoute | None,
    ) -> None:
        self.source = source
        self.route = route

    def suggest_hypotheses(
        self, context: ChallengeContext
    ) -> Tuple[HypothesisSuggestion, ...]:
        return self.source.suggest_hypotheses(context)

    def suggest_actions(self, context: ChallengeContext) -> Tuple[ActionSuggestion, ...]:
        actions = self.source.suggest_actions(context)
        if self.route is None:
            return actions
        routed = []
        for action in actions:
            candidate = self._route(action, context)
            if candidate is not None:
                routed.append(candidate)
        return tuple(routed)

    def interpret(self, context: ChallengeContext) -> Tuple[InterpretationNote, ...]:
        return self.source.interpret(context)

    def _route(
        self, action: ActionSuggestion, context: ChallengeContext
    ) -> ActionSuggestion | None:
        if not action.candidate_flag:
            return action
        if not self._eligible_candidate(action, context):
            # Drop the candidate action entirely before planner/adapter execution. In particular,
            # the configured verifier is never called without current evidence already bound to
            # the candidate and a kernel-SUPPORTED source hypothesis.
            return None
        parameters = dict(self.route.relevant_parameters)
        parameters.setdefault("method", self.route.method)
        input_data = (
            {self.route.input_field: action.candidate_flag}
            if self.route.input_field
            else action.candidate_flag
        )
        return replace(
            action,
            tool=self.route.tool,
            target=self.route.target,
            input_data=input_data,
            relevant_parameters=parameters,
            objective="submit observed candidate to the configured authoritative verifier",
        )

    @staticmethod
    def _eligible_candidate(
        action: ActionSuggestion, context: ChallengeContext
    ) -> bool:
        import re

        supported = any(
            view.hypothesis.hypothesis_id == action.hypothesis_id
            and view.state is FactState.SUPPORTED
            for view in context.hypothesis_views()
        )
        if not supported:
            return False
        pattern = rf"(?<![\w{{]){re.escape(action.candidate_flag)}(?![\w}}])"
        for evidence in context.snapshot.evidence:
            if action.hypothesis_id not in evidence.affected_hypotheses:
                continue
            execution = evidence.observation.execution
            output = "\n".join((execution.stdout, execution.response_body))
            fields = {
                execution.metadata.get("verified_candidate"),
                execution.metadata.get("submitted_candidate"),
            }
            if re.search(pattern, output, flags=re.UNICODE) or action.candidate_flag in fields:
                return True
        return False
