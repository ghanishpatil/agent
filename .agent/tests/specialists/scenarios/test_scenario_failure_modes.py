"""End-to-end specialist scenarios under failure conditions (phase4.md section 17).

These deliberately produce tool failure, ambiguous evidence, and duplicate-action attempts, and
assert the system behaves correctly: failures NEVER become disproof, ambiguity stays UNRESOLVED,
duplicates are blocked, and the loop reaches a safe blocked state (never an "impossible" claim).
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from ctf_agent.adapters import AdapterRegistry, SubprocessAdapter
from ctf_agent.adapters.subprocess_adapter import SubprocessCommand
from ctf_agent.context import ChallengeMetadata
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.loop import LoopOutcome, ReasoningLoop
from ctf_agent.models import (
    EnvironmentState,
    HypothesisStatus,
    RelevantState,
    TestSpecification,
    VerificationPolicy,
)
from ctf_agent.planner import ActionPlanner
from ctf_agent.specialists import SpecialistRegistry, SpecialistReasoningSource


FIXED_CLOCK = datetime(2026, 9, 24, tzinfo=timezone.utc)


def _loop_with_tool(tmp_path: Path, tool_source: str, *, trusted=None):
    handout = tmp_path / "handout.bin"
    handout.write_bytes(b"\x01\x02\x03some bytes")
    tool_path = tmp_path / "tool.py"
    tool_path.write_text(tool_source, encoding="utf-8")
    arg = str(handout)
    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("decode_tool",)),
        trusted_sources={"decode_tool": (arg,)},
    )
    registry = AdapterRegistry()
    registry.register(
        SubprocessAdapter("decode_tool", SubprocessCommand(sys.executable, (str(tool_path),)))
    )
    brain = SpecialistReasoningSource(
        SpecialistRegistry.default(), available_tools=("decode_tool",)
    )
    loop = ReasoningLoop(
        metadata=ChallengeMetadata(
            name="cipher",
            category="crypto",
            description="an encoded cipher artifact; possibly base64 or single-byte xor key",
            files=(arg,),
            flag_format="CTF{...}",
        ),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=brain,
        journal=RuntimeJournal(tmp_path / "runtime" / "fail.jsonl"),
        run_id="spec-fail-1",
        clock=lambda: FIXED_CLOCK,
        board=HypothesisBoard(),
        trusted_sources_for_disproof=trusted or {},
    )
    return loop, loop.board


def test_tool_failure_never_becomes_disproof_end_to_end(tmp_path: Path) -> None:
    # The only tool always crashes (nonzero exit -> TOOL_FAILURE).
    loop, board = _loop_with_tool(tmp_path, "import sys; sys.exit(3)")
    state = RelevantState(EnvironmentState("env-1", ("decode_tool",)), "guest", "s1", "c1")
    result = loop.run(state, max_actions=10)

    # No mechanism may be disproven from a tool failure; the run ends in a safe blocked state.
    assert result.outcome in {LoopOutcome.BLOCKED_NO_ACTIONS, LoopOutcome.BUDGET_EXHAUSTED}
    assert result.outcome is not LoopOutcome.VERIFIED
    for hypothesis in board.all_hypotheses():
        assert hypothesis.status is not HypothesisStatus.DISPROVEN
    # There is deliberately no "IMPOSSIBLE" outcome in the vocabulary.
    assert not hasattr(LoopOutcome, "IMPOSSIBLE")


def test_duplicate_probe_attempts_are_blocked_end_to_end(tmp_path: Path) -> None:
    # The failing tool means each mechanism stays UNRESOLVED, so the specialist keeps re-proposing
    # the same probes; the planner's dedup must stop them re-running in the same state.
    loop, board = _loop_with_tool(tmp_path, "import sys; sys.exit(3)")
    state = RelevantState(EnvironmentState("env-1", ("decode_tool",)), "guest", "s1", "c1")
    result = loop.run(state, max_actions=25)

    # Far fewer executions than the budget: each distinct probe runs once, then dedup blocks it.
    assert result.actions_taken <= 6
    assert result.outcome in {LoopOutcome.BLOCKED_NO_ACTIONS, LoopOutcome.BUDGET_EXHAUSTED}


def test_ambiguous_evidence_stays_unresolved_end_to_end(tmp_path: Path) -> None:
    # The tool succeeds (exit 0) but its output matches neither the supporting nor contradicting
    # marker of the registered discriminating test -> UNRESOLVES (inconclusive), never disproof.
    trusted = {
        "crypto-xor": TestSpecification(
            hypothesis_id="crypto-xor",
            supporting_body_contains=("DECODE_OK:",),
            contradicting_body_contains=("DECODE_NOT_A_FLAG",),
            authoritative_sources=(str(tmp_path / "handout.bin"),),
        ),
        "crypto-base64": TestSpecification(
            hypothesis_id="crypto-base64",
            supporting_body_contains=("DECODE_OK:",),
            contradicting_body_contains=("DECODE_FAILED",),
            authoritative_sources=(str(tmp_path / "handout.bin"),),
        ),
    }
    loop, board = _loop_with_tool(
        tmp_path, "print('INCONCLUSIVE_UNRECOGNIZED_OUTPUT')", trusted=trusted
    )
    state = RelevantState(EnvironmentState("env-1", ("decode_tool",)), "guest", "s1", "c1")
    result = loop.run(state, max_actions=10)

    assert result.outcome is not LoopOutcome.VERIFIED
    for hypothesis in board.all_hypotheses():
        assert hypothesis.status is not HypothesisStatus.DISPROVEN
        assert hypothesis.status is not HypothesisStatus.SUPPORTED
