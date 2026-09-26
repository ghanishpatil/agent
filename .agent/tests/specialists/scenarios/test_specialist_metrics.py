"""Specialist quality metrics (phase4.md section 18) computed across the 5 domain scenarios."""
from __future__ import annotations

from pathlib import Path

from ctf_agent.models import EnvironmentState, RelevantState
from ctf_agent.specialists.metrics import (
    evaluate_specialist_run,
    evaluate_specialist_runs,
)

from .test_scenario_crypto_specialist import build_crypto_specialist_loop
from .test_scenario_forensics_specialist import build_forensics_specialist_loop
from .test_scenario_pwn_specialist import build_pwn_specialist_loop
from .test_scenario_reverse_specialist import build_reverse_specialist_loop
from .test_scenario_web_specialist import build_web_specialist_loop


def _state(tools):
    return RelevantState(EnvironmentState("env-1", tools), "guest", "s1", "c1")


def test_single_run_metrics_capture_wrong_path_recovery(tmp_path: Path) -> None:
    loop, board, brain = build_crypto_specialist_loop(tmp_path)
    result = loop.run(_state(("decode_tool",)), max_actions=8)
    metrics = evaluate_specialist_run(
        result, board, brain.last_selection, expected_flag="CTF{xor_specialist}"
    )
    assert metrics.verified is True
    assert metrics.recovered_from_wrong_path is True  # base64 disproven, xor won
    assert metrics.disproven_hypotheses >= 1
    assert metrics.false_verification_count == 0
    assert metrics.false_disproof_count == 0
    assert metrics.discriminating_tests_run >= 2
    assert "crypto" in metrics.selected_specialists


def test_aggregate_metrics_across_all_five_specialist_scenarios(
    tmp_path: Path, local_http_server
) -> None:
    runs = []

    web_loop, web_board, web_brain = build_web_specialist_loop(tmp_path / "web", local_http_server)
    (tmp_path / "web").mkdir(exist_ok=True)
    runs.append(
        (
            web_loop.run(_state(("http_probe",)), max_actions=8),
            web_board,
            web_brain,
            "CTF{web_specialist}",
        )
    )

    for sub, builder, tools, flag in (
        ("crypto", build_crypto_specialist_loop, ("decode_tool",), "CTF{xor_specialist}"),
        ("forensics", build_forensics_specialist_loop, ("analyze_tool",), "CTF{trailer_specialist}"),
        ("reverse", build_reverse_specialist_loop, ("analyze_tool",), "CTF{strings_specialist}"),
        ("pwn", build_pwn_specialist_loop, ("exploit_harness",), "CTF{overflow_specialist}"),
    ):
        sub_dir = tmp_path / sub
        sub_dir.mkdir(exist_ok=True)
        loop, board, brain = builder(sub_dir)
        runs.append((loop.run(_state(tools), max_actions=8), board, brain, flag))

    per_run = [
        evaluate_specialist_run(result, board, brain.last_selection, expected_flag=flag)
        for result, board, brain, flag in runs
    ]
    aggregate = evaluate_specialist_runs(per_run)

    assert aggregate.run_count == 5
    assert aggregate.successful_termination_rate == 1.0
    assert aggregate.false_verification_rate == 0.0
    assert aggregate.false_disproof_rate == 0.0
    # 4 of 5 scenarios (crypto/forensics/reverse/pwn/web) exercise a disproven wrong path then win.
    assert aggregate.recovered_from_wrong_path_rate >= 0.8
    assert aggregate.average_actions_to_solution is not None
