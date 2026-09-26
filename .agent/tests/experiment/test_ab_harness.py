from __future__ import annotations

from pathlib import Path

from ctf_experiment.ab_harness import run_ab_experiment


def test_control_reproduces_frozen_baseline(labeled_corpus, audit_root: Path, tmp_path: Path) -> None:
    comparison = run_ab_experiment(labeled_corpus, tmp_path / "ab", audit_root=audit_root)
    control = comparison.control.summary()
    # The frozen Phase 5 baseline: 5/6 solved (one intended BLOCKED), verified == solved.
    assert control["case_count"] == 6
    assert abs(control["verified_solve_rate"] - (5 / 6)) < 1e-9
    assert control["false_verification_rate"] == 0.0
    assert control["budget_violations"] == 0
    per_case = control["per_case"]
    assert per_case["unavailable-tool"]["status"] == "BLOCKED"
    assert per_case["known-xor"]["status"] == "SOLVED"


def test_treatment_preserves_all_control_invariants(labeled_corpus, audit_root: Path, tmp_path: Path) -> None:
    comparison = run_ab_experiment(labeled_corpus, tmp_path / "ab", audit_root=audit_root)
    assert all(comparison.invariants.values()), comparison.invariants
    # Knowledge augmentation must never raise false verification/disproof or violate budgets.
    assert comparison.deltas["false_verification_rate"] <= 0.0
    assert comparison.deltas["false_disproof_rate"] <= 0.0
    assert comparison.deltas["budget_violations"] == 0
    assert not comparison.verdict.startswith("REJECT")
    assert not comparison.verdict.startswith("REGRESSION")


def test_treatment_does_not_fabricate_flags(labeled_corpus, audit_root: Path, tmp_path: Path) -> None:
    comparison = run_ab_experiment(labeled_corpus, tmp_path / "ab", audit_root=audit_root)
    # No case that was not solved suddenly returns a flag under augmentation.
    for case_id, after in comparison.treatment.summary()["per_case"].items():
        if after["status"] != "SOLVED":
            assert after["verified_flag"] is None


def test_experiment_runs_without_audit_root(labeled_corpus, tmp_path: Path) -> None:
    # External-only treatment vs memory-free control still preserves invariants.
    comparison = run_ab_experiment(labeled_corpus, tmp_path / "ab2", audit_root=None)
    assert all(comparison.invariants.values()), comparison.invariants
