from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .classifier import classify_result
from .evidence import EvidenceManager
from .impact import determine_impact
from .models import (
    ControlDecision,
    EnvironmentState,
    ExecutionResult,
    FlagCandidate,
    HypothesisImpact,
    ImpactContext,
    Observation,
    RelevantState,
    ResultClass,
    VerificationPolicy,
)
from .verification import FlagAttemptRegistry, VerificationController


@dataclass(frozen=True)
class HistoricalRegressionResult:
    failure_id: str
    passed: bool
    actual_result_class: ResultClass
    actual_impact: HypothesisImpact
    actual_control: str


def _execution(data: dict[str, Any]) -> ExecutionResult:
    return ExecutionResult(**data)


def _record_current(
    manager: EvidenceManager,
    execution: ExecutionResult,
    impact: HypothesisImpact,
):
    observation = Observation(
        f"obs-{execution.action_id}",
        execution.action_id,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        f"historical-replay:{execution.action_id}",
        execution,
    )
    return manager.record_current(
        observation=observation,
        classification=classify_result(execution),
        impact=impact,
        affected_hypotheses=("h",),
    )


def _run_verification(case: dict[str, Any]):
    execution = _execution(case["execution"])
    classification = classify_result(execution)
    impact = determine_impact(classification.result_class, ImpactContext("h"))
    manager = EvidenceManager()
    evidence = _record_current(manager, execution, impact)
    policy_data = {
        key: tuple(value) for key, value in case.get("policy", {}).items()
    }
    controller = VerificationController(manager, VerificationPolicy(**policy_data))
    decision = controller.evaluate(
        FlagCandidate(case["candidate"], case["source"]),
        (evidence.evidence_id,),
    )
    control = (
        f"{decision.candidate.verification_status.value}:{decision.decision.value}"
    )
    return classification.result_class, impact, control


def _run_anti_spray(case: dict[str, Any]):
    execution = _execution(case["execution"])
    classification = classify_result(execution)
    impact = determine_impact(classification.result_class, ImpactContext("h"))
    manager = EvidenceManager()
    evidence = _record_current(manager, execution, impact)
    registry = FlagAttemptRegistry(manager)
    state = RelevantState(EnvironmentState("env", (execution.tool,)), "guest", "s1", "c1")
    candidate = FlagCandidate(case["candidate"], case["source"])
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    registry.check_and_record(candidate, "ctfd", (evidence.evidence_id,), state, now)
    duplicate = registry.check_and_record(
        candidate, "ctfd", (evidence.evidence_id,), state, now
    )
    return classification.result_class, impact, duplicate.value


def _run_case(case: dict[str, Any]):
    kind = case["kind"]
    if kind == "verification":
        return _run_verification(case)
    if kind == "anti_spray":
        return _run_anti_spray(case)
    if kind == "no_observation":
        impact = determine_impact(
            ResultClass.AMBIGUOUS,
            ImpactContext("h", observation_available=False),
        )
        return ResultClass.AMBIGUOUS, impact, impact.value
    if kind == "classification":
        execution = _execution(case["execution"])
        classification = classify_result(execution)
        context = ImpactContext(**case["impact_context"])
        impact = determine_impact(classification.result_class, context)
        return classification.result_class, impact, impact.value
    raise ValueError(f"unsupported historical replay kind: {kind}")


def run_historical_regression(
    failures_path: Path,
    expectations_path: Path,
    replays_path: Path,
) -> tuple[HistoricalRegressionResult, ...]:
    failure_ids = [
        json.loads(line)["id"]
        for line in failures_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
    replays = json.loads(replays_path.read_text(encoding="utf-8"))
    results: list[HistoricalRegressionResult] = []
    for failure_id in failure_ids:
        actual_class, actual_impact, actual_control = _run_case(replays[failure_id])
        expected = expectations[failure_id]
        passed = (
            actual_class.value == expected["expected_result_class"]
            and actual_impact.value == expected["expected_impact"]
            and actual_control == expected["expected_control"]
        )
        results.append(
            HistoricalRegressionResult(
                failure_id, passed, actual_class, actual_impact, actual_control
            )
        )
    return tuple(results)


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def render_historical_regression_report(
    failures_path: Path,
    expectations_path: Path,
    results: tuple[HistoricalRegressionResult, ...],
) -> str:
    failures = {
        record["id"]: record
        for record in (
            json.loads(line)
            for line in failures_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
    passed = sum(result.passed for result in results)
    lines = [
        "# Historical Failure Regression",
        "",
        f"**Result: {passed}/{len(results)} PASS.**",
        "",
        "Each row maps Phase 1 history to a separately curated structured replay and expectation.",
        "",
        (
            "| Case | Historical situation | Old incorrect interpretation | "
            "New classification | Hypothesis impact | Recovery / control | Result |"
        ),
        (
            "|------|----------------------|------------------------------|"
            "--------------------|-------------------|--------------------|--------|"
        ),
    ]
    for result in results:
        failure = failures[result.failure_id]
        expectation = expectations[result.failure_id]
        recovery = failure.get("recovery") or expectation["expected_control"]
        row = (
            "| {case} | {situation} | {old} | {classification} | {impact} | "
            "{recovery} (`{control}`) | {status} |"
        )
        lines.append(
            row.format(
                case=result.failure_id,
                situation=_markdown_cell(failure["observed_result"]),
                old=_markdown_cell(failure["initial_interpretation"]),
                classification=result.actual_result_class.value,
                impact=result.actual_impact.value,
                recovery=_markdown_cell(recovery),
                control=result.actual_control,
                status="PASS" if result.passed else "FAIL",
            )
        )
    lines.extend(
        (
            "",
            "## Interpretation",
            "- Environmental/tool/auth/network/timeout outcomes never become automatic disproof.",
            (
                "- Compound historical cases are replayed at their relevant control layer rather "
                "than forced into fabricated raw output."
            ),
            "- Collision, readability, behavioral matching, and model suggestions remain unverified.",
            "- Missing historical fields remain null; no evidence or recovery data is invented.",
            "",
        )
    )
    return "\n".join(lines)
