from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from ctf_agent import SolveStatus, solve
from ctf_agent.adapters import AdapterRegistry
from ctf_agent.autonomy.contracts import PermittedTool, SolveConstraints
from ctf_agent.autonomy.control import AutonomyController
from ctf_agent.context import ChallengeMetadata
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.loop import LoopOutcome, ReasoningLoop
from ctf_agent.models import Action, EnvironmentState, ExecutionResult, RelevantState
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion, HypothesisSuggestion


class IncrementingMonotonic:
    def __init__(self, values):
        self.values = list(values)
        self.last = self.values[-1]

    def __call__(self):
        if self.values:
            self.last = self.values.pop(0)
        return self.last


def test_tool_execution_budget_denies_before_second_execution(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, verifier = crypto_package
    constrained = replace(constraints, max_tool_executions=1)
    result = solve(challenge, resources, environment, constrained)
    assert result.status is SolveStatus.EXHAUSTED
    assert result.budget_usage.tool_executions == 1
    assert len(result.actions) == 1
    assert verifier.calls == 0
    assert result.budget_usage.budget_violations == 0


def test_attempt_limit_tightens_submission_budget(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, verifier = crypto_package
    challenge = replace(challenge, attempt_limit=0)
    result = solve(challenge, resources, environment, constraints)
    assert result.status is SolveStatus.EXHAUSTED
    assert result.verified_flag is None
    assert result.budget_usage.submissions == 0
    assert verifier.calls == 0


def test_specialist_call_budget_is_enforced_before_actions(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, verifier = crypto_package
    result = solve(
        challenge,
        resources,
        environment,
        replace(constraints, max_specialist_calls=0),
    )
    assert result.status is SolveStatus.EXHAUSTED
    assert result.actions == ()
    assert result.budget_usage.specialist_calls == 0
    assert verifier.calls == 0


def test_wall_clock_timeout_is_terminal_without_execution(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, verifier = crypto_package
    monotonic = IncrementingMonotonic([0.0, 0.0, 50.0, 50.0])
    environment = replace(environment, monotonic=monotonic)
    result = solve(
        challenge,
        resources,
        environment,
        replace(constraints, timeout_seconds=1.0),
    )
    assert result.status is SolveStatus.TIMEOUT
    assert result.actions == ()
    assert verifier.calls == 0


class StateAdapter:
    name = "state_tool"

    def execute(self, action: Action) -> ExecutionResult:
        if action.objective == "unlock environment":
            return ExecutionResult(
                action.action_id,
                action.tool,
                exit_code=0,
                state_changed=True,
                metadata={
                    "state_revision": "rev-2",
                    "mutation_description": "authenticated session established",
                    "authentication_context": "authenticated",
                    "satisfied_prerequisites": ("unlocked",),
                },
            )
        return ExecutionResult(action.action_id, action.tool, exit_code=0, stdout="probe complete")


class StateReasoner:
    def suggest_hypotheses(self, context):
        return (
            HypothesisSuggestion("h-unlock", "environment can be unlocked"),
            HypothesisSuggestion("h-probe", "authenticated probe is useful"),
        )

    def suggest_actions(self, context):
        return (
            ActionSuggestion("h-unlock", "unlock environment", "state_tool", "local"),
            ActionSuggestion(
                "h-probe",
                "authenticated probe",
                "state_tool",
                "local",
                prerequisites=("unlocked",),
                expected_observation="authenticated response confirms access",
            ),
        )

    def interpret(self, context):
        return ()


def _controlled_loop(tmp_path: Path, adapter, reasoner):
    registry = AdapterRegistry()
    registry.register(adapter)
    journal = RuntimeJournal(tmp_path / "state.jsonl")
    constraints = SolveConstraints(max_actions=2, max_iterations=3)
    tool = PermittedTool(adapter.name, adapter)
    controller = AutonomyController(
        constraints,
        (tool,),
        journal,
        "state-run",
        lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
        lambda: 0.0,
    )
    loop = ReasoningLoop(
        metadata=ChallengeMetadata("state", "web"),
        kernel=TrustKernel(),
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=reasoner,
        journal=journal,
        run_id="state-run",
        clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
        board=HypothesisBoard(),
        controller=controller,
    )
    state = RelevantState(EnvironmentState("rev-1", (adapter.name,)), "guest", "s1", "c1")
    return loop, state, controller


def test_state_change_satisfies_prerequisite_and_changes_dedup_identity(tmp_path: Path) -> None:
    loop, state, _controller = _controlled_loop(tmp_path, StateAdapter(), StateReasoner())
    result = loop.run(state, max_actions=2)
    assert result.outcome is LoopOutcome.BUDGET_EXHAUSTED
    assert len(result.pipeline_results) == 2
    assert result.pipeline_results[1].action.objective == "authenticated probe"
    assert result.pipeline_results[1].action.state_before.environment.revision == "rev-2"
    assert "unlocked" in loop.satisfied_prerequisites


class UnknownMutationAdapter:
    name = "state_tool"

    def __init__(self):
        self.calls = 0

    def execute(self, action: Action) -> ExecutionResult:
        self.calls += 1
        return ExecutionResult(action.action_id, action.tool, exit_code=0, state_changed=True)


def test_unknown_state_mutation_blocks_further_execution(tmp_path: Path) -> None:
    adapter = UnknownMutationAdapter()
    loop, state, controller = _controlled_loop(tmp_path, adapter, StateReasoner())
    result = loop.run(state, max_actions=5)
    assert result.outcome is LoopOutcome.BLOCKED_PREREQUISITES
    assert adapter.calls == 1
    assert "state mutation" in controller.terminal_reason


class MalformedMutationAdapter:
    name = "state_tool"

    def execute(self, action: Action) -> ExecutionResult:
        return ExecutionResult(
            action.action_id,
            action.tool,
            exit_code=0,
            state_changed=True,
            metadata={
                "state_revision": "rev-2",
                "mutation_description": "claims an unpermitted tool",
                "available_tools": ("not-permitted",),
                "satisfied_prerequisites": ("unlocked",),
            },
        )


def test_malformed_state_mutation_fails_closed(tmp_path: Path) -> None:
    adapter = MalformedMutationAdapter()
    loop, state, controller = _controlled_loop(tmp_path, adapter, StateReasoner())
    result = loop.run(state, max_actions=5)
    assert result.outcome is LoopOutcome.BLOCKED_PREREQUISITES
    assert "unpermitted" in controller.terminal_reason
    assert "unlocked" not in loop.satisfied_prerequisites


class MutableTimer:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


class LateVerifier:
    name = "flag_verifier"

    def __init__(self, expected: str, timer: MutableTimer) -> None:
        self.expected = expected
        self.timer = timer
        self.calls = 0

    def execute(self, action: Action) -> ExecutionResult:
        self.calls += 1
        self.timer.value = 2.0  # completes after the hard one-second deadline
        candidate = action.input_data.get("flag", "")
        return ExecutionResult(
            action.action_id,
            action.tool,
            exit_code=0,
            metadata={"submitted_candidate": candidate, "verifier_accepted": True},
        )


def test_late_verifier_response_cannot_produce_solved(crypto_package) -> None:
    challenge, resources, environment, constraints, flag, _old_verifier = crypto_package
    timer = MutableTimer()
    late = LateVerifier(flag, timer)
    tools = tuple(
        replace(tool, adapter=late)
        if tool.name == "flag_verifier"
        else tool
        for tool in environment.permitted_tools
    )
    environment = replace(environment, permitted_tools=tools, monotonic=timer)
    result = solve(
        challenge,
        resources,
        environment,
        replace(constraints, timeout_seconds=1.0),
    )
    assert late.calls == 1
    assert result.status is SolveStatus.TIMEOUT
    assert result.verified_flag is None
    assert not any(action.decision == "STOP" for action in result.actions)
