from __future__ import annotations

from pathlib import Path

from ctf_agent.autonomy.contracts import (
    ActionTrace,
    ChallengeUnderstanding,
    HypothesisTrace,
    SolveResult,
    SolveStatus,
)

from ctf_experiment.knowledge_dependent_benchmark import (
    BASELINE_SOLVABLE,
    CONFLICTING,
    KNOWLEDGE_DEPENDENT,
    MISLEADING,
    NOISE,
    build_cases,
)
from ctf_experiment.knowledge_dependent_harness import (
    _knowledge_attributable,
    run_knowledge_dependent_experiment,
)


def test_benchmark_has_all_five_case_kinds(tmp_path: Path) -> None:
    cases = build_cases(tmp_path / "bench")
    kinds = {c.kind for c in cases}
    assert kinds == {BASELINE_SOLVABLE, KNOWLEDGE_DEPENDENT, MISLEADING, CONFLICTING, NOISE}


def test_experiment_outcomes_and_safety(tmp_path: Path) -> None:
    report = run_knowledge_dependent_experiment(tmp_path / "work")
    by_id = {o.case_id: o for o in report.outcomes}

    # Baseline solvable in both arms (knowledge not required for capability).
    base = by_id["kd-baseline-solvable"]
    assert base.control["status"] == "SOLVED"
    assert base.treatment["status"] == "SOLVED"

    # Knowledge-dependent: same verifiable env but no indicators -> both arms BLOCKED.
    dep = by_id["kd-knowledge-dependent"]
    assert dep.control["status"] == "BLOCKED"
    assert dep.treatment["status"] == "BLOCKED"
    assert dep.knowledge_attributable is False
    assert dep.attribution_reasons  # explains why (treatment did not kernel-verify)

    # All safety invariants preserved on every case.
    assert report.all_safety_invariants_preserved
    for outcome in report.outcomes:
        assert all(outcome.safety.values()), (outcome.case_id, outcome.safety)


def test_misleading_knowledge_never_verifies_decoy(tmp_path: Path) -> None:
    report = run_knowledge_dependent_experiment(tmp_path / "work")
    mis = next(o for o in report.outcomes if o.case_id == "kd-misleading")
    assert mis.treatment["verified_flag"] == "CTF{kd_misleading_real}"
    assert mis.treatment["verified_flag"] != "CTF{sqli_decoy_should_never_verify}"
    assert mis.safety["no_false_verification"]


def test_conflicting_knowledge_does_not_cause_false_disproof(tmp_path: Path) -> None:
    report = run_knowledge_dependent_experiment(tmp_path / "work")
    conf = next(o for o in report.outcomes if o.case_id == "kd-conflicting")
    assert conf.treatment["status"] == "SOLVED"
    assert conf.safety["no_false_disproof"]


def test_zero_knowledge_attributable_solves_current_architecture(tmp_path: Path) -> None:
    report = run_knowledge_dependent_experiment(tmp_path / "work")
    # Honest result: advisory knowledge is observability-only in the frozen solver.
    assert report.knowledge_attributable_verified_solves == 0
    assert report.all_safety_invariants_preserved
    assert "KNOWLEDGE-SAFE" in report.verdict()


# -- Gate soundness: the strict gate MUST credit a genuine flip, so the 0 above is a real
#    architectural result, not a broken/over-strict gate. -------------------------------------


def _understanding() -> ChallengeUnderstanding:
    return ChallengeUnderstanding((), (), (), (), ())


def _blocked() -> SolveResult:
    return SolveResult(
        status=SolveStatus.BLOCKED,
        run_id="r",
        challenge_name="c",
        understanding=_understanding(),
        terminal_reason="no useful action",
    )


def _verified_solve() -> SolveResult:
    actions = (
        ActionTrace("a1", "probe ssti", "http_probe", "u", "TARGET_RESPONSE", "SUPPORTS", "CONTINUE", 1),
        ActionTrace("a2", "submit", "flag_verifier", "g", "SUCCESS", "SUPPORTS", "STOP", 1),
    )
    hyp = HypothesisTrace("web-ssti", "ssti", "SUPPORTED", ("e1",), (), (), 1)
    return SolveResult(
        status=SolveStatus.SOLVED,
        run_id="r",
        challenge_name="c",
        understanding=_understanding(),
        terminal_reason="verified",
        verified_flag="CTF{x}",
        verification_evidence_ids=("e1",),
        final_verification_method="AUTHORITATIVE_VERIFIER",
        actions=actions,
        key_hypotheses=(hyp,),
    )


class _Case:
    expected_flag = "CTF{x}"
    expected_hypothesis = "web-ssti"
    decoy_flag = ""


def test_gate_credits_a_genuine_knowledge_flip() -> None:
    attributable, reasons = _knowledge_attributable(_Case(), _blocked(), _verified_solve())
    assert attributable is True
    assert reasons == ()


def test_gate_rejects_solve_without_supporting_evidence() -> None:
    # Treatment "solved" but no SUPPORTS action / unsupported hypothesis -> not attributable.
    weak = SolveResult(
        status=SolveStatus.SOLVED,
        run_id="r",
        challenge_name="c",
        understanding=_understanding(),
        terminal_reason="verified",
        verified_flag="CTF{x}",
        verification_evidence_ids=("e1",),
        final_verification_method="AUTHORITATIVE_VERIFIER",
        actions=(ActionTrace("a", "submit", "v", "g", "SUCCESS", "NONE", "STOP", 1),),
        key_hypotheses=(HypothesisTrace("web-ssti", "s", "PLAUSIBLE", (), (), (), 1),),
    )
    attributable, reasons = _knowledge_attributable(_Case(), _blocked(), weak)
    assert attributable is False
    assert any("discriminating" in r for r in reasons)
