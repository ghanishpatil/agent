from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Tuple

from .models import Evidence, EvidenceOrigin, Hypothesis, HypothesisImpact, HypothesisStatus


def _append_unique(values: Tuple[str, ...], value: str) -> Tuple[str, ...]:
    return values if value in values else values + (value,)


def apply_evidence(
    hypothesis: Hypothesis,
    evidence: Evidence,
    impact: HypothesisImpact,
    updated_at: datetime,
) -> Hypothesis:
    """Apply current evidence; historical memory may propose tests but cannot change belief."""
    if evidence.provenance.origin is EvidenceOrigin.HISTORICAL_MEMORY:
        raise ValueError("historical memory cannot directly update a current hypothesis")
    evidence_id = evidence.evidence_id
    if impact is HypothesisImpact.SUPPORTS:
        return replace(
            hypothesis,
            status=HypothesisStatus.SUPPORTED,
            supporting_evidence=_append_unique(hypothesis.supporting_evidence, evidence_id),
            last_updated=updated_at,
        )
    if impact is HypothesisImpact.DISPROVES:
        return replace(
            hypothesis,
            status=HypothesisStatus.DISPROVEN,
            contradicting_evidence=_append_unique(hypothesis.contradicting_evidence, evidence_id),
            last_updated=updated_at,
        )
    if impact is HypothesisImpact.WEAKENS:
        return replace(
            hypothesis,
            status=HypothesisStatus.OPEN,
            contradicting_evidence=_append_unique(hypothesis.contradicting_evidence, evidence_id),
            last_updated=updated_at,
        )
    if impact in {HypothesisImpact.UNRESOLVES, HypothesisImpact.BLOCKS_TEST}:
        return replace(
            hypothesis,
            status=HypothesisStatus.UNRESOLVED,
            unresolved_evidence=_append_unique(hypothesis.unresolved_evidence, evidence_id),
            last_updated=updated_at,
        )
    return hypothesis
