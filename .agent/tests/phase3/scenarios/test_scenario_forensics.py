"""Synthetic end-to-end scenario C (FORENSICS/STEGO), per prompt_phase 3.md section 8.

A local deterministic "extracted artifact" file has a flag appended after a trailer marker (a
simple, deterministic stand-in for a real steganographic payload). Two candidate mechanisms are
plausible up front: (1) EXIF-style metadata comment field, (2) an appended-trailer payload. The
agent must pick between them -- it tries the (wrong) EXIF-style hypothesis first via a real local
inspection tool, gets an inconclusive/negative result, then tries the appended-trailer hypothesis,
finds the flag, and the kernel authoritatively verifies it.

All analysis "tools" here are tiny local stdlib-only scripts run through SubprocessAdapter -- the
mechanism-selection logic lives in the scripted reasoning source (standing in for an LLM), never in
an adapter.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

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
from ctf_agent.proposals import ActionSuggestion


FIXED_CLOCK = datetime(2026, 9, 24, tzinfo=timezone.utc)
REAL_FLAG = "CTF{trailer_not_exif}"
TRAILER_MARKER = b"\x00\x00FLAGSTART\x00\x00"

_ANALYZE_TOOL_SOURCE = '''
import sys

mode = sys.argv[1]
path = sys.argv[2]
with open(path, "rb") as fh:
    raw = fh.read()

if mode == "exif_comment":
    # A real EXIF reader would look for a JPEG COM segment; this synthetic artifact never has
    # one, so this mode always honestly reports nothing found.
    print("NO_COMMENT_FIELD_FOUND")
elif mode == "trailer_scan":
    marker = b"\\x00\\x00FLAGSTART\\x00\\x00"
    idx = raw.find(marker)
    if idx == -1:
        print("NO_TRAILER_FOUND")
    else:
        payload = raw[idx + len(marker):].decode("utf-8", errors="replace")
        print("TRAILER_PAYLOAD:" + payload)
else:
    print("UNKNOWN_MODE")
'''


class ScriptedForensicsReasoning:
    """Tries the wrong mechanism (EXIF comment) first, then the right one (trailer scan)."""

    def __init__(self, artifact_path: str) -> None:
        self._artifact_path = artifact_path
        self._step = 0

    def suggest_hypotheses(self, context):
        return ()

    def suggest_actions(self, context) -> Tuple[ActionSuggestion, ...]:
        self._step += 1
        if self._step == 1:
            return (
                ActionSuggestion(
                    hypothesis_id="h-exif",
                    objective="inspect for an EXIF-style comment field",
                    tool="analyze_tool",
                    target="artifact.bin",
                    input_data=["exif_comment", self._artifact_path],
                    expected_observation="a comment field containing a flag",
                ),
            )
        if self._step == 2:
            return (
                ActionSuggestion(
                    hypothesis_id="h-trailer",
                    objective="scan for an appended trailer payload",
                    tool="analyze_tool",
                    target="artifact.bin",
                    input_data=["trailer_scan", self._artifact_path],
                    expected_observation="a trailer payload containing a flag",
                ),
            )
        return (
            ActionSuggestion(
                hypothesis_id="h-trailer",
                objective="submit the flag observed in the trailer payload",
                tool="analyze_tool",
                target="artifact.bin",
                input_data=["trailer_scan", self._artifact_path],
                candidate_flag=REAL_FLAG,
            ),
        )

    def interpret(self, context):
        return ()


def build_forensics_scenario_loop(tmp_path: Path) -> tuple[ReasoningLoop, HypothesisBoard]:
    """Reusable builder so other tests (e.g. a cross-scenario metrics aggregate) can run this
    exact scenario without duplicating its setup."""
    artifact_path = tmp_path / "artifact.bin"
    artifact_path.write_bytes(b"\xff\xd8\xff\xe0JFIF-like-header-bytes" + TRAILER_MARKER + REAL_FLAG.encode("utf-8"))

    analyze_tool_path = tmp_path / "analyze_tool.py"
    analyze_tool_path.write_text(_ANALYZE_TOOL_SOURCE, encoding="utf-8")

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("analyze_tool",)),
        trusted_sources={"analyze_tool": ("artifact.bin",)},
    )
    board = HypothesisBoard()
    board.propose_hypothesis(
        "h-exif", "the flag is hidden in an EXIF-style comment field", technique="exif-metadata"
    )
    board.propose_hypothesis(
        "h-trailer", "the flag is appended after a trailer marker", technique="appended-trailer"
    )

    registry = AdapterRegistry()
    registry.register(
        SubprocessAdapter(
            "analyze_tool", SubprocessCommand(sys.executable, (str(analyze_tool_path),))
        )
    )

    trusted_sources_for_disproof = {
        "h-exif": TestSpecification(
            hypothesis_id="h-exif",
            supporting_body_contains=("COMMENT_FOUND:",),
            contradicting_body_contains=("NO_COMMENT_FIELD_FOUND",),
            authoritative_sources=("artifact.bin",),
        ),
        "h-trailer": TestSpecification(
            hypothesis_id="h-trailer",
            supporting_body_contains=("TRAILER_PAYLOAD:",),
            contradicting_body_contains=("NO_TRAILER_FOUND",),
            authoritative_sources=("artifact.bin",),
        ),
    }

    loop = ReasoningLoop(
        metadata=ChallengeMetadata(name="forensics-scenario", category="forensics"),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=ScriptedForensicsReasoning(str(artifact_path)),
        journal=RuntimeJournal(tmp_path / "runtime" / "forensics_scenario.jsonl"),
        run_id="scenario-forensics-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )
    return loop, board


def test_scenario_forensics_selects_correct_mechanism_among_candidates(tmp_path: Path) -> None:
    loop, board = build_forensics_scenario_loop(tmp_path)
    state = RelevantState(EnvironmentState("env-1", ("analyze_tool",)), "guest", "s1", "forensics-1")
    result = loop.run(state, max_actions=5)

    assert board.get("h-exif").status is HypothesisStatus.DISPROVEN
    assert board.get("h-trailer").status is HypothesisStatus.SUPPORTED
    assert result.outcome is LoopOutcome.VERIFIED

    # The disproven mechanism must never have been marked disproven by anything other than the
    # kernel-processed, registered discriminating test.
    exif_pipeline_result = result.pipeline_results[0]
    assert exif_pipeline_result.impact.value == "DISPROVES"

    from ctf_agent.metrics import evaluate_single_run

    metrics = evaluate_single_run(result)
    assert metrics.verified is True
    assert metrics.actions_to_solution == 3
    assert metrics.state_is_consistent
    assert metrics.unnecessary_action_count == 0
