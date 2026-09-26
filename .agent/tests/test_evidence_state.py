from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ctf_agent.classifier import classify_result
from ctf_agent.evidence import EvidenceManager
from ctf_agent.hypothesis import apply_evidence
from ctf_agent.models import (
    EvidenceOrigin,
    ExecutionResult,
    Hypothesis,
    HypothesisImpact,
    HypothesisStatus,
    Observation,
)


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)


def observation(action_id: str = "a1", source: str = "http://ctf.local/login") -> Observation:
    return Observation(
        observation_id="obs-1",
        action_id=action_id,
        timestamp=NOW,
        source=source,
        execution=ExecutionResult(action_id, "http_request", exit_code=0, http_status=429),
    )


def record_current(manager: EvidenceManager, obs: Observation):
    return manager.record_current(
        observation=obs,
        classification=classify_result(obs.execution),
        impact=HypothesisImpact.UNRESOLVES,
        affected_hypotheses=("h1",),
    )


def test_every_evidence_record_requires_provenance() -> None:
    manager = EvidenceManager()
    with pytest.raises(ValueError, match="provenance"):
        record_current(manager, observation(source=""))


def test_evidence_preserves_the_exact_observation_and_provenance() -> None:
    manager = EvidenceManager()
    obs = observation()
    evidence = record_current(manager, obs)
    assert evidence.observation is obs
    assert evidence.provenance.origin is EvidenceOrigin.CURRENT_OBSERVATION
    assert evidence.provenance.locator == obs.source
    assert evidence.action_id == "a1"
    assert evidence.result_class.value == "RATE_LIMIT"


def test_current_evidence_wins_over_conflicting_historical_memory() -> None:
    manager = EvidenceManager()
    current = record_current(manager, observation())
    historical = manager.record_historical_prior(
        observation=observation(action_id="historical", source="FAIL-005"),
        affected_hypotheses=("h1",),
    )
    assert manager.resolve_conflict(current=current, historical=historical) is current


def test_hypothesis_state_tracks_supporting_contradicting_and_unresolved_evidence() -> None:
    manager = EvidenceManager()
    obs = observation()
    evidence = record_current(manager, obs)
    hypothesis = Hypothesis("h1", "SQL injection may exist")

    hypothesis = apply_evidence(
        hypothesis, evidence, HypothesisImpact.UNRESOLVES, NOW
    )
    assert hypothesis.status is HypothesisStatus.UNRESOLVED
    assert hypothesis.unresolved_evidence == (evidence.evidence_id,)

    hypothesis = apply_evidence(hypothesis, evidence, HypothesisImpact.SUPPORTS, NOW)
    assert hypothesis.status is HypothesisStatus.SUPPORTED
    assert hypothesis.supporting_evidence == (evidence.evidence_id,)

    hypothesis = apply_evidence(hypothesis, evidence, HypothesisImpact.DISPROVES, NOW)
    assert hypothesis.status is HypothesisStatus.DISPROVEN
    assert hypothesis.contradicting_evidence == (evidence.evidence_id,)
