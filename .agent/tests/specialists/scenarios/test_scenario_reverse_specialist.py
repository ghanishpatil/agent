"""End-to-end scenario D (REVERSE) driven by the ReverseSpecialist through the real loop.

Ambiguity: is the flag guarded by a key-comparison check, or stored as an embedded string? The
specialist tests the (alphabetically first) keycheck mechanism -- the WRONG path -- which is
DISPROVEN (the check is opaque/dynamic), then static strings analysis reveals an embedded flag
(SUPPORTED), which is submitted + verified.
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
REAL_FLAG = "CTF{strings_specialist}"

_ANALYZE_TOOL = f'''
import sys
mode, _path = sys.argv[1], sys.argv[2]
if mode == "keycheck":
    print("KEYCHECK_OPAQUE")   # the comparison is computed at runtime; static angle inconclusive
elif mode == "strings":
    print("STRINGS_FLAG:{REAL_FLAG}")
elif mode == "decode":
    print("DECODE_NO_TRANSFORM")
else:
    print("UNKNOWN_MODE")
'''


def build_reverse_specialist_loop(tmp_path: Path):
    binary = tmp_path / "crackme"
    binary.write_bytes(b"\x7fELF crackme that validates a serial key and embeds strings")
    tool_path = tmp_path / "analyze_tool.py"
    tool_path.write_text(_ANALYZE_TOOL, encoding="utf-8")
    arg = str(binary)

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("analyze_tool",)),
        trusted_sources={"analyze_tool": (arg,)},
    )
    registry = AdapterRegistry()
    registry.register(
        SubprocessAdapter("analyze_tool", SubprocessCommand(sys.executable, (str(tool_path),)))
    )
    brain = SpecialistReasoningSource(
        SpecialistRegistry.default(), available_tools=("analyze_tool",)
    )
    trusted_sources_for_disproof = {
        "reverse-keycheck": TestSpecification(
            hypothesis_id="reverse-keycheck",
            supporting_body_contains=("KEYCHECK_TARGET:",),
            contradicting_body_contains=("KEYCHECK_OPAQUE",),
            authoritative_sources=(arg,),
        ),
        "reverse-strings": TestSpecification(
            hypothesis_id="reverse-strings",
            supporting_body_contains=("STRINGS_FLAG:",),
            contradicting_body_contains=("NO_STRINGS_FLAG",),
            authoritative_sources=(arg,),
        ),
    }
    loop = ReasoningLoop(
        metadata=ChallengeMetadata(
            name="crackme",
            category="rev",
            description="an ELF crackme binary that validates a serial key; may embed strings",
            files=(arg,),
            flag_format="CTF{...}",
        ),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=brain,
        journal=RuntimeJournal(tmp_path / "runtime" / "reverse.jsonl"),
        run_id="spec-reverse-1",
        clock=lambda: FIXED_CLOCK,
        board=HypothesisBoard(),
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )
    return loop, loop.board, brain


def test_reverse_specialist_static_first_and_verifies(tmp_path: Path) -> None:
    loop, board, brain = build_reverse_specialist_loop(tmp_path)
    state = RelevantState(EnvironmentState("env-1", ("analyze_tool",)), "guest", "s1", "reverse-1")
    result = loop.run(state, max_actions=8)

    assert result.outcome is LoopOutcome.VERIFIED
    assert board.get("reverse-keycheck").status is HypothesisStatus.DISPROVEN
    assert board.get("reverse-strings").status is HypothesisStatus.SUPPORTED
    assert "reverse" in {s.name for s in brain.last_selection.selected}
