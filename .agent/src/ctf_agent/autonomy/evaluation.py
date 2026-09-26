from __future__ import annotations

import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Sequence, Tuple

from .contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    KnowledgeSource,
    SolveConstraints,
    SolveResult,
    SolveStatus,
)
from .solver import solve


class EvaluationKind(str, Enum):
    KNOWN = "KNOWN"
    NOVEL = "NOVEL"
    ADVERSARIAL = "ADVERSARIAL"
    HELD_OUT = "HELD_OUT"


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    kind: EvaluationKind
    challenge: ChallengeInput
    resources: Tuple[ChallengeResource, ...]
    environment_factory: Callable[[], EnvironmentConfig]
    constraints: SolveConstraints
    expected_status: SolveStatus
    expected_flag: Optional[str] = None
    expected_specialists: Tuple[str, ...] = ()
    known_correct_hypotheses: Tuple[str, ...] = ()
    expected_knowledge_sources: Tuple[KnowledgeSource, ...] = ()
    recovery_result_classes: Tuple[str, ...] = ()
    requires_dead_end_recovery: bool = False


@dataclass(frozen=True)
class EvaluationCaseResult:
    case_id: str
    kind: EvaluationKind
    result: SolveResult
    expected_status: SolveStatus
    expected_flag: Optional[str]
    status_correct: bool
    flag_correct: bool
    failures: Tuple[str, ...]


@dataclass(frozen=True)
class EvaluationMetrics:
    case_count: int
    solve_rate: float
    verified_solve_rate: float
    false_verification_rate: float
    false_disproof_rate: Optional[float]
    average_actions_per_solve: float
    median_actions_per_solve: float
    duplicate_action_rate: float
    blind_retry_rate: float
    dead_end_recovery_rate: Optional[float]
    environmental_failure_recovery_rate: Optional[float]
    tool_failure_recovery_rate: Optional[float]
    specialist_selection_accuracy: float
    useful_specialist_proposal_rate: float
    candidate_verification_success: float
    stop_correctness: float
    budget_violations: int
    average_reasoning_iterations: float
    average_time_to_verified_solution_ms: float
    average_resource_tool_cost: float
    terminal_state_correctness: float


@dataclass(frozen=True)
class EvaluationReport:
    cases: Tuple[EvaluationCaseResult, ...]
    metrics: EvaluationMetrics
    knowledge_attribution: Tuple[Tuple[str, Tuple[KnowledgeSource, ...]], ...]


class EvaluationHarness:
    """Runs labeled cases without supplying any action or hypothesis sequence to the solver."""

    def run(self, cases: Sequence[EvaluationCase]) -> EvaluationReport:
        results = []
        for case in cases:
            result = solve(
                case.challenge,
                case.resources,
                case.environment_factory(),
                case.constraints,
            )
            failures = _case_failures(case, result)
            results.append(
                EvaluationCaseResult(
                    case_id=case.case_id,
                    kind=case.kind,
                    result=result,
                    expected_status=case.expected_status,
                    expected_flag=case.expected_flag,
                    status_correct=result.status is case.expected_status,
                    flag_correct=result.verified_flag == case.expected_flag,
                    failures=failures,
                )
            )
        case_results = tuple(results)
        return EvaluationReport(
            cases=case_results,
            metrics=_metrics(tuple(cases), case_results),
            knowledge_attribution=tuple(
                (item.case_id, item.result.knowledge_sources) for item in case_results
            ),
        )


def _case_failures(case: EvaluationCase, result: SolveResult) -> Tuple[str, ...]:
    failures = []
    if result.status is not case.expected_status:
        failures.append(
            f"status expected {case.expected_status.value}, got {result.status.value}"
        )
    if result.verified_flag != case.expected_flag:
        failures.append(
            f"flag expected {case.expected_flag!r}, got {result.verified_flag!r}"
        )
    selected = {c.specialist for c in result.specialist_contributions}
    expected = set(case.expected_specialists)
    if expected and not expected.issubset(selected):
        failures.append(f"missing specialists: {tuple(sorted(expected - selected))}")
    for source in case.expected_knowledge_sources:
        if source not in result.knowledge_sources:
            failures.append(f"missing knowledge attribution: {source.value}")
    return tuple(failures)


def _metrics(
    cases: Tuple[EvaluationCase, ...], results: Tuple[EvaluationCaseResult, ...]
) -> EvaluationMetrics:
    n = len(results)
    if not n:
        return EvaluationMetrics(
            case_count=0,
            solve_rate=0.0,
            verified_solve_rate=0.0,
            false_verification_rate=0.0,
            false_disproof_rate=None,
            average_actions_per_solve=0.0,
            median_actions_per_solve=0.0,
            duplicate_action_rate=0.0,
            blind_retry_rate=0.0,
            dead_end_recovery_rate=None,
            environmental_failure_recovery_rate=None,
            tool_failure_recovery_rate=None,
            specialist_selection_accuracy=0.0,
            useful_specialist_proposal_rate=0.0,
            candidate_verification_success=0.0,
            stop_correctness=0.0,
            budget_violations=0,
            average_reasoning_iterations=0.0,
            average_time_to_verified_solution_ms=0.0,
            average_resource_tool_cost=0.0,
            terminal_state_correctness=0.0,
        )

    solved = [item for item in results if item.result.status is SolveStatus.SOLVED]
    verified = [
        item
        for item in solved
        if item.result.verified_flag and item.result.verification_evidence_ids
    ]
    actions = [len(item.result.actions) for item in solved]
    total_actions = sum(len(item.result.actions) for item in results)
    duplicate_proposals = sum(
        item.result.budget_usage.duplicate_proposals for item in results
    )
    blind_retries = sum(item.result.budget_usage.blind_retries for item in results)

    false_verified = sum(
        1
        for case, item in zip(cases, results)
        if item.result.status is SolveStatus.SOLVED
        and item.result.verified_flag != case.expected_flag
    )
    false_disproofs = sum(
        1
        for case, item in zip(cases, results)
        for hypothesis in item.result.key_hypotheses
        if hypothesis.status == "DISPROVEN"
        and hypothesis.hypothesis_id in case.known_correct_hypotheses
    )
    false_disproof_denominator = sum(
        len(case.known_correct_hypotheses) for case in cases
    )

    dead_end_episodes = [
        (case, item)
        for case, item in zip(cases, results)
        if case.requires_dead_end_recovery
    ]
    env_failure_episodes = [
        (case, item)
        for case, item in zip(cases, results)
        if "ENVIRONMENT_FAILURE" in case.recovery_result_classes
    ]
    tool_failure_episodes = [
        (case, item)
        for case, item in zip(cases, results)
        if "TOOL_FAILURE" in case.recovery_result_classes
    ]

    selection_scores = []
    useful_contributions = 0
    contribution_count = 0
    for case, item in zip(cases, results):
        selected = {c.specialist for c in item.result.specialist_contributions}
        expected = set(case.expected_specialists)
        if expected:
            union = selected | expected
            selection_scores.append(len(selected & expected) / len(union) if union else 1.0)
        evidence_hypotheses = {
            hypothesis_id
            for evidence in item.result.important_evidence
            for hypothesis_id in evidence.affected_hypotheses
        }
        for contribution in item.result.specialist_contributions:
            contribution_count += 1
            if any(hypothesis in evidence_hypotheses for hypothesis in contribution.hypotheses):
                useful_contributions += 1

    stop_correct = sum(
        1
        for case, item in zip(cases, results)
        if _stop_is_correct(case, item)
    )

    return EvaluationMetrics(
        case_count=n,
        solve_rate=len(solved) / n,
        verified_solve_rate=len(verified) / n,
        false_verification_rate=false_verified / n,
        false_disproof_rate=false_disproofs / false_disproof_denominator
        if false_disproof_denominator
        else None,
        average_actions_per_solve=statistics.mean(actions) if actions else 0.0,
        median_actions_per_solve=statistics.median(actions) if actions else 0.0,
        duplicate_action_rate=duplicate_proposals / (total_actions + duplicate_proposals)
        if total_actions + duplicate_proposals
        else 0.0,
        blind_retry_rate=blind_retries / (total_actions + blind_retries)
        if total_actions + blind_retries
        else 0.0,
        dead_end_recovery_rate=_dead_end_recovery_rate(dead_end_episodes),
        environmental_failure_recovery_rate=_failure_recovery_rate(
            env_failure_episodes, "ENVIRONMENT_FAILURE"
        ),
        tool_failure_recovery_rate=_failure_recovery_rate(
            tool_failure_episodes, "TOOL_FAILURE"
        ),
        specialist_selection_accuracy=statistics.mean(selection_scores)
        if selection_scores
        else 0.0,
        useful_specialist_proposal_rate=useful_contributions / contribution_count
        if contribution_count
        else 0.0,
        candidate_verification_success=len(solved)
        / sum(item.result.budget_usage.submissions for item in results)
        if sum(item.result.budget_usage.submissions for item in results)
        else 0.0,
        stop_correctness=stop_correct / n,
        budget_violations=sum(item.result.budget_usage.budget_violations for item in results),
        average_reasoning_iterations=statistics.mean(
            item.result.reasoning_iterations for item in results
        ),
        average_time_to_verified_solution_ms=statistics.mean(
            item.result.duration_ms for item in solved
        )
        if solved
        else 0.0,
        average_resource_tool_cost=statistics.mean(
            item.result.budget_usage.total_cost for item in results
        ),
        terminal_state_correctness=sum(item.status_correct for item in results) / n,
    )


def _stop_is_correct(case: EvaluationCase, item: EvaluationCaseResult) -> bool:
    actions = item.result.actions
    stop_indexes = [index for index, action in enumerate(actions) if action.decision == "STOP"]
    if item.result.status is SolveStatus.SOLVED:
        return (
            case.expected_status is SolveStatus.SOLVED
            and item.result.verified_flag == case.expected_flag
            and stop_indexes == [len(actions) - 1]
        )
    return (
        item.result.status is case.expected_status
        and item.result.verified_flag is None
        and not stop_indexes
    )


def _dead_end_recovery_rate(
    episodes: Sequence[Tuple[EvaluationCase, EvaluationCaseResult]],
) -> Optional[float]:
    if not episodes:
        return None
    recovered = 0
    for _case, item in episodes:
        disproved = next(
            (
                index
                for index, action in enumerate(item.result.actions)
                if action.impact == "DISPROVES"
            ),
            None,
        )
        if disproved is not None and any(
            action.decision == "STOP" for action in item.result.actions[disproved + 1 :]
        ):
            recovered += 1
    return recovered / len(episodes)


def _failure_recovery_rate(
    episodes: Sequence[Tuple[EvaluationCase, EvaluationCaseResult]], result_class: str
) -> Optional[float]:
    if not episodes:
        return None
    recovered = 0
    for _case, item in episodes:
        failure = next(
            (
                index
                for index, action in enumerate(item.result.actions)
                if action.result_class == result_class
            ),
            None,
        )
        if failure is not None and any(
            action.decision == "STOP"
            or action.impact in {"SUPPORTS", "DISPROVES", "WEAKENS"}
            for action in item.result.actions[failure + 1 :]
        ):
            recovered += 1
    return recovered / len(episodes)
