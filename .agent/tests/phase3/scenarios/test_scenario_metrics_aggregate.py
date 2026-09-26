"""Aggregate evaluation metrics across all 3 synthetic end-to-end scenarios, per
prompt_phase 3.md section 9.

This runs the web, crypto, and forensics scenarios back to back and feeds their LoopResults into
metrics.evaluate_runs(), producing the minimum measurements the spec asks for: successful
termination rate, duplicate/unnecessary action rate, and actions-to-solution, across the full set
of synthetic scenarios rather than one scenario at a time.
"""
from __future__ import annotations

from pathlib import Path

from ctf_agent.metrics import evaluate_runs
from ctf_agent.models import EnvironmentState, RelevantState

from .test_scenario_crypto import build_crypto_scenario_loop
from .test_scenario_forensics import build_forensics_scenario_loop
from .test_scenario_web import build_web_scenario_loop


def test_all_three_synthetic_scenarios_verify_with_healthy_metrics(
    tmp_path: Path, local_http_server
) -> None:
    web_dir = tmp_path / "web"
    crypto_dir = tmp_path / "crypto"
    forensics_dir = tmp_path / "forensics"
    web_dir.mkdir()
    crypto_dir.mkdir()
    forensics_dir.mkdir()

    web_loop = build_web_scenario_loop(web_dir, local_http_server)
    web_state = RelevantState(
        EnvironmentState("env-1", ("http_probe", "challenge_service")), "guest", "s1", "web-1"
    )
    web_result = web_loop.run(web_state, max_actions=5)

    crypto_loop, _crypto_board = build_crypto_scenario_loop(crypto_dir)
    crypto_state = RelevantState(EnvironmentState("env-1", ("decode_tool",)), "guest", "s1", "crypto-1")
    crypto_result = crypto_loop.run(crypto_state, max_actions=5)

    forensics_loop, _forensics_board = build_forensics_scenario_loop(forensics_dir)
    forensics_state = RelevantState(
        EnvironmentState("env-1", ("analyze_tool",)), "guest", "s1", "forensics-1"
    )
    forensics_result = forensics_loop.run(forensics_state, max_actions=5)

    aggregate = evaluate_runs([web_result, crypto_result, forensics_result])

    assert aggregate.run_count == 3
    # All three scenarios are designed to reach VERIFIED via real, kernel-checked evidence.
    assert aggregate.successful_termination_rate == 1.0
    # No ground truth contradiction was supplied for any run, so both false-positive rates report
    # their honest zero-evidence-of-a-problem default.
    assert aggregate.false_verification_rate == 0.0
    assert aggregate.false_disproof_rate == 0.0
    # None of the three scripted scenarios ever repeats a duplicate action.
    assert aggregate.average_duplicate_action_rate == 0.0
    assert aggregate.average_actions_to_solution == 3.0
