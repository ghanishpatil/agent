"""Retrieval layer over the ingested knowledge store.

Deterministic, dependency-free ranking (no embeddings/vector index) so results are
reproducible and auditable. A record is scored against a query by three signals:

- category match          (coarse but strong when present)
- technique-keyword overlap (query terms vs a record's extracted technique keywords)
- token overlap            (query terms vs the record's title + summary + technique names)

The retriever is read-only and advisory: it selects and ranks knowledge; it never
executes anything, mutates evidence, or verifies flags. Consumers (the A/B harness)
feed selected records through the solver's existing advisory-memory boundary only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .models import KnowledgeRecord
from .store import KnowledgeStore

_TOKEN = re.compile(r"[a-z0-9]{3,}")

_STOPWORDS = frozenset(
    {
        "the", "and", "for", "with", "that", "this", "was", "are", "were", "our", "not",
        "but", "you", "your", "from", "into", "have", "has", "had", "will", "can", "use",
        "used", "using", "given", "which", "they", "them", "then", "than", "may", "get",
        "got", "some", "any", "all", "one", "two", "also", "how", "what", "when", "why",
        "challenge", "flag", "ctf", "writeup", "solution", "task",
    }
)


def _tokens(text: str) -> List[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


@dataclass(frozen=True)
class RetrievalQuery:
    text: str = ""
    category: str = ""
    keywords: Tuple[str, ...] = ()

    def terms(self) -> Set[str]:
        terms = set(_tokens(self.text))
        terms.update(t for kw in self.keywords for t in _tokens(kw))
        return terms


@dataclass(frozen=True)
class RetrievalResult:
    record: KnowledgeRecord
    score: float
    matched_terms: Tuple[str, ...] = ()
    category_match: bool = False


@dataclass
class KnowledgeRetriever:
    """Ranks ingested KnowledgeRecords for a query. Build via ``from_records``/``from_store``."""

    records: Tuple[KnowledgeRecord, ...]
    category_weight: float = 3.0
    technique_weight: float = 2.0
    token_weight: float = 1.0
    _index: List[Tuple[KnowledgeRecord, Set[str], Set[str], str]] = field(
        default_factory=list, repr=False
    )

    def __post_init__(self) -> None:
        self._index = []
        for record in self.records:
            technique_terms: Set[str] = set()
            for technique in record.techniques:
                technique_terms.update(_tokens(technique.name))
                for keyword in technique.keywords:
                    technique_terms.update(_tokens(keyword))
            doc_terms = set(_tokens(record.title))
            doc_terms.update(_tokens(record.summary))
            doc_terms.update(technique_terms)
            for step in record.trajectory.steps:
                doc_terms.update(_tokens(step.text))
            self._index.append(
                (record, doc_terms, technique_terms, (record.metadata.category or "").lower())
            )

    @classmethod
    def from_records(cls, records: Iterable[KnowledgeRecord], **kwargs) -> "KnowledgeRetriever":
        # Exclude near/exact duplicates from the searchable set; they add no new knowledge.
        unique = tuple(r for r in records if r.duplicate_of is None)
        return cls(records=unique, **kwargs)

    @classmethod
    def from_store(cls, store: KnowledgeStore, **kwargs) -> "KnowledgeRetriever":
        return cls.from_records(records_from_store(store), **kwargs)

    def retrieve(self, query: RetrievalQuery, k: int = 5) -> Tuple[RetrievalResult, ...]:
        query_terms = query.terms()
        query_category = (query.category or "").lower()
        scored: List[RetrievalResult] = []
        for record, doc_terms, technique_terms, category in self._index:
            matched = query_terms & doc_terms
            technique_hits = query_terms & technique_terms
            category_match = bool(query_category) and query_category == category
            score = (
                self.category_weight * (1.0 if category_match else 0.0)
                + self.technique_weight * len(technique_hits)
                + self.token_weight * len(matched)
            )
            if score <= 0.0:
                continue
            scored.append(
                RetrievalResult(
                    record=record,
                    score=round(score, 3),
                    matched_terms=tuple(sorted(matched)),
                    category_match=category_match,
                )
            )
        scored.sort(key=lambda r: (r.score, r.record.record_id), reverse=True)
        return tuple(scored[:k])


# --------------------------------------------------------------------------------------
# Rehydrate KnowledgeRecord from a stored dict (store.read_all yields plain dicts).
# --------------------------------------------------------------------------------------

from .models import (  # noqa: E402  (kept local to avoid a heavy import at module top)
    ChallengeMetadata,
    FailureCorrection,
    Provenance,
    ReasoningTrajectory,
    SourceType,
    Technique,
    TrajectoryStep,
    TrajectoryStepKind,
)


def records_from_store(store: KnowledgeStore) -> Tuple[KnowledgeRecord, ...]:
    """Rehydrate all KnowledgeRecords (including duplicates) from a persisted store."""
    return tuple(_record_from_dict(row) for row in store.read_all())


def _record_from_dict(row: Dict) -> KnowledgeRecord:
    prov = row.get("provenance", {})
    meta = row.get("metadata", {})
    traj = row.get("trajectory", {}) or {}
    return KnowledgeRecord(
        record_id=row["record_id"],
        content_hash=row.get("content_hash", ""),
        provenance=Provenance(
            source_type=SourceType(prov.get("source_type", "LOCAL_DIRECTORY")),
            source_uri=prov.get("source_uri", ""),
            document_path=prov.get("document_path", ""),
            retrieved_at=prov.get("retrieved_at", ""),
            revision=prov.get("revision", ""),
            content_sha256=prov.get("content_sha256", ""),
            license_note=prov.get("license_note", ""),
            extra=dict(prov.get("extra", {})),
        ),
        metadata=ChallengeMetadata(
            name=meta.get("name", ""),
            category=meta.get("category", ""),
            event=meta.get("event", ""),
            points=meta.get("points"),
            difficulty=meta.get("difficulty", ""),
            flag_format=meta.get("flag_format", ""),
            flags=tuple(meta.get("flags", [])),
            tags=tuple(meta.get("tags", [])),
        ),
        techniques=tuple(
            Technique(
                technique_id=t["technique_id"],
                name=t.get("name", ""),
                category=t.get("category", ""),
                keywords=tuple(t.get("keywords", [])),
                confidence=float(t.get("confidence", 0.0)),
                evidence=t.get("evidence", ""),
            )
            for t in row.get("techniques", [])
        ),
        trajectory=ReasoningTrajectory(
            steps=tuple(
                TrajectoryStep(
                    order=s.get("order", i),
                    kind=TrajectoryStepKind(s["kind"]),
                    text=s.get("text", ""),
                    confidence=float(s.get("confidence", 0.0)),
                    source_heading=s.get("source_heading", ""),
                )
                for i, s in enumerate(traj.get("steps", []))
            ),
            completeness=float(traj.get("completeness", 0.0)),
        ),
        failures=tuple(
            FailureCorrection(
                failed_approach=f.get("failed_approach", ""),
                failure_reason=f.get("failure_reason", ""),
                correction=f.get("correction", ""),
                confidence=float(f.get("confidence", 0.0)),
            )
            for f in row.get("failures", [])
        ),
        title=row.get("title", ""),
        summary=row.get("summary", ""),
        schema_version=row.get("schema_version", "1.0"),
        duplicate_of=row.get("duplicate_of"),
    )
