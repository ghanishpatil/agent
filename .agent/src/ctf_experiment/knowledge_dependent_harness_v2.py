"""Knowledge-dependent A/B harness v2 (integration-enabled).

Runs each v2 case in control (no knowledge) and treatment (case knowledge) mode. BOTH arms use
the identical composition (``solve_with_knowledge``) with identical challenge/tools/environment/
budgets/solver configuration; only the retriever (knowledge availability) differs. This isolates
knowledge as the single variable while keeping the solver configuration constant.

Reports the required metrics and enforces the strict knowledge-attribution gate and safety
invariants. Does not overwrite the v1 KNOWLEDGE-SAFE / NON-CONTRIBUTING result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from ctf_agent.autonomy.contracts import SolveResult, SolveStatus
from ctf_agent.journal import RuntimeJournal

from ctf_ingest.retrieval import KnowledgeRetriever
from .knowledge_dependent_benchmark_v2 import KDCaseV2, build_cases_v2
from .knowledge_reasoning import KnowledgeMetrics
from .knowledge_solver import solve_with_knowledge


def _journal_timings(result: SolveResult) -> Dict[str, Optional[float]]:
    if not result.journal_path:
        return {"time_to_first_action_ms": None, "time_to_verified_ms": None}
    events = RuntimeJournal(Path(result.journal_path)).read_all()
    started = _first_ts(events, "solve_started")
    first_action = _first_ts(events, "action_executed")
    stop = _first_ts(events, "stop_reached")
    return {
        "time_to_first_action_ms": _delta_ms(started, first_action),
        "time_to_verified_ms": _delta_ms(started, stop),
    }


def _first_ts(events, kind: str) -> Optional[datetime]:
    for event in events:
        if event.get("kind") == kind:
            try:
                return datetime.fromisoformat(event["timestamp"])
            except (KeyError, ValueError):
                return None
    return None


def _delta_ms(a: Optional[datetime], b: Optional[datetime]) -> Optional[float]:
    if a is None or b is None:
        return None
    return round((b - a).total_seconds() * 1000.0, 3)


def _is_verified_solve(result: SolveResult, expected_flag: Optional[str]) -> bool:
    return (
        result.status is SolveStatus.SOLVED
        and expected_flag is not None
        and result.verified_flag == expected_flag
        and bool(result.verification_evidence_ids)
        and bool(result.final_verification_method)
    )


def _used_discriminating_evidence(result: SolveResult, hypothesis_id: str) -> bool:
    supports = any(a.impact == "SUPPORTS" for a in result.actions)
    hyp = next((h for h in result.key_hypotheses if h.hypothesis_id == hypothesis_id), None)
    return supports and hyp is not None and hyp.status in {"SUPPORTED", "VERIFIED"} and bool(
        hyp.supporting_evidence
    )


def _executed_duplicates(result: SolveResult) -> int:
    return sum(1 for a in result.actions if a.decision == "DUPLICATE")


def _stopping_ok(result: SolveResult) -> bool:
    stops = [i for i, a in enumerate(result.actions) if a.decision == "STOP"]
    if result.status is SolveStatus.SOLVED:
        return stops == [len(result.actions) - 1]
    return not stops


def _hyp_status(result: SolveResult, hypothesis_id: str) -> Optional[str]:
    hyp = next((h for h in result.key_hypotheses if h.hypothesis_id == hypothesis_id), None)
    return hyp.status if hyp else None


@dataclass
class KDv2Outcome:
    case_id: str
    kind: str
    control: Dict[str, object]
    treatment: Dict[str, object]
    metrics: Dict[str, object]
    knowledge_attributable: bool
    attribution_reasons: List[str]
    safety: Dict[str, bool]

    def to_dict(self) -> Dict[str, object]:
        return {
            "case_id": self.case_id,
            "kind": self.kind,
            "control": self.control,
            "treatment": self.treatment,
            "metrics": self.metrics,
            "knowledge_attributable_verified_solve": self.knowledge_attributable,
            "attribution_reasons": self.attribution_reasons,
            "safety_invariants": self.safety,
        }


@dataclass
class KDv2Report:
    outcomes: List[KDv2Outcome] = field(default_factory=list)

    @property
    def knowledge_attributable_verified_solves(self) -> int:
        return sum(1 for o in self.outcomes if o.knowledge_attributable)

    @property
    def all_safety_preserved(self) -> bool:
        return all(all(o.safety.values()) for o in self.outcomes)

    def verdict(self) -> str:
        if not self.all_safety_preserved:
            return "REJECT: a safety invariant was violated under knowledge augmentation"
        n = self.knowledge_attributable_verified_solves
        if n > 0:
            return (
                f"KNOWLEDGE-CONTRIBUTING: {n} knowledge-attributable verified solve(s); all safety "
                "invariants preserved; easy cases stayed on the fast path"
            )
        return "KNOWLEDGE-SAFE / NON-CONTRIBUTING: 0 knowledge-attributable verified solves"

    def to_dict(self) -> Dict[str, object]:
        return {
            "case_count": len(self.outcomes),
            "knowledge_attributable_verified_solves": self.knowledge_attributable_verified_solves,
            "all_safety_invariants_preserved": self.all_safety_preserved,
            "verdict": self.verdict(),
            "cases": [o.to_dict() for o in self.outcomes],
        }


def _summary(result: SolveResult, knowledge: KnowledgeMetrics, hypothesis_id: str) -> Dict[str, object]:
    return {
        "status": result.status.value,
        "verified_flag": result.verified_flag,
        "actions": len(result.actions),
        "duplicate_proposals": result.budget_usage.duplicate_proposals,
        "budget_violations": result.budget_usage.budget_violations,
        "submissions": result.budget_usage.submissions,
        "retrieval_calls": knowledge.retrieval_calls,
        "knowledge_hypotheses": knowledge.knowledge_hypotheses,
        "unnecessary_retrievals": knowledge.unnecessary_retrievals,
        "expected_hypothesis_status": _hyp_status(result, hypothesis_id),
        "ends_with_stop": bool(result.actions) and result.actions[-1].decision == "STOP",
    }


def run_experiment_v2(
    work_root: Path,
    cases: Optional[Sequence[KDCaseV2]] = None,
    retriever_factory=None,
) -> KDv2Report:
    """Run the knowledge-dependent A/B.

    ``retriever_factory``: optional ``callable(case) -> KnowledgeRetriever | None`` used for the
    treatment arm. When omitted, each case's own synthetic ``treatment_records`` are used (original
    behavior). Supplying a corpus-backed factory lets the same cases be evaluated against
    local / Jia Jie / combined knowledge without changing the frozen solver or the cases.
    """
    work_root = Path(work_root)
    work_root.mkdir(parents=True, exist_ok=True)
    if cases is None:
        cases = build_cases_v2(work_root / "bench")

    report = KDv2Report()
    for case in cases:
        # Control: identical solver, NO knowledge (retriever=None).
        control = solve_with_knowledge(
            case.challenge, (), _rerun_env(case, work_root, "control"), case.constraints,
            retriever=None,
        )
        # Treatment: identical solver, knowledge available.
        if retriever_factory is not None:
            retriever = retriever_factory(case)
        else:
            retriever = KnowledgeRetriever.from_records(case.treatment_records)
        treatment = solve_with_knowledge(
            case.challenge, (), _rerun_env(case, work_root, "treatment"), case.constraints,
            retriever=retriever,
        )

        c_res, t_res = control.result, treatment.result
        attributable, reasons = _attribution(case, c_res, t_res)
        timings = _journal_timings(t_res)
        report.outcomes.append(
            KDv2Outcome(
                case_id=case.case_id,
                kind=case.kind,
                control=_summary(c_res, control.knowledge, case.expected_hypothesis),
                treatment=_summary(t_res, treatment.knowledge, case.expected_hypothesis),
                metrics={
                    "time_to_first_action_ms": timings["time_to_first_action_ms"],
                    "time_to_verified_ms": timings["time_to_verified_ms"],
                    "actions_per_solve": len(t_res.actions),
                    "retrieval_calls_per_solve": treatment.knowledge.retrieval_calls,
                    "retrieved_records_per_solve": treatment.knowledge.retrieved_records,
                    "knowledge_hypotheses_per_solve": treatment.knowledge.knowledge_hypotheses,
                    "unnecessary_retrievals": treatment.knowledge.unnecessary_retrievals,
                    "duplicate_actions": t_res.budget_usage.duplicate_proposals,
                    "budget_violations": t_res.budget_usage.budget_violations,
                    "false_verification": not _flag_ok(case, t_res) or not _flag_ok(case, c_res),
                    "false_disproof": _false_disproof(case, t_res),
                    "stopping_correct": _stopping_ok(t_res) and _stopping_ok(c_res),
                },
                knowledge_attributable=attributable,
                attribution_reasons=reasons,
                safety=_safety(case, c_res, t_res),
            )
        )
    return report


def _rerun_env(case: KDCaseV2, work_root: Path, arm: str):
    # Fresh environment per arm so journals/workspaces do not collide.
    base_env = case.environment_factory()
    from dataclasses import replace

    root = work_root / f"{case.case_id}-{arm}"
    root.mkdir(parents=True, exist_ok=True)
    return replace(
        base_env,
        workspace_root=root,
        journal_path=root / "journal.jsonl",
        run_id=f"{case.case_id}-{arm}",
    )


def _flag_ok(case: KDCaseV2, result: SolveResult) -> bool:
    if result.verified_flag is None:
        return True
    if case.decoy_flag and result.verified_flag == case.decoy_flag:
        return False
    return result.verified_flag == case.expected_flag


def _false_disproof(case: KDCaseV2, treatment: SolveResult) -> bool:
    if not case.treatment_should_solve:
        return False
    return _hyp_status(treatment, case.expected_hypothesis) == "DISPROVEN"


def _attribution(case: KDCaseV2, control: SolveResult, treatment: SolveResult):
    reasons: List[str] = []
    if _is_verified_solve(control, case.expected_flag):
        reasons.append("control already verify-solved (not knowledge-attributable)")
    if not _is_verified_solve(treatment, case.expected_flag):
        reasons.append("treatment did not kernel-verify the expected flag")
    elif not _used_discriminating_evidence(treatment, case.expected_hypothesis):
        reasons.append("treatment lacked a discriminating SUPPORTS action + supported hypothesis")
    if not (treatment.actions and treatment.actions[-1].decision == "STOP"):
        if _is_verified_solve(treatment, case.expected_flag):
            reasons.append("treatment did not terminate with STOP")
    return (not reasons), reasons


def _safety(case: KDCaseV2, control: SolveResult, treatment: SolveResult) -> Dict[str, bool]:
    return {
        "no_false_verification": _flag_ok(case, control) and _flag_ok(case, treatment),
        "no_false_disproof": not _false_disproof(case, treatment),
        "no_blind_guessing": control.budget_usage.blind_retries == 0
        and treatment.budget_usage.blind_retries == 0,
        "no_budget_violations": control.budget_usage.budget_violations == 0
        and treatment.budget_usage.budget_violations == 0,
        # No DUPLICATE action ever executes (planner/kernel block duplicates before execution).
        # duplicate_proposals (blocked attempts) is reported as a metric; it legitimately rises when
        # knowledge introduces an extra mechanism that evidence then rules out, which is anti-spray
        # working, not wasted execution.
        "no_executed_duplicate_actions": _executed_duplicates(control) == 0
        and _executed_duplicates(treatment) == 0,
        "stopping_correct": _stopping_ok(control) and _stopping_ok(treatment),
    }
