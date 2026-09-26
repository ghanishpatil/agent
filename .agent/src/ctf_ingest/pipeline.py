"""Ingestion pipeline orchestrator.

    source(s) -> normalize -> extract(metadata, techniques, trajectory, failures)
              -> deduplicate -> attach provenance -> knowledge store

The pipeline is deterministic given the same inputs and never mutates its sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .dedup import Deduplicator
from .extract import (
    extract_failures,
    extract_metadata,
    extract_techniques,
    extract_trajectory,
)
from .models import KnowledgeRecord, RawDocument
from .normalize import normalize
from .sources import Source
from .store import KnowledgeStore


@dataclass
class IngestReport:
    documents_seen: int = 0
    records_written: int = 0
    unique_records: int = 0
    duplicate_records: int = 0
    manifest: Dict[str, object] = field(default_factory=dict)
    duplicate_pairs: List[Dict[str, object]] = field(default_factory=list)


def build_record(document: RawDocument, dedup: Deduplicator) -> KnowledgeRecord:
    """Normalize + extract one document into a KnowledgeRecord (dedup linkage applied)."""
    writeup = normalize(document)
    metadata = extract_metadata(writeup)
    techniques = extract_techniques(writeup)
    trajectory = extract_trajectory(writeup)
    failures = extract_failures(writeup)
    content_hash = writeup.normalized_sha256
    record_id = document.doc_id
    decision = dedup.evaluate(record_id, content_hash, writeup.body_text)
    summary = writeup.body_text[:280]
    return KnowledgeRecord(
        record_id=record_id,
        content_hash=content_hash,
        provenance=writeup.provenance,
        metadata=metadata,
        techniques=techniques,
        trajectory=trajectory,
        failures=failures,
        title=writeup.title,
        summary=summary,
        duplicate_of=decision.duplicate_of,
    )


class IngestionPipeline:
    def __init__(self, near_threshold: float = 0.9) -> None:
        self.near_threshold = near_threshold

    def run(
        self,
        sources: Iterable[Source],
        store: Optional[KnowledgeStore] = None,
    ) -> tuple[List[KnowledgeRecord], IngestReport]:
        dedup = Deduplicator(near_threshold=self.near_threshold)
        records: List[KnowledgeRecord] = []
        report = IngestReport()
        for source in sources:
            for document in source.documents():
                report.documents_seen += 1
                record = build_record(document, dedup)
                if record.duplicate_of is None:
                    dedup.accept(record.record_id, record.content_hash, record.summary + record.title)
                    report.unique_records += 1
                else:
                    report.duplicate_records += 1
                    report.duplicate_pairs.append(
                        {"record_id": record.record_id, "duplicate_of": record.duplicate_of}
                    )
                records.append(record)
        report.records_written = len(records)
        if store is not None:
            report.manifest = store.write(records)
        return records, report


def ingest_local_directory(
    root: Path,
    store_root: Path,
    *,
    license_note: str = "",
    near_threshold: float = 0.9,
) -> IngestReport:
    """Convenience: ingest a local writeups directory into a knowledge store."""
    from .sources import LocalDirectorySource

    source = LocalDirectorySource(root, license_note=license_note)
    store = KnowledgeStore(store_root)
    _records, report = IngestionPipeline(near_threshold=near_threshold).run([source], store)
    return report
