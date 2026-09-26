from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from ..hypothesis_engine import HypothesisBoard
from ..kernel import PipelineResult
from ..loop import LoopOutcome, LoopResult
from ..models import ControlDecision, HypothesisImpact, HypothesisStatus, VerificationStatus
from .selection import SpecialistSelection


_SPECIALIST_PREFIXES = ("web", "crypto", "reverse", "forensics", "pwn")


def _specialist_of(hypothesis_id: str) -> str:
    return hypothesis_id.split("-", 1)[0] if "-" in hypothesis_id else ""


@dataclass(frozen=True)
class SpecialistRunMetrics:
    """Section-18 quality metrics for one specialist-driven run, derived from the run itself.

    Everything is computed from the ``LoopResult`` + final board + the brain's ``SpecialistSelection``
    -- never from separately-kept counters. Metrics needing external ground truth
    (false disproof/verification) report 0 unless that ground truth is supplied, which is the honest
    default rather than a guess.
    """

    outcome: LoopOutcome
    verified: bool
    actions_to_solution: Optional[int]
    selected_specialists: Tuple[str, ...]
    proposed_hypotheses: int
    evidence_backed_hypotheses: int
    useful_hypothesis_rate: float
    disproven_hypotheses: int
    duplicate_action_count: int
    duplicate_action_rate: float
    unnecessary_action_count: int
    unnecessary_action_rate: float
    discriminating_tests_run: int
    recovered_from_wrong_path: bool
    unnecessary_specialist_invocations: int
    false_disproof_count: int
    false_verification_count: int

    @property
    def clean(self) -> bool:
        """A run is 'clean' if it made no false disproof and no false verification."""
        return self.false_disproof_count == 0 and self.false_verification_count == 0


def _evidence_backed(hypothesis) -> bool:
    return (
        hypothesis.status is not HypothesisStatus.OPEN
        or bool(hypothesis.supporting_evidence)
        or bool(hypothesis.contradicting_evidence)
        or bool(hypothesis.unresolved_evidence)
    )


def evaluate_specialist_run(
    result: LoopResult,
    board: HypothesisBoard,
    selection: Optional[SpecialistSelection],
    *,
    expected_flag: Optional[str] = None,
    known_correct_hypotheses: Tuple[str, ...] = (),
) -> SpecialistRunMetrics:
    pipeline = result.pipeline_results
    total = len(pipeline)

    duplicate_count = sum(1 for pr in pipeline if pr.decision is ControlDecision.DUPLICATE)
    unnecessary_count = sum(
        1
        for pr in pipeline
        if pr.decision is not ControlDecision.DUPLICATE
        and pr.impact is HypothesisImpact.NO_IMPACT
        and pr.verification is None
    )
    discriminating = sum(
        1
        for pr in pipeline
        if pr.impact in {HypothesisImpact.SUPPORTS, HypothesisImpact.DISPROVES, HypothesisImpact.WEAKENS}
    )

    hypotheses = board.all_hypotheses()
    proposed = len(hypotheses)
    evidence_backed = sum(1 for h in hypotheses if _evidence_backed(h))
    disproven = sum(1 for h in hypotheses if h.status is HypothesisStatus.DISPROVEN)

    verified = result.outcome is LoopOutcome.VERIFIED
    recovered = verified and disproven > 0

    selected_names = (
        tuple(s.name for s in selection.selected) if selection is not None else ()
    )
    # A selected specialist is "unnecessary" if none of its (prefixed) hypotheses ever gained
    # evidence -- it was consulted but contributed nothing testable.
    unnecessary_specialists = 0
    for name in selected_names:
        contributed = any(
            _specialist_of(h.hypothesis_id) == name and _evidence_backed(h) for h in hypotheses
        )
        if not contributed:
            unnecessary_specialists += 1

    false_disproof = sum(
        1
        for h in hypotheses
        if h.status is HypothesisStatus.DISPROVEN and h.hypothesis_id in known_correct_hypotheses
    )
    false_verification = 0
    if expected_flag is not None:
        for pr in pipeline:
            if (
                pr.verification is not None
                and pr.verification.candidate.verification_status is VerificationStatus.VERIFIED
                and pr.verification.candidate.value != expected_flag
            ):
                false_verification += 1

    return SpecialistRunMetrics(
        outcome=result.outcome,
        verified=verified,
        actions_to_solution=result.actions_taken if verified else None,
        selected_specialists=selected_names,
        proposed_hypotheses=proposed,
        evidence_backed_hypotheses=evidence_backed,
        useful_hypothesis_rate=(evidence_backed / proposed) if proposed else 0.0,
        disproven_hypotheses=disproven,
        duplicate_action_count=duplicate_count,
        duplicate_action_rate=(duplicate_count / total) if total else 0.0,
        unnecessary_action_count=unnecessary_count,
        unnecessary_action_rate=(unnecessary_count / total) if total else 0.0,
        discriminating_tests_run=discriminating,
        recovered_from_wrong_path=recovered,
        unnecessary_specialist_invocations=unnecessary_specialists,
        false_disproof_count=false_disproof,
        false_verification_count=false_verification,
    )


@dataclass(frozen=True)
class SpecialistAggregateMetrics:
    run_count: int
    successful_termination_rate: float
    false_verification_rate: float
    false_disproof_rate: float
    average_useful_hypothesis_rate: float
    average_duplicate_action_rate: float
    average_actions_to_solution: Optional[float]
    recovered_from_wrong_path_rate: float


def evaluate_specialist_runs(
    runs: Sequence[SpecialistRunMetrics],
) -> SpecialistAggregateMetrics:
    n = len(runs)
    if n == 0:
        return SpecialistAggregateMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, None, 0.0)
    verified = [m for m in runs if m.verified]
    solved = [m.actions_to_solution for m in verified if m.actions_to_solution is not None]
    return SpecialistAggregateMetrics(
        run_count=n,
        successful_termination_rate=len(verified) / n,
        false_verification_rate=sum(m.false_verification_count for m in runs) / n,
        false_disproof_rate=sum(m.false_disproof_count for m in runs) / n,
        average_useful_hypothesis_rate=sum(m.useful_hypothesis_rate for m in runs) / n,
        average_duplicate_action_rate=sum(m.duplicate_action_rate for m in runs) / n,
        average_actions_to_solution=(sum(solved) / len(solved)) if solved else None,
        recovered_from_wrong_path_rate=sum(1 for m in runs if m.recovered_from_wrong_path) / n,
    )
