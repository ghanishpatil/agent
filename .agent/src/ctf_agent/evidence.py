from __future__ import annotations

import hashlib

from .classifier import classify_result
from .models import (
    Evidence,
    EvidenceOrigin,
    EvidenceStatus,
    Freshness,
    HypothesisImpact,
    Observation,
    Provenance,
    ResultClass,
    ResultClassification,
)


_ENVIRONMENTAL_RESULTS = {
    ResultClass.RATE_LIMIT,
    ResultClass.TIMEOUT,
    ResultClass.NETWORK_FAILURE,
    ResultClass.ENVIRONMENT_FAILURE,
}


def _status_for(result_class: ResultClass, impact: HypothesisImpact) -> EvidenceStatus:
    if result_class is ResultClass.TOOL_FAILURE:
        return EvidenceStatus.TOOL_FAILURE
    if result_class in _ENVIRONMENTAL_RESULTS:
        return EvidenceStatus.ENVIRONMENTAL_FAILURE
    if impact is HypothesisImpact.BLOCKS_TEST:
        return EvidenceStatus.BLOCKED
    if impact is HypothesisImpact.SUPPORTS:
        return EvidenceStatus.SUPPORTED
    if impact is HypothesisImpact.DISPROVES:
        return EvidenceStatus.DISPROVEN
    if impact is HypothesisImpact.WEAKENS:
        return EvidenceStatus.PLAUSIBLE
    return EvidenceStatus.UNRESOLVED


class EvidenceManager:
    """The only ledger for current evidence and read-only historical priors."""

    def __init__(self) -> None:
        self._records: dict[str, Evidence] = {}

    @property
    def records(self) -> tuple[Evidence, ...]:
        return tuple(self._records.values())

    def get(self, evidence_id: str) -> Evidence:
        try:
            return self._records[evidence_id]
        except KeyError as error:
            raise KeyError(f"unknown evidence: {evidence_id}") from error

    def record_current(
        self,
        *,
        observation: Observation,
        classification: ResultClassification,
        impact: HypothesisImpact,
        affected_hypotheses: tuple[str, ...],
    ) -> Evidence:
        actual = classify_result(observation.execution)
        if actual != classification:
            raise ValueError("classification is not bound to the supplied observation")
        return self._record(
            observation=observation,
            result_class=classification.result_class,
            status=_status_for(classification.result_class, impact),
            strength=(
                1.0
                if impact in {HypothesisImpact.SUPPORTS, HypothesisImpact.DISPROVES}
                else 0.6
            ),
            affected_hypotheses=affected_hypotheses,
            freshness=Freshness.CURRENT,
            provenance=Provenance(EvidenceOrigin.CURRENT_OBSERVATION, observation.source),
        )

    def record_historical_prior(
        self,
        *,
        observation: Observation,
        affected_hypotheses: tuple[str, ...],
    ) -> Evidence:
        return self._record(
            observation=observation,
            result_class=ResultClass.AMBIGUOUS,
            status=EvidenceStatus.PLAUSIBLE,
            strength=0.2,
            affected_hypotheses=affected_hypotheses,
            freshness=Freshness.STALE,
            provenance=Provenance(EvidenceOrigin.HISTORICAL_MEMORY, observation.source),
        )

    def _record(
        self,
        *,
        observation: Observation,
        result_class: ResultClass,
        status: EvidenceStatus,
        strength: float,
        affected_hypotheses: tuple[str, ...],
        freshness: Freshness,
        provenance: Provenance,
    ) -> Evidence:
        if not observation.source.strip() or not provenance.locator.strip():
            raise ValueError("evidence provenance is required")
        identity = "|".join(
            (
                observation.observation_id,
                result_class.value,
                status.value,
                provenance.origin.value,
                provenance.locator,
                *affected_hypotheses,
            )
        )
        evidence_id = "ev-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
        evidence = Evidence(
            evidence_id=evidence_id,
            action_id=observation.action_id,
            timestamp=observation.timestamp,
            source=observation.source,
            observation=observation,
            result_class=result_class,
            status=status,
            strength=strength,
            affected_hypotheses=affected_hypotheses,
            freshness=freshness,
            provenance=provenance,
        )
        self._records[evidence_id] = evidence
        return evidence

    @staticmethod
    def resolve_conflict(*, current: Evidence, historical: Evidence) -> Evidence:
        if current.provenance.origin is not EvidenceOrigin.CURRENT_OBSERVATION:
            raise ValueError("current evidence must originate from a current observation")
        if historical.provenance.origin is not EvidenceOrigin.HISTORICAL_MEMORY:
            raise ValueError("historical evidence must originate from historical memory")
        return current
