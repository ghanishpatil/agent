from __future__ import annotations

from pathlib import Path

from ctf_agent import SolveStatus
from ctf_agent.autonomy.evaluation import EvaluationHarness, EvaluationKind

from ctf_bench.phase5_benchmark import build_phase5_cases


def build_evaluation_cases(tmp_path: Path, crypto_package):
    """Delegate to the frozen benchmark so the challenge set is a single source of truth."""
    return build_phase5_cases(tmp_path, crypto_package)


def test_evaluation_separates_known_novel_adversarial_and_heldout(
    tmp_path: Path, crypto_package
) -> None:
    cases, adversarial_verifier = build_evaluation_cases(tmp_path, crypto_package)
    report = EvaluationHarness().run(cases)

    assert len(report.cases) == 6
    assert {item.kind for item in report.cases} == {
        EvaluationKind.KNOWN,
        EvaluationKind.NOVEL,
        EvaluationKind.ADVERSARIAL,
        EvaluationKind.HELD_OUT,
    }
    # Negative results are retained: unavailable-tool is expected BLOCKED, not hidden.
    blocked = next(item for item in report.cases if item.case_id == "unavailable-tool")
    assert blocked.result.status is SolveStatus.BLOCKED
    assert blocked.result.verified_flag is None
    assert all(item.status_correct and item.flag_correct for item in report.cases)

    # The adversarial decoy may be submitted, but it cannot verify; the solver recovers to SSTI.
    assert adversarial_verifier.submitted
    assert adversarial_verifier.submitted[-1] == "CTF{real_template_flag}"


def test_all_twenty_phase5_metrics_are_computed(tmp_path: Path, crypto_package) -> None:
    cases, _ = build_evaluation_cases(tmp_path, crypto_package)
    report = EvaluationHarness().run(cases)
    metrics = report.metrics

    assert metrics.case_count == 6
    assert 0.0 < metrics.solve_rate < 1.0  # includes the expected blocked case
    assert metrics.verified_solve_rate == metrics.solve_rate
    assert metrics.false_verification_rate == 0.0
    assert metrics.false_disproof_rate == 0.0
    assert metrics.average_actions_per_solve > 0
    assert metrics.median_actions_per_solve > 0
    assert 0.0 < metrics.duplicate_action_rate < 1.0
    assert metrics.blind_retry_rate == 0.0
    assert metrics.dead_end_recovery_rate > 0
    assert metrics.environmental_failure_recovery_rate == 1.0
    assert metrics.tool_failure_recovery_rate == 1.0
    assert metrics.specialist_selection_accuracy > 0
    assert metrics.useful_specialist_proposal_rate > 0
    assert metrics.candidate_verification_success > 0
    assert metrics.stop_correctness == 1.0
    assert metrics.budget_violations == 0
    assert metrics.average_reasoning_iterations > 0
    assert metrics.average_time_to_verified_solution_ms >= 0
    assert metrics.average_resource_tool_cost > 0
    assert metrics.terminal_state_correctness == 1.0


def test_anti_memorization_pair_uses_different_mechanisms(tmp_path: Path, crypto_package) -> None:
    cases, _ = build_evaluation_cases(tmp_path, crypto_package)
    report = EvaluationHarness().run(cases)
    known = next(item.result for item in report.cases if item.case_id == "known-xor")
    held = next(item.result for item in report.cases if item.case_id == "heldout-classical")

    assert known.verified_flag != held.verified_flag
    assert any(h.hypothesis_id == "crypto-xor" and h.status == "SUPPORTED" for h in known.key_hypotheses)
    assert any(
        h.hypothesis_id == "crypto-classical" and h.status == "SUPPORTED"
        for h in held.key_hypotheses
    )
