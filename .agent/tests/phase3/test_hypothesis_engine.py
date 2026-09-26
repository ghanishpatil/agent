from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ctf_agent.hypothesis_engine import HypothesisAuthorityError, HypothesisBoard
from ctf_agent.kernel import TrustKernel
from ctf_agent.models import (
    Action,
    EnvironmentState,
    ExecutionResult,
    Hypothesis,
    HypothesisImpact,
    HypothesisStatus,
    RelevantState,
    TestSpecification,
)


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("http_request",)), "guest", "s1", "c1")


def action(action_id: str, tool: str = "http_request") -> Action:
    return Action(
        action_id, "probe", tool, "https://ctf.local/probe", None, {}, (), STATE
    )


def test_board_creates_open_hypothesis_without_terminal_status() -> None:
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "SQLi may exist", technique="sqli")
    assert hypothesis.status is HypothesisStatus.OPEN
    assert board.meta("h1").technique == "sqli"


def test_board_rejects_duplicate_hypothesis_id() -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "first")
    with pytest.raises(ValueError, match="already exists"):
        board.propose_hypothesis("h1", "second")


def test_board_records_kernel_output_and_reflects_unresolved_state() -> None:
    kernel = TrustKernel()
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "SQLi may exist")
    result = kernel.process(
        action=action("a1"),
        execution=ExecutionResult("a1", "http_request", http_status=429),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="live",
    )
    updated = board.record(result)
    assert updated.status is HypothesisStatus.UNRESOLVED
    assert board.get("h1").status is HypothesisStatus.UNRESOLVED


def test_board_records_supported_state_only_via_real_evidence() -> None:
    kernel = TrustKernel(trusted_sources={"http_request": ("trusted-service",)})
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "Feature exists")
    kernel.register_test(
        action("a1"),
        TestSpecification(
            hypothesis_id="h1",
            supporting_body_contains=("feature present",),
            authoritative_sources=("trusted-service",),
        ),
    )
    result = kernel.process(
        action=action("a1"),
        execution=ExecutionResult(
            "a1", "http_request", http_status=200, response_body="feature present"
        ),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="trusted-service",
    )
    updated = board.record(result)
    assert updated.status is HypothesisStatus.SUPPORTED


def test_board_refuses_to_record_a_hand_constructed_terminal_hypothesis() -> None:
    from ctf_agent.kernel import PipelineResult
    from ctf_agent.models import ControlDecision

    board = HypothesisBoard()
    fabricated = Hypothesis(
        hypothesis_id="h1", statement="I decided this myself", status=HypothesisStatus.DISPROVEN
    )
    fake_result = PipelineResult(action("a1"), ControlDecision.CONTINUE, fabricated)
    with pytest.raises(HypothesisAuthorityError):
        board.record(fake_result)


def test_set_priority_closes_a_branch_without_declaring_disproof() -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "Weak lead")
    board.set_priority("h1", 0)
    assert board.get("h1").status is HypothesisStatus.OPEN
    assert board.meta("h1").priority == 0
    assert board.get("h1") not in board.open_hypotheses()


def test_unresolved_hypotheses_excludes_closed_branches() -> None:
    kernel = TrustKernel()
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "SQLi may exist")
    result = kernel.process(
        action=action("a1"),
        execution=ExecutionResult("a1", "http_request", http_status=429),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="live",
    )
    board.record(result)
    assert board.get("h1") in board.unresolved_hypotheses()
    board.set_priority("h1", 0)
    assert board.get("h1") not in board.unresolved_hypotheses()
