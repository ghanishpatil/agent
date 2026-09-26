from __future__ import annotations

import pytest

from ctf_agent.classifier import classify_result
from ctf_agent.impact import determine_impact
from ctf_agent.models import (
    ExecutionResult,
    HypothesisImpact,
    ImpactContext,
    ResultClass,
)


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (
            ExecutionResult("a-rate", "http_request", exit_code=0, http_status=429),
            ResultClass.RATE_LIMIT,
        ),
        (
            ExecutionResult("a-auth", "http_request", exit_code=0, http_status=401),
            ResultClass.AUTH_FAILURE,
        ),
        (
            ExecutionResult("a-authz", "http_request", exit_code=0, http_status=403),
            ResultClass.AUTHZ_FAILURE,
        ),
        (
            ExecutionResult("a-input", "http_request", exit_code=0, http_status=422),
            ResultClass.INPUT_REJECTION,
        ),
        (ExecutionResult("a-tool", "gdb", tool_available=False), ResultClass.TOOL_FAILURE),
        (
            ExecutionResult("a-env", "docker", environment_available=False),
            ResultClass.ENVIRONMENT_FAILURE,
        ),
        (
            ExecutionResult("a-network", "http_request", network_state="unreachable"),
            ResultClass.NETWORK_FAILURE,
        ),
        (ExecutionResult("a-timeout", "solver", timed_out=True, exit_code=1), ResultClass.TIMEOUT),
        (
            ExecutionResult(
                "a-state", "login", exit_code=0, http_status=200, state_changed=True
            ),
            ResultClass.STATE_CHANGE,
        ),
        (
            ExecutionResult("a-target", "http_request", exit_code=0, http_status=200),
            ResultClass.TARGET_RESPONSE,
        ),
        (ExecutionResult("a-success", "script", exit_code=0), ResultClass.SUCCESS),
        (ExecutionResult("a-amb", "script"), ResultClass.AMBIGUOUS),
    ],
)
def test_structured_results_are_classified_deterministically(result: ExecutionResult, expected: ResultClass) -> None:
    assert classify_result(result).result_class is expected


def test_explicit_timeout_outranks_generic_nonzero_exit() -> None:
    result = ExecutionResult("a1", "solver", exit_code=127, timed_out=True)
    assert classify_result(result).result_class is ResultClass.TIMEOUT


def test_http_status_outranks_successful_process_exit() -> None:
    result = ExecutionResult("a1", "http_request", exit_code=0, http_status=429)
    assert classify_result(result).result_class is ResultClass.RATE_LIMIT


@pytest.mark.parametrize(
    ("result_class", "expected"),
    [
        (ResultClass.RATE_LIMIT, HypothesisImpact.UNRESOLVES),
        (ResultClass.TIMEOUT, HypothesisImpact.UNRESOLVES),
        (ResultClass.NETWORK_FAILURE, HypothesisImpact.UNRESOLVES),
        (ResultClass.TOOL_FAILURE, HypothesisImpact.UNRESOLVES),
        (ResultClass.ENVIRONMENT_FAILURE, HypothesisImpact.UNRESOLVES),
        (ResultClass.AUTH_FAILURE, HypothesisImpact.BLOCKS_TEST),
        (ResultClass.AUTHZ_FAILURE, HypothesisImpact.BLOCKS_TEST),
        (ResultClass.INPUT_REJECTION, HypothesisImpact.BLOCKS_TEST),
        (ResultClass.AMBIGUOUS, HypothesisImpact.UNRESOLVES),
    ],
)
def test_failures_do_not_automatically_disprove_hypotheses(
    result_class: ResultClass, expected: HypothesisImpact
) -> None:
    context = ImpactContext(hypothesis_id="h1")
    assert determine_impact(result_class, context) is expected


def test_authoritative_expected_observation_supports_hypothesis() -> None:
    context = ImpactContext(
        hypothesis_id="h1",
        prerequisites_met=True,
        valid_discriminating_test=True,
        authoritative_observation=True,
        expected_observation_seen=True,
    )
    assert determine_impact(ResultClass.TARGET_RESPONSE, context) is HypothesisImpact.SUPPORTS


def test_only_authoritative_discriminating_contradiction_disproves() -> None:
    context = ImpactContext(
        hypothesis_id="h1",
        prerequisites_met=True,
        valid_discriminating_test=True,
        authoritative_observation=True,
        contradiction_observed=True,
    )
    assert determine_impact(ResultClass.TARGET_RESPONSE, context) is HypothesisImpact.DISPROVES


def test_non_authoritative_contradiction_only_weakens() -> None:
    context = ImpactContext(
        hypothesis_id="h1",
        prerequisites_met=True,
        valid_discriminating_test=True,
        authoritative_observation=False,
        contradiction_observed=True,
    )
    assert determine_impact(ResultClass.TARGET_RESPONSE, context) is HypothesisImpact.WEAKENS


def test_generic_success_has_no_hypothesis_meaning_by_itself() -> None:
    context = ImpactContext(hypothesis_id="h1")
    assert determine_impact(ResultClass.SUCCESS, context) is HypothesisImpact.NO_IMPACT
