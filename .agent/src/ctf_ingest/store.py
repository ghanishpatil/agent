"""Knowledge store persistence: append-only JSONL records + a manifest with integrity.

The store is a plain, auditable directory:
    <root>/records.jsonl   one KnowledgeRecord per line (JSON)
    <root>/manifest.json   counts, provenance summary, schema version, sha256 of records

Records retain full provenance so every fact is traceable to a source document.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List

from .models import INGEST_SCHEMA_VERSION, KnowledgeRecord

RECORDS_FILE = "records.jsonl"
MANIFEST_FILE = "manifest.json"


@dataclass
class KnowledgeStore:
    root: Path
    _records_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self._records_path = self.root / RECORDS_FILE

    # -- writing -----------------------------------------------------------------
    def write(self, records: Iterable[KnowledgeRecord]) -> Dict[str, object]:
        self.root.mkdir(parents=True, exist_ok=True)
        materialized: List[KnowledgeRecord] = list(records)
        lines = [json.dumps(record.to_dict(), sort_keys=True) for record in materialized]
        self._records_path.write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )
        manifest = self._build_manifest(materialized)
        (self.root / MANIFEST_FILE).write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        return manifest

    def _build_manifest(self, records: List[KnowledgeRecord]) -> Dict[str, object]:
        unique = [r for r in records if r.duplicate_of is None]
        duplicates = [r for r in records if r.duplicate_of is not None]
        category_counts = Counter(r.metadata.category or "unknown" for r in unique)
        technique_counts: Counter = Counter()
        source_counts: Counter = Counter()
        trajectory_completeness = []
        for record in unique:
            for technique in record.techniques:
                technique_counts[technique.technique_id] += 1
            source_counts[record.provenance.source_type.value] += 1
            trajectory_completeness.append(record.trajectory.completeness)
        records_bytes = self._records_path.read_bytes() if self._records_path.exists() else b""
        avg_completeness = (
            round(sum(trajectory_completeness) / len(trajectory_completeness), 3)
            if trajectory_completeness
            else 0.0
        )
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": INGEST_SCHEMA_VERSION,
            "total_records": len(records),
            "unique_records": len(unique),
            "duplicate_records": len(duplicates),
            "records_sha256": hashlib.sha256(records_bytes).hexdigest(),
            "by_category": dict(sorted(category_counts.items())),
            "by_source_type": dict(sorted(source_counts.items())),
            "by_technique": dict(sorted(technique_counts.items())),
            "records_with_failures": sum(1 for r in unique if r.failures),
            "average_trajectory_completeness": avg_completeness,
        }

    # -- reading -----------------------------------------------------------------
    def read_all(self) -> Iterator[Dict[str, object]]:
        if not self._records_path.exists():
            return
        for line in self._records_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                yield json.loads(line)

    def read_manifest(self) -> Dict[str, object]:
        path = self.root / MANIFEST_FILE
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
