from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ctf_agent.adapters import AdapterRegistry, FileAdapter
from ctf_agent.context import ChallengeMetadata
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.loop import LoopOutcome, ReasoningLoop
from ctf_agent.metrics import evaluate_runs, evaluate_single_run
from ctf_agent.models import EnvironmentState, RelevantState, VerificationPolicy
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion


FIXED_CLOCK = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("file_read",)), "guest", "s1", "c1")


def metadata() -> ChallengeMetadata:
    return ChallengeMetadata(name="sample", category="forensics")


def make_loop(tmp_path: Path, *, action_script, board=None) -> ReasoningLoop:
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    return ReasoningLoop(
        metadata=metadata(),
        kernel=TrustKernel(),
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=_ScriptedSource(action_script),
        journal=RuntimeJournal(tmp_path / "runtime" / "journal.jsonl"),
        run_id="run-1",
        clock=lambda: FIXED_CLOCK,
        board=board or HypothesisBoard(),
    )


class _ScriptedSource:
    def __init__(self, script) -> None:
        self._script = script

    def suggest_hypotheses(self, context):
        return ()

    def suggest_actions(self, context):
        return self._script

    def interpret(self, context):
        return ()


def test_single_run_metrics_on_blocked_no_actions(tmp_path: Path) -> None:
    loop = make_loop(tmp_path, action_script=())
    result = loop.run(STATE, max_actions=5)
    metrics = evaluate_single_run(result)

    assert metrics.outcome is LoopOutcome.BLOCKED_NO_ACTIONS
    assert metrics.actions_taken == 0
    assert metrics.verified is False
    assert metrics.actions_to_solution is None
    assert metrics.duplicate_action_rate == 0.0
    assert metrics.unnecessary_action_rate == 0.0
    assert metrics.verification_latency_actions is None
    assert metrics.state_is_consistent


def test_single_run_metrics_counts_no_impact_probes_as_unnecessary(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("nothing here", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in a.txt")
    suggestion = ActionSuggestion(
        hypothesis_id="h1", objective="probe", tool="file_read", target="a.txt", input_data="a.txt"
    )
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    result = loop.run(STATE, max_actions=1)
    metrics = evaluate_single_run(result)

    assert metrics.actions_taken == 1
    assert metrics.unnecessary_action_count == 1
    assert metrics.unnecessary_action_rate == 1.0
    assert metrics.duplicate_action_count == 0


def test_single_run_metrics_counts_duplicate_actions(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("data", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in a.txt")
    suggestion = ActionSuggestion(
        hypothesis_id="h1", objective="probe", tool="file_read", target="a.txt", input_data="a.txt"
    )
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    result = loop.run(STATE, max_actions=10)
    metrics = evaluate_single_run(result)

    # Only the first attempt executes; the loop blocks further proposals once it dedups, so no
    # DUPLICATE-decision pipeline result is ever produced in this scenario. This documents that
    # the planner's own dedup, not a kernel DUPLICATE decision, is what stops the spray here.
    assert metrics.actions_taken == 1
    assert metrics.duplicate_action_count == 0


def test_single_run_metrics_on_verified_run_reports_actions_to_solution(tmp_path: Path) -> None:
    (tmp_path / "derive.txt").write_text("candidate flag: CTF{real}", encoding="utf-8")
    (tmp_path / "submit.txt").write_text("accepted CTF{real}", encoding="utf-8")

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("challenge_service",))
    )
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "candidate is the intended flag")

    derive_suggestion = ActionSuggestion(
        hypothesis_id="h1", objective="derive", tool="file_read", target="derive.txt", input_data="derive.txt"
    )
    submit_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="submit",
        tool="challenge_service",
        target="submit.txt",
        input_data="submit.txt",
        candidate_flag="CTF{real}",
    )

    class TwoStep:
        def __init__(self):
            self.step = 0

        def suggest_hypotheses(self, context):
            return ()

        def suggest_actions(self, context):
            self.step += 1
            return (derive_suggestion,) if self.step == 1 else (submit_suggestion,)

        def interpret(self, context):
            return ()

    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    registry.register(FileAdapter("challenge_service", tmp_path))

    loop = ReasoningLoop(
        metadata=metadata(),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=TwoStep(),
        journal=RuntimeJournal(tmp_path / "runtime" / "journal.jsonl"),
        run_id="run-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
    )
    result = loop.run(STATE, max_actions=5)
    metrics = evaluate_single_run(result)

    assert metrics.verified is True
    assert metrics.actions_to_solution == 2
    assert metrics.verification_latency_actions == 1
    assert metrics.state_is_consistent


def test_aggregate_metrics_across_multiple_runs_without_ground_truth(tmp_path: Path) -> None:
    loop_a = make_loop(tmp_path / "a", action_script=())
    result_a = loop_a.run(STATE, max_actions=1)

    board_b = HypothesisBoard()
    board_b.propose_hypothesis("h1", "flag is in b.txt")
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "b.txt").write_text("data", encoding="utf-8")
    suggestion = ActionSuggestion(
        hypothesis_id="h1", objective="probe", tool="file_read", target="b.txt", input_data="b.txt"
    )
    loop_b = make_loop(tmp_path / "b", action_script=(suggestion,), board=board_b)
    result_b = loop_b.run(STATE, max_actions=1)

    aggregate = evaluate_runs([result_a, result_b])

    assert aggregate.run_count == 2
    assert aggregate.successful_termination_rate == 0.0
    assert aggregate.false_verification_rate == 0.0
    assert aggregate.false_disproof_rate == 0.0
    assert aggregate.average_actions_to_solution is None


def test_aggregate_metrics_reports_zero_run_case() -> None:
    aggregate = evaluate_runs([])
    assert aggregate.run_count == 0
    assert aggregate.average_actions_to_solution is None
