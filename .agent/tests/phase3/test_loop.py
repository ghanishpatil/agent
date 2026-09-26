from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from ctf_agent.adapters import AdapterRegistry, FileAdapter
from ctf_agent.context import ChallengeMetadata
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.llm_boundary import ScriptedReasoningSource
from ctf_agent.loop import LoopOutcome, ReasoningLoop
from ctf_agent.models import (
    EnvironmentState,
    RelevantState,
    TestSpecification,
    VerificationPolicy,
)
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion


FIXED_CLOCK = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("file_read",)), "guest", "s1", "c1")


def metadata() -> ChallengeMetadata:
    return ChallengeMetadata(name="sample", category="forensics")


def make_registry(tmp_path: Path) -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    return registry


def make_loop(
    tmp_path: Path,
    *,
    action_script: Tuple[ActionSuggestion, ...],
    board: HypothesisBoard | None = None,
    kernel: TrustKernel | None = None,
    trusted_sources_for_disproof: dict | None = None,
) -> ReasoningLoop:
    registry = make_registry(tmp_path)
    journal_path = tmp_path / "runtime" / "journal.jsonl"
    return ReasoningLoop(
        metadata=metadata(),
        kernel=kernel or TrustKernel(),
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=ScriptedReasoningSource(action_script=action_script),
        journal=RuntimeJournal(journal_path),
        run_id="run-1",
        clock=lambda: FIXED_CLOCK,
        board=board or HypothesisBoard(),
        trusted_sources_for_disproof=trusted_sources_for_disproof or {},
    )


def test_loop_blocks_when_no_open_hypotheses(tmp_path: Path) -> None:
    loop = make_loop(tmp_path, action_script=())
    result = loop.run(STATE, max_actions=5)
    assert result.outcome is LoopOutcome.BLOCKED_NO_ACTIONS
    assert result.actions_taken == 0


def test_loop_reports_blocked_prerequisites_when_only_gated_actions_exist(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag needs an unlocked service")
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="probe locked service",
        tool="file_read",
        target="service",
        prerequisites=("service-started",),
    )
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    result = loop.run(STATE, max_actions=5)
    assert result.outcome is LoopOutcome.BLOCKED_PREREQUISITES
    assert result.actions_taken == 0


def test_loop_executes_actions_and_records_evidence_across_iterations(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("nothing interesting here", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in note.txt")
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="read note",
        tool="file_read",
        target="note.txt",
        input_data="note.txt",
        expected_observation="contains flag",
    )
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    result = loop.run(STATE, max_actions=1)

    assert result.actions_taken == 1
    assert len(result.pipeline_results) == 1
    pipeline_result = result.pipeline_results[0]
    assert pipeline_result.evidence is not None
    # State persisted onto the loop's own board, not reset between iterations.
    assert loop.board.get("h1").hypothesis_id == "h1"


def test_loop_does_not_repeat_a_duplicate_action_in_the_same_state(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("nothing interesting here", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in note.txt")
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="read note",
        tool="file_read",
        target="note.txt",
        input_data="note.txt",
    )
    # Same suggestion every time the scripted source is asked; state never changes, so after the
    # first action is fingerprinted, the planner must refuse to propose it again -> no proposals.
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    result = loop.run(STATE, max_actions=5)

    assert result.actions_taken == 1
    assert result.outcome is LoopOutcome.BLOCKED_NO_ACTIONS


def test_loop_deprioritizes_a_repeatedly_unresolving_branch_without_disproving_it(
    tmp_path: Path,
) -> None:
    # allowed_root itself does not exist -> every read is an ENVIRONMENT_FAILURE -> UNRESOLVES.
    missing_root = tmp_path / "does-not-exist"
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", missing_root))
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in a file under the missing mount")

    suggestions = tuple(
        ActionSuggestion(
            hypothesis_id="h1",
            objective=f"probe attempt {i}",
            tool="file_read",
            target=f"candidate-{i}.txt",
            input_data=f"candidate-{i}.txt",
        )
        for i in range(4)
    )

    class RotatingSource:
        def __init__(self, script: Tuple[ActionSuggestion, ...]) -> None:
            self._script = list(script)

        def suggest_hypotheses(self, context):
            return ()

        def suggest_actions(self, context):
            # Each call offers only the next not-yet-tried suggestion, since the target changes
            # every time (so dedup never blocks it), but the hypothesis keeps failing the same way.
            return (self._script.pop(0),) if self._script else ()

        def interpret(self, context):
            return ()

    journal_path = tmp_path / "runtime" / "journal.jsonl"
    loop = ReasoningLoop(
        metadata=metadata(),
        kernel=TrustKernel(),
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=RotatingSource(suggestions),
        journal=RuntimeJournal(journal_path),
        run_id="run-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
    )
    result = loop.run(STATE, max_actions=4)

    # The branch must be deprioritized (closed as low value), never marked DISPROVEN: only real
    # discriminating evidence recorded via a registered TestSpecification can disprove a
    # hypothesis, and none was registered here.
    from ctf_agent.models import HypothesisStatus

    assert loop.board.get("h1").status is not HypothesisStatus.DISPROVEN
    assert loop.board.meta("h1").priority == 0
    # The branch closes (priority -> 0) once 3 unresolved-evidence entries accumulate, so the 4th
    # scripted suggestion is never even proposed: the loop stops itself at 3 actions, not 4.
    assert result.actions_taken == 3
    assert result.outcome is LoopOutcome.BLOCKED_NO_ACTIONS


def test_loop_terminates_verified_when_kernel_confirms_flag(tmp_path: Path) -> None:
    flag_dir = tmp_path
    (flag_dir / "derive.txt").write_text("candidate flag: CTF{real}", encoding="utf-8")
    (flag_dir / "submit.txt").write_text("accepted CTF{real}", encoding="utf-8")

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("challenge_service",))
    )
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "candidate is the intended flag")

    derive_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="derive candidate flag",
        tool="file_read",
        target="derive.txt",
        input_data="derive.txt",
    )
    submit_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="submit candidate flag",
        tool="challenge_service",
        target="submit.txt",
        input_data="submit.txt",
        candidate_flag="CTF{real}",
    )

    class TwoStepSource:
        def __init__(self) -> None:
            self._step = 0

        def suggest_hypotheses(self, context):
            return ()

        def suggest_actions(self, context):
            self._step += 1
            if self._step == 1:
                return (derive_suggestion,)
            return (submit_suggestion,)

        def interpret(self, context):
            return ()

    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", flag_dir))
    registry.register(FileAdapter("challenge_service", flag_dir))

    journal_path = tmp_path / "runtime" / "journal.jsonl"

    # Uses the real, unmodified ReasoningLoop: the "submit" ActionSuggestion carries
    # candidate_flag="CTF{real}", which the loop forwards to kernel.process(candidate=...) only
    # because prior evidence for this hypothesis (from the "derive" step) already contains that
    # exact value. The kernel's VerificationController is what actually decides VERIFIED -- the
    # suggestion only proposes a value to try.
    loop = ReasoningLoop(
        metadata=metadata(),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=TwoStepSource(),
        journal=RuntimeJournal(journal_path),
        run_id="run-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
    )
    result = loop.run(STATE, max_actions=5)

    assert result.outcome is LoopOutcome.VERIFIED
    assert result.actions_taken == 2
    assert result.actions_taken == 2


def test_loop_exhausts_budget_without_verifying(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("just some text", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in note.txt")

    class InfiniteVariantSource:
        def __init__(self) -> None:
            self._counter = 0

        def suggest_hypotheses(self, context):
            return ()

        def suggest_actions(self, context):
            self._counter += 1
            return (
                ActionSuggestion(
                    hypothesis_id="h1",
                    objective=f"probe variant {self._counter}",
                    tool="file_read",
                    target="note.txt",
                    input_data="note.txt",
                    relevant_parameters={"variant": self._counter},
                ),
            )

        def interpret(self, context):
            return ()

    loop = make_loop(tmp_path, action_script=(), board=board)
    loop.reasoning_source = InfiniteVariantSource()
    result = loop.run(STATE, max_actions=3)

    assert result.outcome is LoopOutcome.BUDGET_EXHAUSTED
    assert result.actions_taken == 3


def test_loop_journal_records_every_stage_of_the_first_action(tmp_path: Path) -> None:
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in note.txt")
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="read note",
        tool="file_read",
        target="note.txt",
        input_data="note.txt",
    )
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    loop.run(STATE, max_actions=1)

    events = loop.journal.read_all()
    kinds = [event["kind"] for event in events]
    assert "action_proposed" in kinds
    assert "action_executed" in kinds
    assert "result_classified" in kinds
    assert "evidence_recorded" in kinds
    assert "hypothesis_transitioned" in kinds
    assert "control_decision" in kinds


def test_loop_ignores_candidate_flag_with_no_prior_evidence_for_the_hypothesis(
    tmp_path: Path,
) -> None:
    """A submit-style suggestion offered as the very first action for a hypothesis has no prior
    evidence bound to it yet -- the loop must run it as a normal probe (no crash, no candidate
    attached) rather than forwarding an empty evidence set to kernel.process()."""
    (tmp_path / "submit.txt").write_text("accepted CTF{real}", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "candidate is the intended flag")
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="submit candidate flag",
        tool="file_read",
        target="submit.txt",
        input_data="submit.txt",
        candidate_flag="CTF{real}",
    )
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    result = loop.run(STATE, max_actions=1)

    assert result.actions_taken == 1
    assert result.outcome is not LoopOutcome.VERIFIED
    assert result.pipeline_results[0].verification is None


def test_loop_ignores_a_candidate_flag_that_does_not_match_prior_evidence(tmp_path: Path) -> None:
    """If the suggested candidate_flag isn't actually present in the prior evidence for this
    hypothesis, the loop must not forward it to kernel.process() at all -- it degrades to a normal
    probe rather than raising ValueError out of FlagAttemptRegistry.check_and_record."""
    (tmp_path / "derive.txt").write_text("nothing flag-shaped here", encoding="utf-8")
    (tmp_path / "submit.txt").write_text("some other unrelated text", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "candidate is the intended flag")

    derive_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="derive",
        tool="file_read",
        target="derive.txt",
        input_data="derive.txt",
    )
    wrong_guess_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="submit a guess unrelated to any evidence",
        tool="file_read",
        target="submit.txt",
        input_data="submit.txt",
        candidate_flag="CTF{totally_made_up}",
    )

    class TwoStepSource:
        def __init__(self) -> None:
            self._step = 0

        def suggest_hypotheses(self, context):
            return ()

        def suggest_actions(self, context):
            self._step += 1
            return (derive_suggestion,) if self._step == 1 else (wrong_guess_suggestion,)

        def interpret(self, context):
            return ()

    loop = make_loop(tmp_path, action_script=(), board=board)
    loop.reasoning_source = TwoStepSource()
    result = loop.run(STATE, max_actions=2)

    assert result.actions_taken == 2
    assert result.outcome is not LoopOutcome.VERIFIED
    assert result.pipeline_results[-1].verification is None
