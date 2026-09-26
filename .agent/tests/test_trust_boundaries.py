from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ctf_agent.classifier import classify_result
from ctf_agent.deduplication import fingerprint_action
from ctf_agent.evidence import EvidenceManager
from ctf_agent.hypothesis import apply_evidence
from ctf_agent.kernel import TrustKernel
from ctf_agent.models import (
    Action,
    ControlDecision,
    EnvironmentState,
    ExecutionResult,
    FlagCandidate,
    Hypothesis,
    HypothesisImpact,
    HypothesisStatus,
    Observation,
    RelevantState,
    TestSpecification,
    VerificationPolicy,
    VerificationStatus,
)
from ctf_agent.verification import FlagAttemptRegistry, VerificationController


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("http_request",)), "guest", "s1", "c1")


def action(action_id: str = "a1") -> Action:
    return Action(
        action_id,
        "Probe hypothesis",
        "http_request",
        "https://ctf.local/probe",
        {"id": "1'"},
        {"method": "GET"},
        ("target-online",),
        STATE,
    )


def record_evidence(manager: EvidenceManager, execution: ExecutionResult, source: str = "live"):
    observation = Observation("obs-1", execution.action_id, NOW, source, execution)
    classification = classify_result(execution)
    return manager.record_current(
        observation=observation,
        classification=classification,
        impact=HypothesisImpact.NO_IMPACT,
        affected_hypotheses=("h1",),
    )


def test_untrusted_flag_like_output_cannot_self_assert_authority() -> None:
    manager = EvidenceManager()
    evidence = record_evidence(
        manager,
        ExecutionResult(
            "a1",
            "http_request",
            exit_code=0,
            http_status=200,
            response_body="CTF{fabricated}",
            metadata={"authoritative_output": True},
        ),
    )
    controller = VerificationController(
        manager,
        VerificationPolicy(authoritative_output_tools=("challenge_service",)),
    )
    result = controller.evaluate(FlagCandidate("CTF{fabricated}", "response"), (evidence.evidence_id,))
    assert result.candidate.verification_status is not VerificationStatus.VERIFIED
    assert result.decision is ControlDecision.CONTINUE


def test_trusted_authoritative_output_is_bound_to_exact_candidate() -> None:
    manager = EvidenceManager()
    evidence = record_evidence(
        manager,
        ExecutionResult(
            "a1",
            "challenge_service",
            exit_code=0,
            response_body="accepted CTF{real}",
        ),
    )
    controller = VerificationController(
        manager,
        VerificationPolicy(authoritative_output_tools=("challenge_service",)),
    )
    real = controller.evaluate(FlagCandidate("CTF{real}", "response"), (evidence.evidence_id,))
    fake = controller.evaluate(FlagCandidate("CTF{fake}", "response"), (evidence.evidence_id,))
    assert real.candidate.verification_status is VerificationStatus.VERIFIED
    assert real.decision is ControlDecision.STOP
    assert fake.candidate.verification_status is not VerificationStatus.VERIFIED


def test_candidate_terminal_status_cannot_be_supplied_by_caller() -> None:
    with pytest.raises(TypeError):
        FlagCandidate(
            "CTF{fabricated}",
            "caller",
            verification_status=VerificationStatus.VERIFIED,
        )


def test_evidence_manager_rejects_classification_not_bound_to_observation() -> None:
    manager = EvidenceManager()
    execution = ExecutionResult("a1", "http_request", http_status=429)
    observation = Observation("obs-1", "a1", NOW, "live", execution)
    mismatched = classify_result(ExecutionResult("a1", "http_request", http_status=200))
    with pytest.raises(ValueError, match="classification"):
        manager.record_current(
            observation=observation,
            classification=mismatched,
            impact=HypothesisImpact.NO_IMPACT,
            affected_hypotheses=("h1",),
        )


def test_historical_evidence_cannot_directly_disprove_current_hypothesis() -> None:
    manager = EvidenceManager()
    historical = manager.record_historical_prior(
        observation=Observation(
            "obs-historical",
            "historical-action",
            NOW,
            "FAIL-001",
            ExecutionResult("historical-action", "memory"),
        ),
        affected_hypotheses=("h1",),
    )
    hypothesis = Hypothesis("h1", "Current hypothesis")
    with pytest.raises(ValueError, match="historical"):
        apply_evidence(hypothesis, historical, HypothesisImpact.DISPROVES, NOW)


def test_kernel_atomically_blocks_duplicate_before_observation_creation() -> None:
    kernel = TrustKernel()
    hypothesis = Hypothesis("h1", "SQLi may exist")
    first_action = action("a1")
    first = kernel.process(
        action=first_action,
        execution=ExecutionResult("a1", "http_request", http_status=429),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="live",
    )
    duplicate_action = action("a2")
    duplicate = kernel.process(
        action=duplicate_action,
        execution=ExecutionResult("a2", "http_request", http_status=429),
        hypothesis=first.hypothesis,
        observed_at=NOW,
        source="live",
    )
    assert first.decision is ControlDecision.CONTINUE
    assert duplicate.decision is ControlDecision.DUPLICATE
    assert duplicate.observation is None
    assert duplicate.evidence is None


def test_kernel_cannot_disprove_from_unregistered_caller_assertions() -> None:
    kernel = TrustKernel()
    hypothesis = Hypothesis("h1", "Feature exists")
    attempted = action("a1")
    result = kernel.process(
        action=attempted,
        execution=ExecutionResult("a1", "http_request", http_status=200, response_body="no"),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="trusted-service",
    )
    assert result.hypothesis.status is not HypothesisStatus.DISPROVEN


def test_registered_discriminating_test_may_disprove_from_authoritative_observation() -> None:
    kernel = TrustKernel(trusted_sources={"http_request": ("trusted-service",)})
    hypothesis = Hypothesis("h1", "Feature exists")
    attempted = action("a1")
    kernel.register_test(
        attempted,
        TestSpecification(
            hypothesis_id="h1",
            contradicting_body_contains=("feature absent",),
            authoritative_sources=("trusted-service",),
        ),
    )
    result = kernel.process(
        action=attempted,
        execution=ExecutionResult(
            "a1", "http_request", http_status=200, response_body="feature absent"
        ),
        hypothesis=hypothesis,
        observed_at=NOW,
        source="trusted-service",
    )
    assert result.impact is HypothesisImpact.DISPROVES
    assert result.hypothesis.status is HypothesisStatus.DISPROVEN


def test_anti_spray_rejects_invented_evidence_ids_and_computes_state_digest() -> None:
    manager = EvidenceManager()
    registry = FlagAttemptRegistry(manager)
    candidate = FlagCandidate("CTF{maybe}", "decoder")
    with pytest.raises(KeyError, match="unknown evidence"):
        registry.check_and_record(candidate, "ctfd", ("invented",), STATE, NOW)


def test_action_test_specification_is_bound_to_semantic_fingerprint() -> None:
    kernel = TrustKernel()
    attempted = action("a1")
    kernel.register_test(attempted, TestSpecification(hypothesis_id="h1"))
    assert kernel.test_fingerprint("h1") == fingerprint_action(attempted)


def test_atomic_kernel_pipeline_verifies_and_stops_from_trusted_output() -> None:
    kernel = TrustKernel(
        verification_policy=VerificationPolicy(
            authoritative_output_tools=("challenge_service",)
        )
    )
    prior = record_evidence(
        kernel.evidence,
        ExecutionResult("derive-1", "analysis", exit_code=0, stdout="CTF{real}"),
    )
    attempted = Action(
        "a-stop",
        "Submit candidate",
        "challenge_service",
        "https://ctf.local/submit",
        {"flag": "CTF{real}"},
        {"method": "POST"},
        ("candidate-ready",),
        STATE,
    )
    result = kernel.process(
        action=attempted,
        execution=ExecutionResult(
            "a-stop", "challenge_service", exit_code=0, response_body="accepted CTF{real}"
        ),
        hypothesis=Hypothesis("h1", "Candidate is intended flag"),
        observed_at=NOW,
        source="challenge-service",
        candidate=FlagCandidate("CTF{real}", "derived"),
        candidate_evidence_ids=(prior.evidence_id,),
        verifier="ctfd-instance",
    )
    assert result.decision is ControlDecision.STOP
    assert result.verification is not None
    assert result.verification.candidate.verification_status is VerificationStatus.VERIFIED
    assert kernel.snapshot().verification.decision is ControlDecision.STOP


def test_kernel_refuses_further_exploration_after_verified_stop() -> None:
    policy = VerificationPolicy(authoritative_output_tools=("challenge_service",))
    kernel = TrustKernel(verification_policy=policy)
    prior = record_evidence(
        kernel.evidence,
        ExecutionResult("derive-2", "analysis", exit_code=0, stdout="CTF{real}"),
    )
    first_action = Action(
        "a-stop",
        "Submit candidate",
        "challenge_service",
        "https://ctf.local/submit",
        {"flag": "CTF{real}"},
        {"method": "POST"},
        ("candidate-ready",),
        STATE,
    )
    kernel.process(
        action=first_action,
        execution=ExecutionResult(
            "a-stop", "challenge_service", exit_code=0, response_body="accepted CTF{real}"
        ),
        hypothesis=Hypothesis("h1", "Candidate is intended flag"),
        observed_at=NOW,
        source="challenge-service",
        candidate=FlagCandidate("CTF{real}", "derived"),
        candidate_evidence_ids=(prior.evidence_id,),
        verifier="ctfd-instance",
    )
    later = action("a-later")
    result = kernel.process(
        action=later,
        execution=ExecutionResult("a-later", "http_request", http_status=200),
        hypothesis=Hypothesis("h2", "Explore another branch"),
        observed_at=NOW,
        source="live",
    )
    assert result.decision is ControlDecision.STOP
    assert result.observation is None
    assert result.evidence is None


def test_action_and_execution_tools_must_match() -> None:
    kernel = TrustKernel(
        verification_policy=VerificationPolicy(
            authoritative_output_tools=("challenge_service",)
        )
    )
    with pytest.raises(ValueError, match="tool must match"):
        kernel.process(
            action=action("a-mismatch"),
            execution=ExecutionResult(
                "a-mismatch",
                "challenge_service",
                exit_code=0,
                response_body="CTF{fabricated}",
            ),
            hypothesis=Hypothesis("h1", "Candidate is real"),
            observed_at=NOW,
            source="challenge-service",
        )


def test_failed_authoritative_output_cannot_verify_candidate() -> None:
    manager = EvidenceManager()
    evidence = record_evidence(
        manager,
        ExecutionResult(
            "a1",
            "challenge_service",
            exit_code=1,
            stderr="rejected CTF{wrong}",
            response_body="rejected CTF{wrong}",
        ),
    )
    controller = VerificationController(
        manager,
        VerificationPolicy(authoritative_output_tools=("challenge_service",)),
    )
    result = controller.evaluate(FlagCandidate("CTF{wrong}", "response"), (evidence.evidence_id,))
    assert result.candidate.verification_status is not VerificationStatus.VERIFIED


def test_invalid_execution_does_not_poison_action_deduplication() -> None:
    kernel = TrustKernel()
    attempted = action("a-valid-after-error")
    with pytest.raises(ValueError, match="action_id"):
        kernel.process(
            action=attempted,
            execution=ExecutionResult("wrong-id", "http_request", http_status=200),
            hypothesis=Hypothesis("h1", "Feature exists"),
            observed_at=NOW,
            source="live",
        )
    result = kernel.process(
        action=attempted,
        execution=ExecutionResult("a-valid-after-error", "http_request", http_status=200),
        hypothesis=Hypothesis("h1", "Feature exists"),
        observed_at=NOW,
        source="live",
    )
    assert result.decision is ControlDecision.CONTINUE
    assert result.observation is not None


def test_anti_spray_requires_nonempty_candidate_relevant_evidence() -> None:
    manager = EvidenceManager()
    registry = FlagAttemptRegistry(manager)
    candidate = FlagCandidate("CTF{maybe}", "decoder")
    with pytest.raises(ValueError, match="non-empty"):
        registry.check_and_record(candidate, "ctfd", (), STATE, NOW)

    unrelated = record_evidence(
        manager,
        ExecutionResult("a1", "analysis", exit_code=0, stdout="unrelated output"),
    )
    with pytest.raises(ValueError, match="candidate"):
        registry.check_and_record(
            candidate, "ctfd", (unrelated.evidence_id,), STATE, NOW
        )


def test_authoritative_output_rejects_candidate_that_is_only_a_strict_substring() -> None:
    manager = EvidenceManager()
    evidence = record_evidence(
        manager,
        ExecutionResult(
            "a1", "challenge_service", exit_code=0, response_body="CTF{real}evil"
        ),
    )
    controller = VerificationController(
        manager,
        VerificationPolicy(authoritative_output_tools=("challenge_service",)),
    )
    result = controller.evaluate(FlagCandidate("CTF{real}", "response"), (evidence.evidence_id,))
    assert result.candidate.verification_status is not VerificationStatus.VERIFIED


def test_anti_spray_rejects_candidate_that_is_only_a_strict_substring() -> None:
    manager = EvidenceManager()
    evidence = record_evidence(
        manager,
        ExecutionResult("a1", "analysis", exit_code=0, stdout="CTF{real}evil"),
    )
    registry = FlagAttemptRegistry(manager)
    with pytest.raises(ValueError, match="candidate"):
        registry.check_and_record(
            FlagCandidate("CTF{real}", "decoder"),
            "ctfd",
            (evidence.evidence_id,),
            STATE,
            NOW,
        )
