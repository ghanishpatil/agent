from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Set, Tuple
from urllib.parse import urlsplit

from ..context import ChallengeContext
from ..journal import JournalEvent, JournalEventKind, RuntimeJournal
from ..kernel import PipelineResult
from ..models import EnvironmentState, RelevantState, ResultClass
from ..planner import ActionProposal
from ..proposals import ActionSuggestion
from .contracts import BudgetUsage, PermittedTool, SolveConstraints


class ControlSignal(str, Enum):
    CONTINUE = "CONTINUE"
    EXHAUSTED = "EXHAUSTED"
    TIMEOUT = "TIMEOUT"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class StateUpdate:
    state: RelevantState
    add_prerequisites: Tuple[str, ...] = ()
    remove_prerequisites: Tuple[str, ...] = ()


class AutonomyController:
    """Deny-before-execute budget gate and deterministic relevant-state reducer."""

    def __init__(
        self,
        constraints: SolveConstraints,
        tools: Tuple[PermittedTool, ...],
        journal: RuntimeJournal,
        run_id: str,
        clock,
        monotonic,
    ) -> None:
        self.constraints = constraints
        self._tools = {tool.name: tool for tool in tools}
        self._journal = journal
        self._run_id = run_id
        self._clock = clock
        self._monotonic = monotonic
        self._started = monotonic()
        self._usage = BudgetUsage()
        self.terminal_reason = ""
        self._seen_suggestions: Set[Tuple[str, str, str, str, str]] = set()
        self._unknown_state_mutation = False
        self._mutation_reason = ""

    @property
    def usage(self) -> BudgetUsage:
        return self._usage

    def before_iteration(self, context: ChallengeContext) -> ControlSignal:
        del context
        if self._unknown_state_mutation:
            self.terminal_reason = self._mutation_reason or (
                "state mutation lacked a declared revision; stopped safely"
            )
            return ControlSignal.BLOCKED
        if self._elapsed() >= self.constraints.timeout_seconds:
            self.terminal_reason = "wall-clock timeout reached"
            return ControlSignal.TIMEOUT
        if self._usage.iterations >= self.constraints.max_iterations:
            self.terminal_reason = "reasoning iteration budget exhausted"
            return ControlSignal.EXHAUSTED
        self._usage = replace(self._usage, iterations=self._usage.iterations + 1)
        self._journal_budget()
        return ControlSignal.CONTINUE

    def observe_suggestions(
        self, suggestions: Tuple[ActionSuggestion, ...], state: RelevantState
    ) -> None:
        # Retain proposal identities for audit only. Actual duplicate accounting is performed from
        # PlannerDiagnostics after the planner compares semantic fingerprints against current state.
        for suggestion in suggestions:
            self._seen_suggestions.add(
                (
                    suggestion.hypothesis_id,
                    suggestion.objective.strip().lower(),
                    suggestion.tool,
                    suggestion.target,
                    repr((suggestion.input_data, suggestion.relevant_parameters, state)),
                )
            )

    def observe_planner(self, diagnostics) -> None:
        duplicates = int(diagnostics.duplicate_rejections)
        if not duplicates:
            return
        self._usage = replace(
            self._usage,
            duplicate_proposals=self._usage.duplicate_proposals + duplicates,
        )

    def allow_specialist_invocation(self, specialist: str) -> bool:
        if self._usage.specialist_calls >= self.constraints.max_specialist_calls:
            self.terminal_reason = "specialist call budget exhausted"
            return False
        self._usage = replace(
            self._usage, specialist_calls=self._usage.specialist_calls + 1
        )
        return True

    def before_action(
        self, proposal: ActionProposal, state: RelevantState
    ) -> ControlSignal:
        del state
        if self.terminal_reason == "specialist call budget exhausted":
            return ControlSignal.EXHAUSTED
        if self._elapsed() >= self.constraints.timeout_seconds:
            self.terminal_reason = "wall-clock timeout reached"
            return ControlSignal.TIMEOUT

        tool = self._tools.get(proposal.tool)
        projected = {
            "total action": (self._usage.total_actions, self.constraints.max_actions, 1),
            "tool execution": (
                self._usage.tool_executions,
                self.constraints.max_tool_executions,
                1,
            ),
            "network action": (
                self._usage.network_actions,
                self.constraints.max_network_actions,
                int(bool(tool and tool.network)),
            ),
            "remote attempt": (
                self._usage.remote_attempts,
                self.constraints.max_remote_attempts,
                int(bool(tool and tool.remote)),
            ),
            "submission": (
                self._usage.submissions,
                self.constraints.max_submissions,
                int(bool(proposal.candidate_flag)),
            ),
            "expensive action": (
                self._usage.expensive_actions,
                self.constraints.max_expensive_actions,
                int(proposal.cost_hint >= 3),
            ),
            "total cost": (
                self._usage.total_cost,
                self.constraints.max_total_cost,
                self._cost(proposal),
            ),
        }
        for label, (used, limit, increment) in projected.items():
            if used + increment > limit:
                self.terminal_reason = f"{label} budget exhausted"
                return ControlSignal.EXHAUSTED
        return ControlSignal.CONTINUE

    def deadline_expired(self) -> bool:
        """Re-check the hard wall deadline after adapter execution and before verification."""
        if self._elapsed() < self.constraints.timeout_seconds:
            return False
        self.terminal_reason = "wall-clock timeout reached after tool execution"
        return True

    def after_result(
        self,
        proposal: ActionProposal,
        result: PipelineResult,
        state: RelevantState,
    ) -> StateUpdate:
        tool = self._tools.get(proposal.tool)
        cost = self._cost(proposal)
        self._usage = replace(
            self._usage,
            total_actions=self._usage.total_actions + 1,
            tool_executions=self._usage.tool_executions + 1,
            network_actions=self._usage.network_actions + int(bool(tool and tool.network)),
            remote_attempts=self._usage.remote_attempts + int(bool(tool and tool.remote)),
            submissions=self._usage.submissions + int(bool(proposal.candidate_flag)),
            expensive_actions=self._usage.expensive_actions + int(proposal.cost_hint >= 3),
            total_cost=self._usage.total_cost + cost,
            blind_retries=self._usage.blind_retries
            + int(result.decision.value == "DUPLICATE"),
        )
        self._journal_budget()

        if result.classification and result.classification.result_class in _FAILURES:
            self._emit(
                JournalEventKind.FAILURE_CLASSIFIED,
                {
                    "action_id": result.action.action_id,
                    "result_class": result.classification.result_class.value,
                    "meaning": "test blocked or unresolved; hypothesis not automatically disproven",
                },
            )

        execution = result.observation.execution if result.observation else None
        if execution is None or not execution.state_changed:
            return StateUpdate(state)
        metadata = execution.metadata
        parsed = self._parse_mutation(metadata, state)
        if isinstance(parsed, str):
            self._block_mutation(result.action.action_id, parsed)
            return StateUpdate(state)
        updated, added, removed = parsed
        return StateUpdate(
            state=updated,
            add_prerequisites=added,
            remove_prerequisites=removed,
        )

    def _parse_mutation(
        self, metadata, state: RelevantState
    ) -> tuple[RelevantState, Tuple[str, ...], Tuple[str, ...]] | str:
        revision = metadata.get("state_revision")
        description = metadata.get("mutation_description")
        if not isinstance(revision, str) or not revision.strip():
            return "state mutation missing a valid state_revision"
        if revision == state.environment.revision:
            return "state mutation did not advance the environment revision"
        if not isinstance(description, str) or not description.strip():
            return "state mutation missing a description"

        available = metadata.get("available_tools", state.environment.available_tools)
        if not isinstance(available, (tuple, list)) or not all(
            isinstance(item, str) and item in self._tools for item in available
        ):
            return "state mutation declared invalid or unpermitted available_tools"
        network = metadata.get("network_available", state.environment.network_available)
        if network is not None and not isinstance(network, bool):
            return "state mutation declared invalid network_available"
        auth = metadata.get("authentication_context", state.authentication_context)
        session = metadata.get("session_context", state.session_context)
        challenge_revision = metadata.get("challenge_revision", state.challenge_revision)
        if not all(isinstance(item, str) for item in (auth, session, challenge_revision)):
            return "state mutation declared invalid context values"
        added = self._string_tuple(metadata.get("satisfied_prerequisites", ()))
        removed = self._string_tuple(metadata.get("invalidated_prerequisites", ()))
        if added is None or removed is None:
            return "state mutation declared malformed prerequisites"
        if set(added) & set(removed):
            return "state mutation both satisfied and invalidated the same prerequisite"

        environment = EnvironmentState(
            revision=revision,
            available_tools=tuple(available),
            network_available=network,
        )
        return (
            RelevantState(
                environment=environment,
                authentication_context=auth,
                session_context=session,
                challenge_revision=challenge_revision,
            ),
            added,
            removed,
        )

    @staticmethod
    def _string_tuple(value) -> Tuple[str, ...] | None:
        if not isinstance(value, (tuple, list)):
            return None
        if not all(isinstance(item, str) and item.strip() for item in value):
            return None
        return tuple(value)

    def _block_mutation(self, action_id: str, reason: str) -> None:
        self._unknown_state_mutation = True
        self._mutation_reason = reason
        self._emit(
            JournalEventKind.RECOVERY_DECISION,
            {"action_id": action_id, "decision": "block", "reason": reason},
        )

    def _cost(self, proposal: ActionProposal) -> int:
        configured = self._tools.get(proposal.tool)
        return max(proposal.cost_hint, configured.cost if configured else 1)

    def _elapsed(self) -> float:
        return max(0.0, self._monotonic() - self._started)

    def _journal_budget(self) -> None:
        self._emit(
            JournalEventKind.BUDGET_UPDATED,
            {
                "iterations": self._usage.iterations,
                "actions": self._usage.total_actions,
                "tool_executions": self._usage.tool_executions,
                "specialist_calls": self._usage.specialist_calls,
                "submissions": self._usage.submissions,
                "total_cost": self._usage.total_cost,
            },
        )

    def _emit(self, kind: JournalEventKind, payload) -> None:
        self._journal.append(JournalEvent(self._run_id, kind, self._clock(), payload))


_FAILURES = {
    ResultClass.INPUT_REJECTION,
    ResultClass.AUTH_FAILURE,
    ResultClass.AUTHZ_FAILURE,
    ResultClass.RATE_LIMIT,
    ResultClass.TIMEOUT,
    ResultClass.NETWORK_FAILURE,
    ResultClass.TOOL_FAILURE,
    ResultClass.ENVIRONMENT_FAILURE,
}
