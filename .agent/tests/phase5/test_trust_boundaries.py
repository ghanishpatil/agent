from __future__ import annotations

import inspect
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from ctf_agent import ChallengeInput, EnvironmentConfig, PermittedTool, SolveStatus, solve
from ctf_agent.adapters import AdapterRegistry
from ctf_agent.context import ChallengeMetadata, build_context
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.kernel import TrustKernel
from ctf_agent.llm_boundary import ScriptedReasoningSource
from ctf_agent.models import (
    Action,
    ControlDecision,
    EnvironmentState,
    ExecutionResult,
    FlagCandidate,
    HypothesisImpact,
    RelevantState,
)
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion, HypothesisSuggestion
from ctf_agent.specialists import CryptoSpecialist


STATE = RelevantState(EnvironmentState("env", ("allowed",)), "guest", "s", "c")


def test_llm_cannot_directly_execute_tools() -> None:
    source = ScriptedReasoningSource(
        action_script=(ActionSuggestion("h", "probe", "allowed", "x"),)
    )
    assert not hasattr(source, "execute")
    assert not hasattr(source.action_script[0], "execute")


def test_specialist_cannot_execute_tools() -> None:
    specialist = CryptoSpecialist()
    assert not hasattr(specialist, "execute")
    source = inspect.getsource(inspect.getmodule(CryptoSpecialist))
    assert "AdapterRegistry.execute" not in source
    assert "subprocess" not in source


def test_llm_cannot_directly_mutate_evidence() -> None:
    suggestion = HypothesisSuggestion("h", "plausible mechanism")
    assert not hasattr(suggestion, "record_evidence")
    assert not hasattr(suggestion, "commit")


def test_specialist_cannot_mutate_evidence() -> None:
    analysis_source = inspect.getsource(inspect.getmodule(CryptoSpecialist))
    assert "EvidenceManager" not in analysis_source
    assert "record_current" not in analysis_source


def test_llm_cannot_verify_a_flag() -> None:
    suggestion = ActionSuggestion(
        "h", "submit", "allowed", "x", candidate_flag="CTF{guess}"
    )
    assert not hasattr(suggestion, "verification_status")
    assert not hasattr(suggestion, "verified")


def test_specialist_cannot_verify_a_flag() -> None:
    assert "VerificationController" not in inspect.getsource(
        inspect.getmodule(CryptoSpecialist)
    )


def test_untrusted_candidate_cannot_become_verified(tmp_path: Path) -> None:
    class FlagLookingTool:
        name = "decode_tool"

        def execute(self, action: Action) -> ExecutionResult:
            return ExecutionResult(
                action.action_id, action.tool, exit_code=0, stdout="DECODE_OK:CTF{untrusted}"
            )

    artifact = tmp_path / "x.bin"
    artifact.write_bytes(b"x")
    result = solve(
        ChallengeInput(
            name="untrusted",
            category="crypto",
            description="xor cipher artifact",
            flag_format="CTF{...}",
        ),
        resources=(),
        environment=EnvironmentConfig(
            permitted_tools=(PermittedTool("decode_tool", FlagLookingTool()),),
            workspace_root=tmp_path,
            journal_path=tmp_path / "j.jsonl",
            run_id="untrusted",
        ),
    )
    assert result.status is not SolveStatus.SOLVED
    assert result.verified_flag is None


def test_regex_match_cannot_verify_candidate() -> None:
    kernel = TrustKernel()
    candidate = FlagCandidate("CTF{looks_right}", "regex")
    decision = kernel.verifier.evaluate(candidate, ())
    assert decision.decision is ControlDecision.CONTINUE


def test_historical_memory_cannot_override_current_evidence() -> None:
    from ctf_agent.classifier import classify_result
    from ctf_agent.models import ExecutionResult, Observation

    kernel = TrustKernel()
    current_execution = ExecutionResult("a1", "tool", exit_code=0, stdout="current")
    current = kernel.evidence.record_current(
        observation=Observation(
            "o1", "a1", datetime(2026, 1, 1, tzinfo=timezone.utc), "current", current_execution
        ),
        classification=classify_result(current_execution),
        impact=HypothesisImpact.SUPPORTS,
        affected_hypotheses=("h",),
    )
    historical = kernel.evidence.record_historical_prior(
        observation=Observation(
            "o2",
            "a2",
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            "history",
            ExecutionResult("a2", "memory"),
        ),
        affected_hypotheses=("h",),
    )
    assert kernel.evidence.resolve_conflict(current=current, historical=historical) is current


def _failure_does_not_disprove(result: ExecutionResult) -> None:
    kernel = TrustKernel()
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h", "mechanism")
    action = Action("a", "probe", result.tool, "target", None, {}, (), STATE)
    pipeline = kernel.process(
        action=action,
        execution=result,
        hypothesis=hypothesis,
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source="target",
    )
    assert pipeline.hypothesis.status.value != "DISPROVEN"


def test_tool_failure_cannot_become_disproof() -> None:
    _failure_does_not_disprove(ExecutionResult("a", "allowed", exit_code=1))


def test_environment_failure_cannot_become_disproof() -> None:
    _failure_does_not_disprove(
        ExecutionResult("a", "allowed", environment_available=False)
    )


def test_duplicate_actions_remain_blocked() -> None:
    kernel = TrustKernel()
    hypothesis = HypothesisBoard().propose_hypothesis("h", "mechanism")
    action = Action("a1", "probe", "allowed", "target", None, {}, (), STATE)
    first = kernel.process(
        action=action,
        execution=ExecutionResult("a1", "allowed", exit_code=0),
        hypothesis=hypothesis,
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source="target",
    )
    duplicate_action = replace(action, action_id="a2")
    duplicate = kernel.process(
        action=duplicate_action,
        execution=ExecutionResult("a2", "allowed", exit_code=0),
        hypothesis=first.hypothesis,
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source="target",
    )
    assert duplicate.decision is ControlDecision.DUPLICATE
    assert duplicate.evidence is None


def test_post_stop_actions_remain_blocked(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, verifier = crypto_package
    result = solve(challenge, resources, environment, constraints)
    assert result.status is SolveStatus.SOLVED
    assert verifier.calls == 1
    assert result.actions[-1].decision == "STOP"


def test_attempt_budgets_cannot_be_exceeded(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, verifier = crypto_package
    result = solve(
        replace(challenge, attempt_limit=0), resources, environment, constraints
    )
    assert result.budget_usage.submissions == 0
    assert result.budget_usage.budget_violations == 0
    assert verifier.calls == 0


def test_invalid_planner_proposal_is_rejected(tmp_path: Path) -> None:
    context = build_context(
        ChallengeMetadata("x", "web"), TrustKernel(), HypothesisBoard()
    )
    board = context.board
    board.propose_hypothesis("h", "mechanism")
    planner = ActionPlanner(AdapterRegistry())
    diagnostics = planner.propose_with_diagnostics(
        context,
        board,
        (ActionSuggestion("h", "probe", "unregistered", "target"),),
        completed_fingerprints=set(),
        state_before=STATE,
    )
    assert diagnostics.proposals == ()


def test_candidate_without_bound_supported_evidence_never_calls_verifier(tmp_path: Path) -> None:
    from datetime import datetime, timezone

    from ctf_agent.autonomy.control import AutonomyController
    from ctf_agent.autonomy.contracts import CandidateVerifierRoute, SolveConstraints
    from ctf_agent.autonomy.reasoning import RoutedReasoningSource
    from ctf_agent.journal import RuntimeJournal
    from ctf_agent.loop import LoopOutcome, ReasoningLoop

    class CountingVerifier:
        name = "flag_verifier"

        def __init__(self):
            self.calls = 0

        def execute(self, action: Action) -> ExecutionResult:
            self.calls += 1
            return ExecutionResult(action.action_id, action.tool, exit_code=0)

    class HostileReasoner:
        def suggest_hypotheses(self, context):
            return (HypothesisSuggestion("h", "unsupported guess"),)

        def suggest_actions(self, context):
            return (
                ActionSuggestion(
                    "h",
                    "submit unsupported guess",
                    "analysis_tool",
                    "artifact",
                    candidate_flag="CTF{unsupported}",
                ),
            )

        def interpret(self, context):
            return ()

    verifier = CountingVerifier()
    registry = AdapterRegistry()
    registry.register(verifier)
    journal = RuntimeJournal(tmp_path / "pre-evidence.jsonl")
    tool = PermittedTool("flag_verifier", verifier, verifier=True)
    controller = AutonomyController(
        SolveConstraints(max_actions=2, max_iterations=2),
        (tool,),
        journal,
        "pre-evidence",
        lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
        lambda: 0.0,
    )
    reasoner = RoutedReasoningSource(
        HostileReasoner(), CandidateVerifierRoute("flag_verifier", "grader")
    )
    loop = ReasoningLoop(
        metadata=ChallengeMetadata("x", "crypto"),
        kernel=TrustKernel(),
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=reasoner,
        journal=journal,
        run_id="pre-evidence",
        clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
        controller=controller,
    )
    result = loop.run(STATE, max_actions=2)
    assert result.outcome is LoopOutcome.BLOCKED_NO_ACTIONS
    assert verifier.calls == 0
    assert controller.usage.submissions == 0
