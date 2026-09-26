"""Corpus analysis for external-knowledge ingestion experiments.

Reuses the ctf_ingest model/store/dedup. Provides: corpus statistics, cross-corpus duplicate
detection (provenance preserved), extraction-quality analysis (explicit/inferred/missing per
requested field, never inventing reasoning stages), and corpus comparison.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from ctf_ingest.dedup import Deduplicator
from ctf_ingest.models import KnowledgeRecord, TrajectoryStepKind

# The 14 fields requested for extraction, mapped to record evidence.
EXPLICIT = "explicit"
INFERRED = "inferred"
MISSING = "missing"

_CATEGORY_LABEL = re.compile(r"category\s*[:\-]", re.IGNORECASE)

_STAGE_FIELDS = {
    "observed_clues": TrajectoryStepKind.OBSERVED_CLUE,
    "hypotheses": TrajectoryStepKind.HYPOTHESIS,
    "discriminating_tests": TrajectoryStepKind.DISCRIMINATING_TEST,
    "observations": TrajectoryStepKind.OBSERVATION,
    "interpretations": TrajectoryStepKind.INTERPRETATION,
    "hypothesis_updates": TrajectoryStepKind.HYPOTHESIS_UPDATE,
    "next_actions": TrajectoryStepKind.NEXT_ACTION,
    "exploit_solution": TrajectoryStepKind.EXPLOIT_SOLUTION,
    "verification": TrajectoryStepKind.VERIFICATION,
    "challenge_context": TrajectoryStepKind.CHALLENGE_CONTEXT,
}


def corpus_stats(records: Sequence[KnowledgeRecord]) -> Dict[str, object]:
    unique = [r for r in records if r.duplicate_of is None]
    categories = Counter(r.metadata.category or "unknown" for r in unique)
    techniques = Counter(t.technique_id for r in unique for t in r.techniques)
    completeness = [r.trajectory.completeness for r in unique]
    with_failures = sum(1 for r in unique if r.failures)
    with_techniques = sum(1 for r in unique if r.techniques)
    challenges = {(r.metadata.event, r.metadata.name or r.title) for r in unique}
    return {
        "documents": len(records),
        "unique_documents": len(unique),
        "unique_challenges": len(challenges),
        "categories": dict(sorted(categories.items())),
        "distinct_techniques": len(techniques),
        "technique_coverage": dict(sorted(techniques.items())),
        "documents_with_techniques": with_techniques,
        "mean_trajectory_completeness": round(sum(completeness) / len(completeness), 4) if completeness else 0.0,
        "documents_with_failures": with_failures,
        "failure_correction_coverage": round(with_failures / len(unique), 4) if unique else 0.0,
        "provenance_completeness": round(_provenance_completeness(unique), 4),
    }


def _provenance_completeness(records: Sequence[KnowledgeRecord]) -> float:
    if not records:
        return 0.0
    fields = ("source_uri", "retrieved_at", "content_sha256", "document_path")
    scores = []
    for r in records:
        present = sum(1 for f in fields if getattr(r.provenance, f))
        # author is stored in provenance.extra
        present += 1 if r.provenance.extra.get("author") else 0
        scores.append(present / (len(fields) + 1))
    return sum(scores) / len(scores)


@dataclass(frozen=True)
class DuplicateMatch:
    new_record_id: str
    new_source: str
    duplicate_of: str
    similarity: float
    reason: str


def cross_corpus_duplicates(
    local_records: Sequence[KnowledgeRecord],
    new_records: Sequence[KnowledgeRecord],
    near_threshold: float = 0.9,
) -> Dict[str, object]:
    """Detect exact/near duplicates of new records against the local corpus.

    Provenance is never discarded: matches are reported, not dropped. The new record keeps its own
    provenance and is annotated with the local record it duplicates.
    """
    dedup = Deduplicator(near_threshold=near_threshold)
    for record in local_records:
        dedup.accept(record.record_id, record.content_hash, _dedup_text(record))
    matches: List[DuplicateMatch] = []
    for record in new_records:
        decision = dedup.evaluate(record.record_id, record.content_hash, _dedup_text(record))
        if decision.is_duplicate:
            matches.append(
                DuplicateMatch(
                    new_record_id=record.record_id,
                    new_source=record.provenance.source_uri,
                    duplicate_of=decision.duplicate_of or "",
                    similarity=decision.similarity,
                    reason=decision.reason,
                )
            )
    return {
        "local_records": len(local_records),
        "new_records": len(new_records),
        "duplicate_matches": [m.__dict__ for m in matches],
        "duplicate_count": len(matches),
        "duplicate_rate": round(len(matches) / len(new_records), 4) if new_records else 0.0,
        "provenance_preserved": True,
    }


def _dedup_text(record: KnowledgeRecord) -> str:
    return f"{record.title} {record.summary}"


def extraction_quality(
    records: Sequence[KnowledgeRecord],
    raw_texts_by_doc: Optional[Dict[str, str]] = None,
) -> Dict[str, object]:
    raw_texts_by_doc = raw_texts_by_doc or {}
    per_record = []
    field_counts: Dict[str, Counter] = {}

    for record in records:
        raw = raw_texts_by_doc.get(record.record_id, "")
        fields: Dict[str, str] = {}

        fields["event_challenge_metadata"] = EXPLICIT if (record.metadata.name or record.title) else MISSING
        # category: explicit if a "Category:" label exists in the source, else inferred if present.
        if record.metadata.category and raw and _CATEGORY_LABEL.search(raw):
            fields["category"] = EXPLICIT
        elif record.metadata.category:
            fields["category"] = INFERRED
        else:
            fields["category"] = MISSING
        fields["challenge_description_context"] = EXPLICIT if record.summary.strip() else MISSING
        fields["techniques_mechanisms"] = EXPLICIT if record.techniques else MISSING
        fields["failures_corrections"] = EXPLICIT if record.failures else MISSING

        present_kinds = {step.kind for step in record.trajectory.steps}
        for field, kind in _STAGE_FIELDS.items():
            fields[field] = EXPLICIT if kind in present_kinds else MISSING

        per_record.append({"record_id": record.record_id, "source": record.provenance.source_uri, "fields": fields})
        for field, verdict in fields.items():
            field_counts.setdefault(field, Counter())[verdict] += 1

    return {
        "record_count": len(records),
        "per_record": per_record,
        "field_summary": {field: dict(counts) for field, counts in sorted(field_counts.items())},
        "note": "reasoning stages are marked missing when absent; none are invented",
    }


def compare_corpora(local: Dict[str, object], new: Dict[str, object]) -> Dict[str, object]:
    def techniques(stats):
        return set(stats.get("technique_coverage", {}).keys())

    local_t, new_t = techniques(local), techniques(new)
    return {
        "documents": {"local": local["documents"], "jiaje": new["documents"]},
        "unique_challenges": {"local": local["unique_challenges"], "jiaje": new["unique_challenges"]},
        "categories": {"local": local["categories"], "jiaje": new["categories"]},
        "distinct_techniques": {"local": local["distinct_techniques"], "jiaje": new["distinct_techniques"]},
        "techniques_only_in_jiaje": sorted(new_t - local_t),
        "techniques_shared": sorted(new_t & local_t),
        "mean_trajectory_completeness": {
            "local": local["mean_trajectory_completeness"], "jiaje": new["mean_trajectory_completeness"]
        },
        "failure_correction_coverage": {
            "local": local["failure_correction_coverage"], "jiaje": new["failure_correction_coverage"]
        },
        "provenance_completeness": {
            "local": local["provenance_completeness"], "jiaje": new["provenance_completeness"]
        },
    }
