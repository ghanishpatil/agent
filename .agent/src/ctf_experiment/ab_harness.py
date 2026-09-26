"""Controlled A/B experiment over the frozen Phase 5 benchmark.

Both arms run the identical frozen solver on the identical frozen benchmark cases. The
ONLY difference is ``environment.memory_root`` (the advisory-memory boundary):

- control  : the existing audit corpus (the Phase 5 baseline advisory memory)
- treatment: a COPY of the audit corpus with projected external writeup knowledge layered on

Nothing else changes. The trust kernel, planner, adapters, verification, and benchmark
semantics are untouched. Retrieved knowledge can only influence advisory ranking; it can
never become evidence or a verified flag.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from ctf_agent.autonomy.contracts import EnvironmentConfig, SolveStatus
from ctf_agent.autonomy.evaluation import EvaluationHarness, EvaluationReport

from ctf_bench.phase5_benchmark import build_phase5_cases
from ctf_ingest.advisory_projection import build_augmented_memory
from ctf_ingest.models import KnowledgeRecord


def _memory_factory(base_factory, memory_root: Optional[Path]):
    def factory() -> EnvironmentConfig:
        return replace(base_factory(), memory_root=memory_root)

    return factory


def _wrap_cases(cases, memory_root: Optional[Path]):
    return tuple(
        replace(case, environment_factory=_memory_factory(case.environment_factory, memory_root))
        for case in cases
    )


def summarize_report(report: EvaluationReport) -> Dict[str, object]:
    m = report.metrics
    return {
        "case_count": m.case_count,
        "solve_rate": m.solve_rate,
        "verified_solve_rate": m.verified_solve_rate,
        "false_verification_rate": m.false_verification_rate,
        "false_disproof_rate": m.false_disproof_rate,
        "duplicate_action_rate": m.duplicate_action_rate,
        "blind_retry_rate": m.blind_retry_rate,
        "average_actions_per_solve": m.average_actions_per_solve,
        "budget_violations": m.budget_violations,
        "stop_correctness": m.stop_correctness,
        "terminal_state_correctness": m.terminal_state_correctness,
        "specialist_selection_accuracy": m.specialist_selection_accuracy,
        "per_case": {
            item.case_id: {
                "status": item.result.status.value,
                "verified_flag": item.result.verified_flag,
                "actions": len(item.result.actions),
            }
            for item in report.cases
        },
    }


@dataclass
class ABArm:
    name: str
    memory_root: Optional[Path]
    report: EvaluationReport

    def summary(self) -> Dict[str, object]:
        data = summarize_report(self.report)
        data["arm"] = self.name
        data["memory_root"] = str(self.memory_root) if self.memory_root else None
        return data


@dataclass
class ABComparison:
    control: ABArm
    treatment: ABArm
    deltas: Dict[str, float] = field(default_factory=dict)
    invariants: Dict[str, bool] = field(default_factory=dict)
    changed_cases: List[Dict[str, object]] = field(default_factory=list)
    verdict: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "control": self.control.summary(),
            "treatment": self.treatment.summary(),
            "deltas": self.deltas,
            "invariants": self.invariants,
            "changed_cases": self.changed_cases,
            "verdict": self.verdict,
        }


def _compare(control: ABArm, treatment: ABArm) -> ABComparison:
    c = summarize_report(control.report)
    t = summarize_report(treatment.report)

    def delta(key: str) -> float:
        return round(float(t[key]) - float(c[key]), 6)

    deltas = {
        "verified_solve_rate": delta("verified_solve_rate"),
        "solve_rate": delta("solve_rate"),
        "false_verification_rate": delta("false_verification_rate"),
        "false_disproof_rate": delta("false_disproof_rate"),
        "duplicate_action_rate": delta("duplicate_action_rate"),
        "average_actions_per_solve": delta("average_actions_per_solve"),
        "budget_violations": float(t["budget_violations"]) - float(c["budget_violations"]),
    }

    # Per-case status/verified changes.
    changed: List[Dict[str, object]] = []
    control_cases = c["per_case"]  # type: ignore[assignment]
    treatment_cases = t["per_case"]  # type: ignore[assignment]
    regressed_solved = False
    for case_id, before in control_cases.items():  # type: ignore[union-attr]
        after = treatment_cases[case_id]  # type: ignore[index]
        if before != after:
            changed.append({"case_id": case_id, "control": before, "treatment": after})
            if before["status"] == "SOLVED" and after["status"] != "SOLVED":
                regressed_solved = True

    invariants = {
        "no_increase_false_verification": t["false_verification_rate"] <= c["false_verification_rate"],
        "no_increase_false_disproof": (t["false_disproof_rate"] or 0.0) <= (c["false_disproof_rate"] or 0.0),
        "no_budget_violations": int(t["budget_violations"]) == 0,
        "no_solved_regression": not regressed_solved,
        "stop_correctness_maintained": t["stop_correctness"] >= c["stop_correctness"],
        "terminal_state_correctness_maintained": t["terminal_state_correctness"] >= c["terminal_state_correctness"],
    }

    verdict = _verdict(deltas, invariants)
    return ABComparison(
        control=control,
        treatment=treatment,
        deltas=deltas,
        invariants=invariants,
        changed_cases=changed,
        verdict=verdict,
    )


def _verdict(deltas: Dict[str, float], invariants: Dict[str, bool]) -> str:
    if not all(invariants.values()):
        return "REJECT: knowledge augmentation violated a control invariant"
    if deltas["verified_solve_rate"] > 0:
        return (
            "IMPROVEMENT: verified solve rate increased with no invariant violation "
            f"(+{deltas['verified_solve_rate']:.3f})"
        )
    if deltas["verified_solve_rate"] < 0:
        return "REGRESSION: verified solve rate decreased"
    # No change in verified solves; report any secondary (efficiency) movement honestly.
    if deltas["average_actions_per_solve"] < 0 or deltas["duplicate_action_rate"] < 0:
        return (
            "NEUTRAL-VERIFIED / SECONDARY-GAIN: verified solve rate unchanged; "
            "efficiency metrics improved; invariants preserved"
        )
    return (
        "NEUTRAL: verified solve rate unchanged and no invariant violated "
        "(knowledge neither helped nor harmed verified solving on this benchmark)"
    )


def run_ab_experiment(
    records: Sequence[KnowledgeRecord],
    work_root: Path,
    *,
    audit_root: Optional[Path] = None,
) -> ABComparison:
    """Run the control vs treatment arms and compare.

    ``records`` are the ingested knowledge records (external corpus). ``audit_root`` is the
    existing advisory corpus used by the control arm; if provided it is copied (never
    mutated) and augmented for the treatment arm.
    """
    work_root = Path(work_root)
    work_root.mkdir(parents=True, exist_ok=True)

    control_memory = audit_root if (audit_root and Path(audit_root).is_dir()) else None
    augmented_memory = build_augmented_memory(
        audit_root or work_root / "empty_audit", records, work_root / "augmented_memory"
    )

    control_cases = _wrap_cases(build_phase5_cases(work_root / "control")[0], control_memory)
    treatment_cases = _wrap_cases(
        build_phase5_cases(work_root / "treatment")[0], augmented_memory
    )

    control = ABArm("control", control_memory, EvaluationHarness().run(control_cases))
    treatment = ABArm("treatment", augmented_memory, EvaluationHarness().run(treatment_cases))
    return _compare(control, treatment)
