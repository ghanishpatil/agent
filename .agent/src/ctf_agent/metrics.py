from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from .kernel import PipelineResult
from .loop import LoopOutcome, LoopResult
from .models import ControlDecision, HypothesisImpact, HypothesisStatus, VerificationStatus


@dataclass(frozen=True)
class SingleRunMetrics:
    """Metrics derivable from exactly one ``LoopResult`` -- no external ground truth needed.

    Everything here is computed by reading ``LoopResult.pipeline_results`` (what the kernel
    actually did), never from separately-kept counters that could drift from what really happened.
    """

    outcome: LoopOutcome
    actions_taken: int
    verified: bool
    actions_to_solution: Optional[int]
    duplicate_action_count: int
    duplicate_action_rate: float
    unnecessary_action_count: int
    unnecessary_action_rate: float
    verification_latency_actions: Optional[int]
    blocked_branch_count: int
    unresolved_branch_count: int
    state_consistency_violations: Tuple[str, ...]

    @property
    def state_is_consistent(self) -> bool:
        return not self.state_consistency_violations


def evaluate_single_run(result: LoopResult) -> SingleRunMetrics:
    """Compute metrics for one completed (or terminated) ``ReasoningLoop.run()`` call."""
    pipeline_results = result.pipeline_results
    total = len(pipeline_results)

    duplicate_count = sum(
        1 for pr in pipeline_results if pr.decision is ControlDecision.DUPLICATE
    )
    # "Unnecessary" here means: the action executed (wasn't a duplicate/STOP short-circuit), but
    # produced neither support nor contradiction nor even an unresolved/blocked signal -- i.e. it
    # told the agent nothing new about any hypothesis. A cheap baseline probe that legitimately
    # comes back empty still counts as informative if it was the first test of a hypothesis; this
    # metric flags NO_IMPACT results specifically because those are exactly the ones that spent an
    # action budget without moving any hypothesis's evidence state at all.
    unnecessary_count = sum(
        1
        for pr in pipeline_results
        if pr.decision is not ControlDecision.DUPLICATE
        and pr.impact is HypothesisImpact.NO_IMPACT
        and pr.verification is None
    )

    verified = result.outcome is LoopOutcome.VERIFIED
    actions_to_solution = result.actions_taken if verified else None

    verification_latency_actions = _verification_latency(pipeline_results) if verified else None

    blocked_branch_count = sum(
        1 for view in result.context.hypothesis_views() if view.hypothesis.status is HypothesisStatus.UNRESOLVED
        and result.context.board.meta(view.hypothesis.hypothesis_id).priority <= 0
    )
    unresolved_branch_count = sum(
        1
        for view in result.context.hypothesis_views()
        if view.hypothesis.status is HypothesisStatus.UNRESOLVED
    )

    violations = _state_consistency_violations(pipeline_results)

    return SingleRunMetrics(
        outcome=result.outcome,
        actions_taken=total,
        verified=verified,
        actions_to_solution=actions_to_solution,
        duplicate_action_count=duplicate_count,
        duplicate_action_rate=_safe_rate(duplicate_count, total),
        unnecessary_action_count=unnecessary_count,
        unnecessary_action_rate=_safe_rate(unnecessary_count, total),
        verification_latency_actions=verification_latency_actions,
        blocked_branch_count=blocked_branch_count,
        unresolved_branch_count=unresolved_branch_count,
        state_consistency_violations=violations,
    )


def _verification_latency(pipeline_results: Tuple[PipelineResult, ...]) -> Optional[int]:
    """Actions between the first piece of CURRENT evidence recorded and the STOP decision.

    A latency of 0 means the very first evidence-producing action was also the one that verified.
    Returns None if no STOP was ever reached (caller already guards on ``verified``).
    """
    first_evidence_index = None
    stop_index = None
    for index, pr in enumerate(pipeline_results):
        if first_evidence_index is None and pr.evidence is not None:
            first_evidence_index = index
        if pr.decision is ControlDecision.STOP or (
            pr.verification is not None
            and pr.verification.candidate.verification_status is VerificationStatus.VERIFIED
        ):
            stop_index = index
            break
    if stop_index is None:
        return None
    if first_evidence_index is None:
        return stop_index
    return stop_index - first_evidence_index


def _state_consistency_violations(pipeline_results: Tuple[PipelineResult, ...]) -> Tuple[str, ...]:
    """Sanity checks that must always hold if the kernel boundary was respected end to end.

    These are architectural invariants, not run-quality judgments: if any of them ever fires it
    indicates a real bug in the loop/kernel interaction, not merely a "bad" run.
    """
    violations: list[str] = []
    seen_stop = False
    for index, pr in enumerate(pipeline_results):
        if seen_stop and (pr.evidence is not None or pr.observation is not None):
            violations.append(
                f"pipeline_results[{index}] produced evidence/observation after an earlier STOP"
            )
        if pr.decision is ControlDecision.STOP:
            seen_stop = True
        if pr.verification is not None and pr.verification.candidate.verification_status is (
            VerificationStatus.VERIFIED
        ) and pr.decision is not ControlDecision.STOP:
            violations.append(
                f"pipeline_results[{index}] has a VERIFIED candidate but decision is not STOP"
            )
    return tuple(violations)


def _safe_rate(count: int, total: int) -> float:
    return count / total if total else 0.0


@dataclass(frozen=True)
class AggregateMetrics:
    """Rates that only make sense across multiple runs (e.g. the 3 synthetic scenarios)."""

    run_count: int
    successful_termination_rate: float
    false_verification_rate: float
    false_disproof_rate: float
    average_duplicate_action_rate: float
    average_unnecessary_action_rate: float
    average_actions_to_solution: Optional[float]


def evaluate_runs(
    results: Sequence[LoopResult],
    *,
    known_correct_flags: Sequence[Optional[str]] | None = None,
    known_wrongly_disproven_hypothesis_ids: Sequence[Tuple[str, ...]] | None = None,
) -> AggregateMetrics:
    """Aggregate metrics across several runs (e.g. the 3 synthetic end-to-end scenarios).

    ``known_correct_flags[i]`` / ``known_wrongly_disproven_hypothesis_ids[i]`` are optional
    external ground truth for run ``i`` (what a human grader independently knows to be true) --
    this module never invents ground truth on its own. Without ground truth, false_verification /
    false_disproof are reported as 0.0 (nothing observed to contradict a VERIFIED/DISPROVEN
    outcome), which is the honest default rather than a guess.
    """
    run_count = len(results)
    if run_count == 0:
        return AggregateMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, None)

    per_run = [evaluate_single_run(result) for result in results]

    successful = sum(1 for metrics in per_run if metrics.verified)
    successful_termination_rate = successful / run_count

    false_verification_count = 0
    if known_correct_flags is not None:
        for result, expected in zip(results, known_correct_flags):
            if expected is None:
                continue
            for pr in result.pipeline_results:
                if (
                    pr.verification is not None
                    and pr.verification.candidate.verification_status is VerificationStatus.VERIFIED
                    and pr.verification.candidate.value != expected
                ):
                    false_verification_count += 1
    false_verification_rate = _safe_rate(false_verification_count, run_count)

    false_disproof_count = 0
    if known_wrongly_disproven_hypothesis_ids is not None:
        for result, wrongly_disproven_ids in zip(results, known_wrongly_disproven_hypothesis_ids):
            for view in result.context.hypothesis_views():
                if (
                    view.hypothesis.status is HypothesisStatus.DISPROVEN
                    and view.hypothesis.hypothesis_id in wrongly_disproven_ids
                ):
                    false_disproof_count += 1
    false_disproof_rate = _safe_rate(false_disproof_count, run_count)

    average_duplicate_action_rate = sum(m.duplicate_action_rate for m in per_run) / run_count
    average_unnecessary_action_rate = sum(m.unnecessary_action_rate for m in per_run) / run_count

    solved_action_counts = [m.actions_to_solution for m in per_run if m.actions_to_solution is not None]
    average_actions_to_solution = (
        sum(solved_action_counts) / len(solved_action_counts) if solved_action_counts else None
    )

    return AggregateMetrics(
        run_count=run_count,
        successful_termination_rate=successful_termination_rate,
        false_verification_rate=false_verification_rate,
        false_disproof_rate=false_disproof_rate,
        average_duplicate_action_rate=average_duplicate_action_rate,
        average_unnecessary_action_rate=average_unnecessary_action_rate,
        average_actions_to_solution=average_actions_to_solution,
    )
