"""Knowledge-dependent evaluation harness.

Runs each benchmark case in control (no knowledge) and treatment (case knowledge) mode,
varying ONLY knowledge availability (via ``environment.memory_root``). Everything else —
challenge package, tools, environment, budgets, solver configuration — is identical.

A case is a *knowledge-attributable verified solve* only if it passes a strict gate:
    1. control did NOT verify-solve,
    2. treatment verify-solved through the kernel (verified flag + verification evidence +
       an authoritative verification method),
    3. treatment actually used a discriminating action that produced SUPPORTS evidence and
       drove the expected hypothesis to SUPPORTED/VERIFIED (not mere retrieval / not a bare
       submission), and
    4. treatment terminated correctly (final action is STOP).

Safety invariants are enforced on every case: no false verification, no false disproof, no
blind guessing, no budget violations, no duplicate-action regression, no stopping regression.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from ctf_agent import solve
from ctf_agent.autonomy.contracts import SolveResult, SolveStatus

from ctf_ingest.advisory_projection import write_external_memory
from .knowledge_dependent_benchmark import KnowledgeDependentCase, build_cases


def _run_arm(case: KnowledgeDependentCase, memory_root: Path) -> SolveResult:
    env = replace(case.environment_factory(), memory_root=memory_root)
    return solve(case.challenge, case.resources, env, case.constraints)


def _result_summary(result: SolveResult, expected_hypothesis: str) -> Dict[str, object]:
    hyp = next(
        (h for h in result.key_hypotheses if h.hypothesis_id == expected_hypothesis), None
    )
    return {
        "status": result.status.value,
        "verified_flag": result.verified_flag,
        "verification_method": result.final_verification_method,
        "actions": len(result.actions),
        "submissions": result.budget_usage.submissions,
        "blind_retries": result.budget_usage.blind_retries,
        "duplicate_proposals": result.budget_usage.duplicate_proposals,
        "budget_violations": result.budget_usage.budget_violations,
        "expected_hypothesis_status": hyp.status if hyp else None,
        "ends_with_stop": bool(result.actions) and result.actions[-1].decision == "STOP",
        "memory_references": sorted(
            {ref for c in result.specialist_contributions for ref in c.memory_references}
        ),
    }


def _is_verified_solve(result: SolveResult, expected_flag: Optional[str]) -> bool:
    return (
        result.status is SolveStatus.SOLVED
        and result.verified_flag == expected_flag
        and bool(result.verification_evidence_ids)
        and bool(result.final_verification_method)
    )


def _used_discriminating_evidence(result: SolveResult, expected_hypothesis: str) -> bool:
    supports_action = any(action.impact == "SUPPORTS" for action in result.actions)
    hyp = next(
        (h for h in result.key_hypotheses if h.hypothesis_id == expected_hypothesis), None
    )
    hyp_supported = hyp is not None and hyp.status in {"SUPPORTED", "VERIFIED"} and bool(
        hyp.supporting_evidence
    )
    return supports_action and hyp_supported


def _knowledge_attributable(
    case: KnowledgeDependentCase, control: SolveResult, treatment: SolveResult
) -> Tuple[bool, Tuple[str, ...]]:
    reasons: List[str] = []
    if _is_verified_solve(control, case.expected_flag):
        reasons.append("control already verify-solved (not knowledge-attributable)")
    if not _is_verified_solve(treatment, case.expected_flag):
        reasons.append("treatment did not kernel-verify the expected flag")
    if not _used_discriminating_evidence(treatment, case.expected_hypothesis):
        reasons.append("treatment lacked a discriminating action + supported hypothesis")
    if not (treatment.actions and treatment.actions[-1].decision == "STOP"):
        reasons.append("treatment did not terminate with STOP")
    attributable = not reasons
    return attributable, tuple(reasons)


def _safety_invariants(
    case: KnowledgeDependentCase, control: SolveResult, treatment: SolveResult
) -> Dict[str, bool]:
    def flag_ok(result: SolveResult) -> bool:
        # Either no flag, or exactly the expected flag. A decoy must never verify.
        if result.verified_flag is None:
            return True
        if case.decoy_flag and result.verified_flag == case.decoy_flag:
            return False
        return result.verified_flag == case.expected_flag

    def hyp_status(result: SolveResult) -> Optional[str]:
        hyp = next(
            (h for h in result.key_hypotheses if h.hypothesis_id == case.expected_hypothesis),
            None,
        )
        return hyp.status if hyp else None

    control_disproven = hyp_status(control) == "DISPROVEN"
    treatment_disproven = hyp_status(treatment) == "DISPROVEN"

    return {
        "no_false_verification": flag_ok(control) and flag_ok(treatment),
        "no_false_disproof": treatment_disproven == control_disproven or not treatment_disproven,
        "no_blind_guessing": control.budget_usage.blind_retries == 0
        and treatment.budget_usage.blind_retries == 0,
        "no_budget_violations": control.budget_usage.budget_violations == 0
        and treatment.budget_usage.budget_violations == 0,
        "no_duplicate_action_regression": treatment.budget_usage.duplicate_proposals
        <= control.budget_usage.duplicate_proposals,
        "no_extra_submissions": treatment.budget_usage.submissions
        <= max(control.budget_usage.submissions, 1),
        "no_stopping_regression": _stopping_ok(control) and _stopping_ok(treatment),
    }


def _stopping_ok(result: SolveResult) -> bool:
    stops = [i for i, a in enumerate(result.actions) if a.decision == "STOP"]
    if result.status is SolveStatus.SOLVED:
        return stops == [len(result.actions) - 1]
    return not stops


@dataclass(frozen=True)
class CaseOutcome:
    case_id: str
    kind: str
    baseline_should_solve: bool
    control: Dict[str, object]
    treatment: Dict[str, object]
    knowledge_attributable: bool
    attribution_reasons: Tuple[str, ...]
    safety: Dict[str, bool]

    def to_dict(self) -> Dict[str, object]:
        return {
            "case_id": self.case_id,
            "kind": self.kind,
            "baseline_should_solve": self.baseline_should_solve,
            "control": self.control,
            "treatment": self.treatment,
            "knowledge_attributable_verified_solve": self.knowledge_attributable,
            "attribution_reasons": list(self.attribution_reasons),
            "safety_invariants": self.safety,
        }


@dataclass
class KnowledgeDependentReport:
    outcomes: List[CaseOutcome] = field(default_factory=list)

    @property
    def knowledge_attributable_verified_solves(self) -> int:
        return sum(1 for o in self.outcomes if o.knowledge_attributable)

    @property
    def all_safety_invariants_preserved(self) -> bool:
        return all(all(o.safety.values()) for o in self.outcomes)

    def verdict(self) -> str:
        if not self.all_safety_invariants_preserved:
            return "REJECT: a safety invariant was violated under knowledge augmentation"
        n = self.knowledge_attributable_verified_solves
        if n > 0:
            return (
                f"KNOWLEDGE-POSITIVE: {n} knowledge-attributable verified solve(s) with all "
                "safety invariants preserved"
            )
        return (
            "KNOWLEDGE-SAFE / NON-CONTRIBUTING: 0 knowledge-attributable verified solves; all "
            "safety invariants preserved. Advisory knowledge did not convert into a verified "
            "solve in the frozen architecture (advisory memory is observability-only)."
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "case_count": len(self.outcomes),
            "knowledge_attributable_verified_solves": self.knowledge_attributable_verified_solves,
            "all_safety_invariants_preserved": self.all_safety_invariants_preserved,
            "verdict": self.verdict(),
            "cases": [o.to_dict() for o in self.outcomes],
        }


def run_knowledge_dependent_experiment(
    work_root: Path, cases: Optional[Sequence[KnowledgeDependentCase]] = None
) -> KnowledgeDependentReport:
    work_root = Path(work_root)
    work_root.mkdir(parents=True, exist_ok=True)
    if cases is None:
        cases = build_cases(work_root / "bench")

    report = KnowledgeDependentReport()
    for case in cases:
        control_mem = write_external_memory(case.control_records, work_root / f"{case.case_id}-control-mem")
        treatment_mem = write_external_memory(
            case.treatment_records, work_root / f"{case.case_id}-treatment-mem"
        )
        control = _run_arm(case, control_mem)
        treatment = _run_arm(case, treatment_mem)

        attributable, reasons = _knowledge_attributable(case, control, treatment)
        report.outcomes.append(
            CaseOutcome(
                case_id=case.case_id,
                kind=case.kind,
                baseline_should_solve=case.baseline_should_solve,
                control=_result_summary(control, case.expected_hypothesis),
                treatment=_result_summary(treatment, case.expected_hypothesis),
                knowledge_attributable=attributable,
                attribution_reasons=reasons,
                safety=_safety_invariants(case, control, treatment),
            )
        )
    return report
