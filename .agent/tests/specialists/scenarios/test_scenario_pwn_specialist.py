"""End-to-end scenario E (PWN) driven by the PwnSpecialist through the real loop.

A synthetic local target analyzed through a controlled harness adapter (NEVER direct execution).
Ambiguity: format-string vs stack-overflow. The specialist tests the (alphabetically first) format
mechanism -- the WRONG path -- which is DISPROVEN (format arg is constant), then the overflow
mechanism reaches a win path (SUPPORTED), and the observed flag is submitted + verified.
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
REAL_FLAG = "CTF{overflow_specialist}"

# A synthetic harness: given a mode, it reports the RESULT of attempting that exploit class against
# a local, controlled fake target. It never runs the real target; it deterministically models the
# outcome of each vulnerability-class hypothesis.
_HARNESS = '''
import sys
mode, _target = sys.argv[1], sys.argv[2]
if mode == "format":
    print("FORMAT_NOT_CONTROLLED")   # the format argument is a constant string
elif mode == "overflow":
    print("WIN:CTF{overflow_specialist}")  # controlled input reaches the win path
elif mode == "heap":
    print("NO_HEAP_PRIMITIVE")
else:
    print("UNKNOWN_MODE")
'''


def build_pwn_specialist_loop(tmp_path: Path):
    target = tmp_path / "vuln"
    target.write_bytes(b"\x7fELF fake target with gets() into a stack buffer and a printf call")
    harness = tmp_path / "harness.py"
    harness.write_text(_HARNESS, encoding="utf-8")
    arg = str(target)

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("exploit_harness",)),
        trusted_sources={"exploit_harness": (arg,)},
    )
    registry = AdapterRegistry()
    registry.register(
        SubprocessAdapter("exploit_harness", SubprocessCommand(sys.executable, (str(harness),)))
    )
    brain = SpecialistReasoningSource(
        SpecialistRegistry.default(), available_tools=("exploit_harness",)
    )
    trusted_sources_for_disproof = {
        "pwn-format": TestSpecification(
            hypothesis_id="pwn-format",
            supporting_body_contains=("LEAK:",),
            contradicting_body_contains=("FORMAT_NOT_CONTROLLED",),
            authoritative_sources=(arg,),
        ),
        "pwn-overflow": TestSpecification(
            hypothesis_id="pwn-overflow",
            supporting_body_contains=("WIN:",),
            contradicting_body_contains=("NO_OVERFLOW",),
            authoritative_sources=(arg,),
        ),
    }
    loop = ReasoningLoop(
        metadata=ChallengeMetadata(
            name="vuln-binary",
            category="pwn",
            description="a binary that uses gets() into a fixed stack buffer and also calls printf",
            files=(arg,),
            flag_format="CTF{...}",
        ),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=brain,
        journal=RuntimeJournal(tmp_path / "runtime" / "pwn.jsonl"),
        run_id="spec-pwn-1",
        clock=lambda: FIXED_CLOCK,
        board=HypothesisBoard(),
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )
    return loop, loop.board, brain


def test_pwn_specialist_finds_primitive_and_verifies(tmp_path: Path) -> None:
    loop, board, brain = build_pwn_specialist_loop(tmp_path)
    state = RelevantState(EnvironmentState("env-1", ("exploit_harness",)), "guest", "s1", "pwn-1")
    result = loop.run(state, max_actions=8)

    assert result.outcome is LoopOutcome.VERIFIED
    assert board.get("pwn-format").status is HypothesisStatus.DISPROVEN
    assert board.get("pwn-overflow").status is HypothesisStatus.SUPPORTED
    assert "pwn" in {s.name for s in brain.last_selection.selected}
