from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ctf_agent.classifier import classify_result
from ctf_agent.evidence import EvidenceManager
from ctf_agent.models import (
    ControlDecision,
    EnvironmentState,
    ExecutionResult,
    FlagCandidate,
    HypothesisImpact,
    Observation,
    RelevantState,
    VerificationMethod,
    VerificationPolicy,
    VerificationStatus,
)
from ctf_agent.verification import FlagAttemptRegistry, VerificationController


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)
STATE = RelevantState(EnvironmentState("env-1", ("http_request",)), "guest", "s1", "c1")


def record(
    manager: EvidenceManager,
    *,
    action_id: str = "a1",
    tool: str = "http_request",
    body: str = "",
    metadata=None,
):
    execution = ExecutionResult(
        action_id,
        tool,
        exit_code=0,
        response_body=body,
        metadata=metadata or {},
    )
    observation = Observation(f"obs-{action_id}", action_id, NOW, "live", execution)
    return manager.record_current(
        observation=observation,
        classification=classify_result(execution),
        impact=HypothesisImpact.NO_IMPACT,
        affected_hypotheses=("h1",),
    )


def test_authoritative_challenge_output_verifies_and_stops() -> None:
    manager = EvidenceManager()
    evidence = record(manager, tool="challenge_service", body="accepted CTF{real}")
    controller = VerificationController(
        manager, VerificationPolicy(authoritative_output_tools=("challenge_service",))
    )
    result = controller.evaluate(FlagCandidate("CTF{real}", "service"), (evidence.evidence_id,))
    assert result.candidate.verification_status is VerificationStatus.VERIFIED
    assert result.decision is ControlDecision.STOP
    assert result.candidate.verified_at == NOW


def test_plausible_readable_flag_is_not_verified() -> None:
    manager = EvidenceManager()
    evidence = record(manager, body="CTF{looks_real}")
    controller = VerificationController(manager, VerificationPolicy())
    result = controller.evaluate(
        FlagCandidate("CTF{looks_real}", "decoded-text"), (evidence.evidence_id,)
    )
    assert result.candidate.verification_status is VerificationStatus.SUPPORTED
    assert result.decision is ControlDecision.CONTINUE


def test_weak_checker_collision_is_never_the_intended_flag() -> None:
    manager = EvidenceManager()
    evidence = record(
        manager,
        tool="trusted_deriver",
        metadata={
            "verified_candidate": "IATCQ{collision}",
            "verification_passed": True,
            "verification_method": VerificationMethod.WEAK_CHECKER_COLLISION.value,
            "verification_basis": "weak 32-bit checker accepted collision",
        },
    )
    controller = VerificationController(
        manager, VerificationPolicy(deterministic_tools=("trusted_deriver",))
    )
    result = controller.evaluate(
        FlagCandidate("IATCQ{collision}", "weak-checker"), (evidence.evidence_id,)
    )
    assert result.candidate.verification_status is not VerificationStatus.VERIFIED
    assert result.decision is ControlDecision.CONTINUE


def test_model_suggestion_is_not_verification() -> None:
    manager = EvidenceManager()
    evidence = record(
        manager,
        tool="trusted_deriver",
        metadata={
            "verified_candidate": "flag{invented}",
            "verification_passed": True,
            "verification_method": VerificationMethod.MODEL_SUGGESTION.value,
            "verification_basis": "model said so",
        },
    )
    controller = VerificationController(
        manager, VerificationPolicy(deterministic_tools=("trusted_deriver",))
    )
    result = controller.evaluate(
        FlagCandidate("flag{invented}", "model"), (evidence.evidence_id,)
    )
    assert result.candidate.verification_status is not VerificationStatus.VERIFIED


def test_rejected_authoritative_attempt_marks_candidate_rejected() -> None:
    manager = EvidenceManager()
    evidence = record(
        manager,
        tool="challenge_verifier",
        metadata={
            "submitted_candidate": "CTF{wrong}",
            "verifier_accepted": False,
            "rejection_reason": "incorrect flag",
        },
    )
    controller = VerificationController(
        manager, VerificationPolicy(verifier_tools=("challenge_verifier",))
    )
    result = controller.evaluate(
        FlagCandidate("CTF{wrong}", "submission"), (evidence.evidence_id,)
    )
    assert result.candidate.verification_status is VerificationStatus.REJECTED
    assert result.decision is ControlDecision.CONTINUE


def test_unknown_verification_evidence_is_rejected() -> None:
    controller = VerificationController(EvidenceManager(), VerificationPolicy())
    with pytest.raises(KeyError, match="unknown evidence"):
        controller.evaluate(FlagCandidate("CTF{maybe}", "source"), ("invented",))


def test_anti_spray_blocks_identical_candidate_attempt_in_identical_context() -> None:
    manager = EvidenceManager()
    evidence = record(manager, body="CTF{maybe}")
    registry = FlagAttemptRegistry(manager)
    candidate = FlagCandidate("CTF{maybe}", "decoder")
    assert registry.check_and_record(
        candidate, "ctfd-instance-1", (evidence.evidence_id,), STATE, NOW
    ) is ControlDecision.ALLOWED
    assert registry.check_and_record(
        candidate, "ctfd-instance-1", (evidence.evidence_id,), STATE, NOW
    ) is ControlDecision.DUPLICATE


def test_anti_spray_allows_attempt_after_material_change() -> None:
    manager = EvidenceManager()
    first = record(manager, action_id="a1", body="CTF{maybe} CTF{changed}")
    second = record(manager, action_id="a2", body="CTF{maybe}")
    registry = FlagAttemptRegistry(manager)
    candidate = FlagCandidate("CTF{maybe}", "decoder")
    registry.check_and_record(candidate, "ctfd", (first.evidence_id,), STATE, NOW)
    assert registry.check_and_record(
        FlagCandidate("CTF{changed}", "decoder"),
        "ctfd",
        (first.evidence_id,),
        STATE,
        NOW,
    ) is ControlDecision.ALLOWED
    assert registry.check_and_record(
        candidate, "ctfd", (first.evidence_id, second.evidence_id), STATE, NOW
    ) is ControlDecision.ALLOWED
    changed_state = RelevantState(STATE.environment, "guest", "s2", "c1")
    assert registry.check_and_record(
        candidate, "ctfd", (first.evidence_id,), changed_state, NOW
    ) is ControlDecision.ALLOWED


def test_anti_spray_registry_preserves_attempt_audit_records() -> None:
    manager = EvidenceManager()
    evidence = record(manager, body="CTF{maybe}")
    registry = FlagAttemptRegistry(manager)
    candidate = FlagCandidate("CTF{maybe}", "decoder-output")
    registry.check_and_record(candidate, "ctfd", (evidence.evidence_id,), STATE, NOW)
    assert len(registry.attempts) == 1
    assert registry.attempts[0].value == "CTF{maybe}"
    assert registry.attempts[0].source == "decoder-output"
    assert registry.attempts[0].attempted_at == NOW
