from __future__ import annotations

from datetime import datetime, timezone

from ctf_agent.kernel import TrustKernel
from ctf_agent.models import (
    Action,
    ControlDecision,
    EnvironmentState,
    ExecutionResult,
    Hypothesis,
    HypothesisImpact,
    RelevantState,
    ResultClass,
)


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("http_request",)), "guest", "s1", "c1")
ACTION = Action(
    action_id="a1",
    objective="Test SQL injection",
    tool="http_request",
    target="https://ctf.local/?id=1%27",
    input_data={"id": "1'"},
    relevant_parameters={"method": "GET"},
    prerequisites=("target-online",),
    state_before=STATE,
)


def test_mandatory_pipeline_keeps_raw_output_separate_from_belief_update() -> None:
    kernel = TrustKernel()
    hypothesis = Hypothesis("h-sqli", "SQL injection may exist")
    execution = ExecutionResult(
        action_id="a1",
        tool="http_request",
        exit_code=0,
        http_status=429,
        response_body="Too Many Requests",
    )
    result = kernel.process(
        action=ACTION,
        execution=execution,
        hypothesis=hypothesis,
        observed_at=NOW,
        source="live-http-response",
    )
    assert result.decision is ControlDecision.CONTINUE
    assert result.classification is not None
    assert result.classification.result_class is ResultClass.RATE_LIMIT
    assert result.impact is HypothesisImpact.UNRESOLVES
    assert result.hypothesis.statement == hypothesis.statement
    assert result.hypothesis.status.value == "UNRESOLVED"
    assert result.evidence is not None
    assert result.evidence.observation.execution is execution
    assert result.evidence.provenance.locator == "live-http-response"


def test_duplicate_action_is_blocked_before_processing() -> None:
    kernel = TrustKernel()
    hypothesis = Hypothesis("h-sqli", "SQL injection may exist")
    first = kernel.process(
        action=ACTION,
        execution=ExecutionResult("a1", "http_request", http_status=429),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="live",
    )
    duplicate = Action(
        action_id="a2",
        objective=ACTION.objective,
        tool=ACTION.tool,
        target=ACTION.target,
        input_data=ACTION.input_data,
        relevant_parameters=ACTION.relevant_parameters,
        prerequisites=ACTION.prerequisites,
        state_before=STATE,
    )
    result = kernel.process(
        action=duplicate,
        execution=ExecutionResult("a2", "http_request", http_status=429),
        hypothesis=first.hypothesis,
        observed_at=NOW,
        source="live",
    )
    assert result.decision is ControlDecision.DUPLICATE
    assert result.observation is None
    assert result.evidence is None
