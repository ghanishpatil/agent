from __future__ import annotations

from datetime import datetime, timezone

from ctf_agent.classifier import classify_result
from ctf_agent.context import ChallengeMetadata, FactState, build_context
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.kernel import TrustKernel
from ctf_agent.models import (
    Action,
    EnvironmentState,
    ExecutionResult,
    FlagCandidate,
    HypothesisImpact,
    Observation,
    RelevantState,
    TestSpecification,
    VerificationPolicy,
)


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("http_request", "challenge_service")), "guest", "s1", "c1")


def action(action_id: str, tool: str = "http_request", target: str = "https://ctf.local/probe") -> Action:
    return Action(action_id, "probe", tool, target, None, {}, (), STATE)


def metadata() -> ChallengeMetadata:
    return ChallengeMetadata(
        name="Sample Web",
        category="web",
        points=100,
        solves=5,
        description="find the flag",
        flag_format="CTF{...}",
        files=(),
        urls=("https://ctf.local/",),
    )


def test_static_metadata_is_known() -> None:
    kernel = TrustKernel()
    board = HypothesisBoard()
    context = build_context(metadata(), kernel, board)
    facts = context.facts()
    assert facts["name"] is FactState.KNOWN
    assert facts["flag_format"] is FactState.KNOWN
    assert facts["urls"] is FactState.KNOWN


def test_hypothesis_starts_plausible_before_any_evidence() -> None:
    kernel = TrustKernel()
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "SQLi may exist")
    context = build_context(metadata(), kernel, board)
    views = {view.hypothesis.hypothesis_id: view for view in context.hypothesis_views()}
    assert views["h1"].state is FactState.PLAUSIBLE
    assert views["h1"].evidence_count == 0


def test_hypothesis_becomes_unresolved_after_environmental_failure() -> None:
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
    context = build_context(metadata(), kernel, board)
    views = {view.hypothesis.hypothesis_id: view for view in context.hypothesis_views()}
    assert views["h1"].state is FactState.UNRESOLVED
    assert views["h1"].evidence_count == 1


def test_closed_branch_reports_blocked_not_disproven() -> None:
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
    board.set_priority("h1", 0)
    context = build_context(metadata(), kernel, board)
    views = {view.hypothesis.hypothesis_id: view for view in context.hypothesis_views()}
    assert views["h1"].state is FactState.BLOCKED


def test_disproven_hypothesis_from_authoritative_contradiction() -> None:
    kernel = TrustKernel(trusted_sources={"http_request": ("trusted-service",)})
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "Feature exists")
    kernel.register_test(
        action("a1"),
        TestSpecification(
            hypothesis_id="h1",
            contradicting_body_contains=("feature absent",),
            authoritative_sources=("trusted-service",),
        ),
    )
    result = kernel.process(
        action=action("a1"),
        execution=ExecutionResult(
            "a1", "http_request", http_status=200, response_body="feature absent"
        ),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="trusted-service",
    )
    board.record(result)
    context = build_context(metadata(), kernel, board)
    views = {view.hypothesis.hypothesis_id: view for view in context.hypothesis_views()}
    assert views["h1"].state is FactState.DISPROVEN


def test_context_is_verified_only_after_kernel_reaches_stop() -> None:
    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("challenge_service",))
    )
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "Candidate is intended flag")

    unverified_context = build_context(metadata(), kernel, board)
    assert unverified_context.is_verified() is False

    derive_execution = ExecutionResult("derive-1", "analysis", exit_code=0, stdout="CTF{real}")
    prior = kernel.evidence.record_current(
        observation=Observation("obs-derive", "derive-1", NOW, "analysis", derive_execution),
        classification=classify_result(derive_execution),
        impact=HypothesisImpact.NO_IMPACT,
        affected_hypotheses=("h1",),
    )
    result = kernel.process(
        action=action("a-stop", tool="challenge_service", target="https://ctf.local/submit"),
        execution=ExecutionResult(
            "a-stop", "challenge_service", exit_code=0, response_body="accepted CTF{real}"
        ),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="challenge-service",
        candidate=FlagCandidate("CTF{real}", "derived"),
        candidate_evidence_ids=(prior.evidence_id,),
        verifier="ctfd",
    )
    board.record(result)
    verified_context = build_context(metadata(), kernel, board)
    assert verified_context.is_verified() is True
