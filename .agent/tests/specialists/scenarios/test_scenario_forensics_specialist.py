"""End-to-end scenario C (FORENSICS/STEGO) driven by the ForensicsSpecialist through the real loop.

Initial ambiguity: EXIF-comment vs appended-trailer hiding mechanism. The specialist tests the
(alphabetically first, cheaper) exif mechanism -- the WRONG path -- which is DISPROVEN by real
evidence, then the trailer mechanism is SUPPORTED and the observed flag is submitted + verified.
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
REAL_FLAG = "CTF{trailer_specialist}"
MARKER = b"\x00\x00FLAGSTART\x00\x00"

_ANALYZE_TOOL = '''
import sys
mode, path = sys.argv[1], sys.argv[2]
raw = open(path, "rb").read()
if mode == "exif_comment":
    print("NO_COMMENT_FIELD_FOUND")
elif mode == "trailer_scan":
    m = b"\\x00\\x00FLAGSTART\\x00\\x00"
    i = raw.find(m)
    print("TRAILER_PAYLOAD:" + raw[i+len(m):].decode("utf-8","replace") if i != -1 else "NO_TRAILER_FOUND")
else:
    print("UNKNOWN_MODE")
'''


def build_forensics_specialist_loop(tmp_path: Path):
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"\xff\xd8\xff\xe0header-bytes" + MARKER + REAL_FLAG.encode("utf-8"))
    tool_path = tmp_path / "analyze_tool.py"
    tool_path.write_text(_ANALYZE_TOOL, encoding="utf-8")
    arg = str(artifact)

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
        "forensics-exif": TestSpecification(
            hypothesis_id="forensics-exif",
            supporting_body_contains=("COMMENT_FOUND:",),
            contradicting_body_contains=("NO_COMMENT_FIELD_FOUND",),
            authoritative_sources=(arg,),
        ),
        "forensics-trailer": TestSpecification(
            hypothesis_id="forensics-trailer",
            supporting_body_contains=("TRAILER_PAYLOAD:",),
            contradicting_body_contains=("NO_TRAILER_FOUND",),
            authoritative_sources=(arg,),
        ),
    }
    loop = ReasoningLoop(
        metadata=ChallengeMetadata(
            name="hidden-artifact",
            category="forensics",
            description="a JPEG with EXIF metadata and possibly appended trailer data after its end",
            files=(arg,),
            flag_format="CTF{...}",
        ),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=brain,
        journal=RuntimeJournal(tmp_path / "runtime" / "forensics.jsonl"),
        run_id="spec-forensics-1",
        clock=lambda: FIXED_CLOCK,
        board=HypothesisBoard(),
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )
    return loop, loop.board, brain


def test_forensics_specialist_selects_mechanism_and_verifies(tmp_path: Path) -> None:
    loop, board, brain = build_forensics_specialist_loop(tmp_path)
    state = RelevantState(EnvironmentState("env-1", ("analyze_tool",)), "guest", "s1", "forensics-1")
    result = loop.run(state, max_actions=8)

    assert result.outcome is LoopOutcome.VERIFIED
    assert board.get("forensics-exif").status is HypothesisStatus.DISPROVEN
    assert board.get("forensics-trailer").status is HypothesisStatus.SUPPORTED
    assert "forensics" in {s.name for s in brain.last_selection.selected}
