"""Synthetic end-to-end scenario B (CRYPTO/REVERSE), per prompt_phase 3.md section 8.

A local deterministic handout file holds a single-byte-XOR-encoded flag. The agent's first
hypothesis assumes plain Base64 (wrong); it runs a real local decode *tool* (a tiny stdlib-only
script invoked through ``SubprocessAdapter`` -- decoding logic lives in a trusted tool, never in
the adapter or in "LLM interpretation") that attempts a base64 decode and reports failure. That
failure is captured as a registered, evidence-based disproof of h-base64 (via TestSpecification +
an authoritative source), not an LLM assertion. The agent then proposes h-xor, runs the XOR decode
tool, gets a valid-looking flag, and submits it; the kernel independently verifies it.

Everything is local: one temp handout file plus one temp decode script, both under tmp_path.
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
XOR_KEY = 0x42
REAL_FLAG = "CTF{xor_not_base64}"

_DECODE_TOOL_SOURCE = '''
import base64, sys

mode = sys.argv[1]
path = sys.argv[2]
with open(path, "rb") as fh:
    raw = fh.read()

if mode == "base64":
    try:
        decoded = base64.b64decode(raw, validate=True).decode("ascii")
        if decoded.startswith("CTF{") and decoded.endswith("}"):
            print("DECODE_OK:" + decoded)
        else:
            print("DECODE_NOT_A_FLAG")
    except Exception:
        print("DECODE_FAILED")
elif mode == "xor42":
    decoded = bytes(b ^ 0x42 for b in raw).decode("utf-8", errors="replace")
    if decoded.startswith("CTF{") and decoded.endswith("}"):
        print("DECODE_OK:" + decoded)
    else:
        print("DECODE_NOT_A_FLAG")
else:
    print("DECODE_UNKNOWN_MODE")
'''


class ScriptedCryptoReasoning:
    """Models hypothesis correction: base64 first (wrong), then xor42 (right)."""

    def __init__(self, handout_path: str) -> None:
        self._handout_path = handout_path
        self._step = 0

    def suggest_hypotheses(self, context):
        return ()

    def suggest_actions(self, context) -> Tuple[ActionSuggestion, ...]:
        self._step += 1
        if self._step == 1:
            return (
                ActionSuggestion(
                    hypothesis_id="h-base64",
                    objective="attempt base64 decode of the handout",
                    tool="decode_tool",
                    target="handout.bin",
                    input_data=["base64", self._handout_path],
                    expected_observation="DECODE_OK: a valid-looking flag",
                ),
            )
        if self._step == 2:
            return (
                ActionSuggestion(
                    hypothesis_id="h-xor",
                    objective="attempt single-byte XOR (key 0x42) decode of the handout",
                    tool="decode_tool",
                    target="handout.bin",
                    input_data=["xor42", self._handout_path],
                    expected_observation="DECODE_OK: a valid-looking flag",
                ),
            )
        # Step 3: now that h-xor has one piece of evidence containing the decoded flag, propose
        # submitting it. The kernel's own VerificationController -- not this script -- decides
        # whether it actually verifies.
        return (
            ActionSuggestion(
                hypothesis_id="h-xor",
                objective="submit the flag observed in the XOR decode",
                tool="decode_tool",
                target="handout.bin",
                input_data=["xor42", self._handout_path],
                candidate_flag=REAL_FLAG,
            ),
        )

    def interpret(self, context):
        return ()


def build_crypto_scenario_loop(tmp_path: Path) -> tuple[ReasoningLoop, HypothesisBoard]:
    """Reusable builder so other tests (e.g. a cross-scenario metrics aggregate) can run this
    exact scenario without duplicating its setup."""
    encoded = bytes(b ^ XOR_KEY for b in REAL_FLAG.encode("utf-8"))
    handout_path = tmp_path / "handout.bin"
    handout_path.write_bytes(encoded)

    decode_tool_path = tmp_path / "decode_tool.py"
    decode_tool_path.write_text(_DECODE_TOOL_SOURCE, encoding="utf-8")

    # "decode_tool" is a trusted local tool: its output is authoritative for THIS run, same as any
    # other explicitly-configured local analysis tool the agent is allowed to run. The loop always
    # calls kernel.process(source=action.target), and both scripted actions target "handout.bin",
    # so that literal string is what must appear in both authoritative_output_tools' trust mapping
    # and each TestSpecification's authoritative_sources.
    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("decode_tool",)),
        trusted_sources={"decode_tool": ("handout.bin",)},
    )
    board = HypothesisBoard()
    board.propose_hypothesis("h-base64", "the handout is plain base64-encoded", technique="base64")
    board.propose_hypothesis("h-xor", "the handout is single-byte XOR-encoded", technique="xor")

    registry = AdapterRegistry()
    registry.register(
        SubprocessAdapter("decode_tool", SubprocessCommand(sys.executable, (str(decode_tool_path),)))
    )

    # Pre-registered discriminating tests: DECODE_OK -> supports; DECODE_FAILED/DECODE_NOT_A_FLAG
    # -> contradicts. Both are real markers produced by the trusted decode tool's own output, not
    # anything the loop or an LLM asserts.
    trusted_sources_for_disproof = {
        "h-base64": TestSpecification(
            hypothesis_id="h-base64",
            supporting_body_contains=("DECODE_OK:",),
            contradicting_body_contains=("DECODE_FAILED",),
            authoritative_sources=("handout.bin",),
        ),
        "h-xor": TestSpecification(
            hypothesis_id="h-xor",
            supporting_body_contains=("DECODE_OK:",),
            contradicting_body_contains=("DECODE_NOT_A_FLAG",),
            authoritative_sources=("handout.bin",),
        ),
    }

    loop = ReasoningLoop(
        metadata=ChallengeMetadata(name="crypto-scenario", category="crypto"),
        kernel=kernel,
        adapters=registry,
        planner=ActionPlanner(registry),
        reasoning_source=ScriptedCryptoReasoning(str(handout_path)),
        journal=RuntimeJournal(tmp_path / "runtime" / "crypto_scenario.jsonl"),
        run_id="scenario-crypto-1",
        clock=lambda: FIXED_CLOCK,
        board=board,
        trusted_sources_for_disproof=trusted_sources_for_disproof,
    )
    return loop, board


def test_scenario_crypto_hypothesis_corrected_after_disproof(tmp_path: Path) -> None:
    loop, board = build_crypto_scenario_loop(tmp_path)
    state = RelevantState(EnvironmentState("env-1", ("decode_tool",)), "guest", "s1", "crypto-1")
    result = loop.run(state, max_actions=5)

    assert board.get("h-base64").status is HypothesisStatus.DISPROVEN
    assert board.get("h-xor").status is HypothesisStatus.SUPPORTED
    assert result.outcome is LoopOutcome.VERIFIED

    from ctf_agent.metrics import evaluate_single_run

    metrics = evaluate_single_run(result)
    assert metrics.verified is True
    assert metrics.actions_to_solution == 3
    assert metrics.state_is_consistent
    # h-base64's disproof came from a real registered discriminating test, not a wasted probe --
    # it counts against neither duplicate_action_count nor unnecessary_action_count, since it did
    # produce a real DISPROVES impact.
    assert metrics.unnecessary_action_count == 0
