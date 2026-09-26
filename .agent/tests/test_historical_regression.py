from __future__ import annotations

import json
from pathlib import Path

from ctf_agent.regression import render_historical_regression_report, run_historical_regression


ROOT = Path(__file__).parents[2]
FAILURES = ROOT / ".agent_audit" / "failures" / "failures.jsonl"
EXPECTATIONS = Path(__file__).parent / "fixtures" / "historical_expectations.json"
REPLAYS = Path(__file__).parent / "fixtures" / "historical_replays.json"


def test_all_twelve_historical_failures_have_explicit_regression_expectations() -> None:
    failure_ids = {
        json.loads(line)["id"] for line in FAILURES.read_text(encoding="utf-8").splitlines() if line
    }
    expected_ids = set(json.loads(EXPECTATIONS.read_text(encoding="utf-8")))
    replay_ids = set(json.loads(REPLAYS.read_text(encoding="utf-8")))
    assert len(failure_ids) == 12
    assert expected_ids == failure_ids
    assert replay_ids == failure_ids


def test_all_historical_failure_regressions_pass() -> None:
    results = run_historical_regression(FAILURES, EXPECTATIONS, REPLAYS)
    assert len(results) == 12
    assert all(result.passed for result in results), [result for result in results if not result.passed]


def test_historical_regression_report_is_traceable_and_complete() -> None:
    results = run_historical_regression(FAILURES, EXPECTATIONS, REPLAYS)
    report = render_historical_regression_report(FAILURES, EXPECTATIONS, results)
    assert report.startswith("# Historical Failure Regression")
    assert report.count("| FAIL-") == 12
    assert "12/12 PASS" in report
    assert "FAIL-001" in report and "SUPPORTED:CONTINUE" in report
