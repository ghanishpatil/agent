"""End-to-end scenario B (CRYPTO) driven by the CryptoSpecialist through the REAL ReasoningLoop.

Initial ambiguity: the artifact could be base64 (encoding) or XOR (cipher). The specialist proposes
both; the cheaper/obvious base64 hypothesis is tested first and DISPROVEN by real evidence (a wrong
path), then XOR is SUPPORTED, then the observed flag is submitted and the Phase 2 kernel verifies.

Everything local/synthetic: one temp handout + one temp decode tool, run via SubprocessAdapter.
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
XOR_KEY = 0x42
REAL_FLAG = "CTF{xor_specialist}"

_DECODE_TOOL = '''
import base64, sys
mode, path = sys.argv[1], sys.argv[2]
raw = open(path, "rb").read()
if mode == "base64":
    try:
        d = base64.b64decode(raw, validate=True).decode("ascii")
        print("DECODE_OK:" + d if d.startswith("CTF{") else "DECODE_NOT_A_FLAG")
    except Exception:
        print("DECODE_FAILED")
elif mode == "xor42":
    d = bytes(b ^ 0x42 for b in raw).decode("utf-8", errors="replace")
    print("DECODE_OK:" + d if (d.startswith("CTF{") and d.endswith("}")) else "DECODE_NOT_A_FLAG")
else:
    print("DECODE_UNKNOWN_MODE")
'''


def build_crypto_specialist_loop(tmp_path: Path):
    handout = tmp_path / "handout.bin"
    handout.write_bytes(bytes(b ^ XOR_KEY for b in REAL_FLAG.encode("utf-8")))
    tool_path = tmp_path / "decode_tool.py"
    tool_path.write_text(_DECODE_TOOL, encoding="utf-8")
    handout_arg = str(handout)

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("decode_tool",)),
        trusted_sources={"decode_tool": (handout_arg,)},
    )
    registry = AdapterRegistry()
    registry.register(
        SubprocessAdapter("decode_tool", SubprocessCommand(sys.executable, (str(tool_path),)))
    )
    board = HypothesisBoard()

    brain = SpecialistReasoningSource(
        SpecialistRegistry.default(), available_tools=("decode_tool",)
    )
    trusted_sources_for_disproof = {
        "crypto-base64": TestSpecification(
            hypothesis_id="crypto-base64",
            supporting_body_contains=("DECODE_OK:",),
            contradicting_body_contains=("DECODE_FAILED",),
            authoritative_sources=(handout_arg,),
        ),
        "crypto-xor": TestSpecification(
            hypothesis_id="crypto-xor",
            supporting_body_contains=("DECODE_OK:",),
            contradicting_body_contains=("DECODE_NOT_A_FLAG",),
            authoritative_sources=(handout_arg,),
        ),
    }
    loop = ReasoningLoop(
        metadata=ChallengeMetadata(
            name="cipher-artifact",
            category="crypto",
            description="an encoded cipher artifact; possibly base64 or a single-byte xor key",
            files=(handout_arg,),
            flag_format="CTF{...}",
        ),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=brain,
        journal=RuntimeJournal(tmp_path / "runtime" / "crypto.jsonl"),
        run_id="spec-crypto-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )
    return loop, board, brain


def test_crypto_specialist_corrects_wrong_path_and_verifies(tmp_path: Path) -> None:
    loop, board, brain = build_crypto_specialist_loop(tmp_path)
    state = RelevantState(EnvironmentState("env-1", ("decode_tool",)), "guest", "s1", "crypto-1")
    result = loop.run(state, max_actions=8)

    assert result.outcome is LoopOutcome.VERIFIED
    # The wrong path (base64) was really tested and disproven by evidence, not skipped.
    assert board.get("crypto-base64").status is HypothesisStatus.DISPROVEN
    assert board.get("crypto-xor").status is HypothesisStatus.SUPPORTED
    # The crypto specialist was actually selected and did the work.
    assert "crypto" in {s.name for s in brain.last_selection.selected}
