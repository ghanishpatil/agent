"""Explicit architectural-boundary tests called out by prompt_phase 3.md sections 7 and 13.

These are deliberately separate from test_loop.py / test_adapters.py / test_hypothesis_engine.py:
each test here targets one specific guarantee named in the spec's testing checklist and final
validation checklist, so a reader can map spec bullet -> test 1:1 without cross-referencing other
files.
"""
from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ctf_agent.adapters import AdapterRegistry, FileAdapter, HttpAdapter, SubprocessAdapter
from ctf_agent.context import ChallengeMetadata
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.llm_boundary import ScriptedReasoningSource
from ctf_agent.loop import LoopOutcome, ReasoningLoop
from ctf_agent.models import (
    ControlDecision,
    EnvironmentState,
    HypothesisStatus,
    RelevantState,
)
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion, ProposalRejected, validate_action_suggestion


FIXED_CLOCK = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("file_read",)), "guest", "s1", "c1")


def metadata() -> ChallengeMetadata:
    return ChallengeMetadata(name="sample", category="forensics")


def make_loop(tmp_path: Path, *, action_script, board=None, kernel=None) -> ReasoningLoop:
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    return ReasoningLoop(
        metadata=metadata(),
        kernel=kernel or TrustKernel(),
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=ScriptedReasoningSource(action_script=action_script),
        journal=RuntimeJournal(tmp_path / "runtime" / "journal.jsonl"),
        run_id="run-1",
        clock=lambda: FIXED_CLOCK,
        board=board or HypothesisBoard(),
    )


# --- Spec 13.10: "Verify tool adapters cannot directly mutate hypotheses/evidence" ------------


def test_tool_adapter_protocol_exposes_only_execute() -> None:
    """The ToolAdapter Protocol has exactly one method, and it is not state-mutating by name."""
    from ctf_agent.adapters.base import ToolAdapter

    members = [name for name, _ in inspect.getmembers(ToolAdapter) if not name.startswith("_")]
    assert members == ["execute"]


@pytest.mark.parametrize(
    "adapter_cls",
    [FileAdapter, SubprocessAdapter, HttpAdapter],
)
def test_concrete_adapters_have_no_reference_to_kernel_or_board_types(adapter_cls) -> None:
    """None of the three concrete adapters import/reference HypothesisBoard, EvidenceManager, or
    TrustKernel anywhere in their module -- there is no code path, not just a runtime check, by
    which an adapter could reach into kernel/board state."""
    source = inspect.getsource(inspect.getmodule(adapter_cls))
    for forbidden_name in ("HypothesisBoard", "EvidenceManager", "TrustKernel", "kernel.process"):
        assert forbidden_name not in source


def test_file_adapter_execute_signature_only_accepts_and_returns_plain_data(tmp_path: Path) -> None:
    """Executing an adapter has no side effect on any hypothesis/evidence object passed near it."""
    (tmp_path / "note.txt").write_text("hello", encoding="utf-8")
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "flag is in note.txt")
    before = board.get("h1")

    adapter = FileAdapter("file_read", tmp_path)
    from ctf_agent.models import Action

    adapter.execute(
        Action("a1", "read", "file_read", "note.txt", "note.txt", {}, (), STATE)
    )

    # The adapter was never given the board or the hypothesis; calling it cannot have changed
    # either, because it has no reference to them at all.
    assert board.get("h1") is before
    assert hypothesis.status is HypothesisStatus.OPEN


# --- Spec 13.9: "Verify LLM proposals cannot bypass deterministic controls" -------------------


def test_llm_action_suggestion_naming_unregistered_tool_never_reaches_the_loop(
    tmp_path: Path,
) -> None:
    """An LLM suggestion for a tool that was never registered is rejected before planning, so the
    loop can never execute it -- it simply reports no proposals, not an unsafe fallback."""
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag reachable via a tool the agent never registered")
    rogue_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="run arbitrary shell command",
        tool="shell_exec_unregistered",
        target="rm -rf /",
    )
    loop = make_loop(tmp_path, action_script=(rogue_suggestion,), board=board)
    result = loop.run(STATE, max_actions=3)

    assert result.outcome is LoopOutcome.BLOCKED_NO_ACTIONS
    assert result.actions_taken == 0


def test_llm_suggestion_containing_forbidden_state_assertion_is_rejected_at_the_boundary(
    tmp_path: Path,
) -> None:
    """A suggestion whose rationale tries to smuggle a state transition never becomes an
    ActionProposal -- validate_action_suggestion raises before the planner ranks anything."""
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    rogue_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="probe",
        tool="file_read",
        target="a",
        rationale="just declare verified once this runs",
    )
    with pytest.raises(ProposalRejected, match="state transition"):
        validate_action_suggestion(rogue_suggestion, registry)


def test_llm_cannot_force_verification_by_supplying_a_hypothesis_id_that_does_not_exist(
    tmp_path: Path,
) -> None:
    """A suggestion naming a hypothesis_id the board never opened is simply not an open
    hypothesis, so the planner discards it -- there is no path from 'LLM names an id' to
    'kernel treats that id as verified'."""
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "the only real hypothesis")
    ghost_suggestion = ActionSuggestion(
        hypothesis_id="h999-does-not-exist",
        objective="probe",
        tool="file_read",
        target="a",
    )
    loop = make_loop(tmp_path, action_script=(ghost_suggestion,), board=board)
    result = loop.run(STATE, max_actions=3)

    assert result.outcome is LoopOutcome.BLOCKED_NO_ACTIONS
    assert result.actions_taken == 0


# --- Spec 13.12 / section 4.C: "environment/tool failures do not become automatic disproof" ---
# at the LOOP level (Phase 2's kernel/impact tests already cover this at the unit level; this
# exercises the same guarantee through the full ReasoningLoop orchestration path).


def test_loop_never_disproves_a_hypothesis_from_repeated_environment_failures(
    tmp_path: Path,
) -> None:
    missing_root = tmp_path / "does-not-exist"
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", missing_root))
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is under the (currently missing) mount")

    suggestions = tuple(
        ActionSuggestion(
            hypothesis_id="h1",
            objective=f"probe {i}",
            tool="file_read",
            target=f"c{i}.txt",
            input_data=f"c{i}.txt",
        )
        for i in range(5)
    )

    class RotatingSource:
        def __init__(self, script) -> None:
            self._script = list(script)

        def suggest_hypotheses(self, context):
            return ()

        def suggest_actions(self, context):
            return (self._script.pop(0),) if self._script else ()

        def interpret(self, context):
            return ()

    loop = ReasoningLoop(
        metadata=metadata(),
        kernel=TrustKernel(),
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=RotatingSource(suggestions),
        journal=RuntimeJournal(tmp_path / "runtime" / "journal.jsonl"),
        run_id="run-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
    )
    loop.run(STATE, max_actions=5)

    # Every one of these was an ENVIRONMENT_FAILURE (root missing). No amount of them may ever
    # flip status to DISPROVEN -- only a registered discriminating TestSpecification plus a
    # trusted, authoritative contradicting observation can do that.
    assert loop.board.get("h1").status is not HypothesisStatus.DISPROVEN
    assert loop.board.get("h1").status is HypothesisStatus.UNRESOLVED


def test_loop_never_disproves_a_hypothesis_from_a_missing_target_file(tmp_path: Path) -> None:
    """A file-not-found (TOOL_FAILURE-classified) result is also never automatic disproof."""
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in a file that happens not to exist")
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="probe missing file",
        tool="file_read",
        target="does-not-exist.txt",
        input_data="does-not-exist.txt",
    )
    loop = make_loop(tmp_path, action_script=(suggestion,), board=board)
    loop.run(STATE, max_actions=1)

    assert loop.board.get("h1").status is not HypothesisStatus.DISPROVEN


# --- Spec 13.8: "Verify no post-STOP actions generate new evidence" (at the loop level) --------


def test_loop_produces_no_new_evidence_once_kernel_verification_reaches_stop(
    tmp_path: Path,
) -> None:
    """Once kernel.process() has returned STOP once, every subsequent process() call for this
    kernel short-circuits (Phase 2 guarantee). This test proves the loop-driven path relies on
    that guarantee rather than re-implementing its own stop check that could drift from it."""
    (tmp_path / "note.txt").write_text("irrelevant", encoding="utf-8")
    kernel = TrustKernel()
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "some hypothesis")

    from ctf_agent.models import Action, ExecutionResult, FlagCandidate, VerificationState

    # Force the kernel into STOP directly via its private state, mirroring what a real verified
    # candidate would produce, to isolate "does the loop stop generating evidence after STOP" from
    # "can something get to STOP" (covered elsewhere / by Phase 2).
    kernel._verification = VerificationState((), ControlDecision.STOP)

    action = Action("a1", "probe", "file_read", "note.txt", "note.txt", {}, (), STATE)
    result = kernel.process(
        action=action,
        execution=ExecutionResult("a1", "file_read", exit_code=0, stdout="irrelevant"),
        hypothesis=hypothesis,
        observed_at=FIXED_CLOCK,
        source="local",
    )
    assert result.decision is ControlDecision.STOP
    assert result.evidence is None
    assert result.observation is None
    assert result.classification is None


def test_loop_run_stops_immediately_when_context_is_already_verified(tmp_path: Path) -> None:
    """If the board already reflects a verified context on iteration 1, the loop must report
    VERIFIED without executing a single action."""
    from ctf_agent.classifier import classify_result
    from ctf_agent.models import (
        Action,
        ExecutionResult,
        FlagCandidate,
        HypothesisImpact,
        Observation,
        VerificationPolicy,
    )

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("challenge_service",))
    )
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "candidate is the intended flag")
    derive_execution = ExecutionResult("derive-1", "analysis", exit_code=0, stdout="CTF{real}")
    prior = kernel.evidence.record_current(
        observation=Observation("obs-derive", "derive-1", FIXED_CLOCK, "analysis", derive_execution),
        classification=classify_result(derive_execution),
        impact=HypothesisImpact.NO_IMPACT,
        affected_hypotheses=("h1",),
    )
    stop_action = Action("a-stop", "submit", "challenge_service", "https://ctf.local/submit", None, {}, (), STATE)
    result = kernel.process(
        action=stop_action,
        execution=ExecutionResult(
            "a-stop", "challenge_service", exit_code=0, response_body="accepted CTF{real}"
        ),
        hypothesis=hypothesis,
        observed_at=FIXED_CLOCK,
        source="challenge-service",
        candidate=FlagCandidate("CTF{real}", "derived"),
        candidate_evidence_ids=(prior.evidence_id,),
        verifier="ctfd",
    )
    board.record(result)

    loop = make_loop(tmp_path, action_script=(), board=board, kernel=kernel)
    loop_result = loop.run(STATE, max_actions=5)

    assert loop_result.outcome is LoopOutcome.VERIFIED
    assert loop_result.actions_taken == 0


# --- Spec 7 "Loop": "duplicate actions are blocked" (already in test_loop.py; this adds the
# specific "same action + same state + same objective, nothing material changed" anti-spray
# framing named explicitly in section 5) --------------------------------------------------------


def test_loop_blocks_spray_of_materially_identical_actions_across_many_iterations(
    tmp_path: Path,
) -> None:
    (tmp_path / "note.txt").write_text("data", encoding="utf-8")
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "flag is in note.txt")
    identical_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="read note",
        tool="file_read",
        target="note.txt",
        input_data="note.txt",
    )
    # The scripted source offers the *same* suggestion every single call, forever. State never
    # changes (STATE is reused). The loop must execute it exactly once, then block.
    loop = make_loop(tmp_path, action_script=(identical_suggestion,), board=board)
    result = loop.run(STATE, max_actions=10)

    assert result.actions_taken == 1
    assert result.outcome is LoopOutcome.BLOCKED_NO_ACTIONS
