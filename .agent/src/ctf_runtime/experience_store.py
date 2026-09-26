"""ExperienceRecord + append-only experience store (Continuous Experience Learning).

This is ADDITIVE and lives entirely in ``ctf_runtime``. It never imports or mutates the frozen
solver, and it writes ONLY under ``knowledge/agent_experience_v1/`` — the external corpora
(jiaje/redbud/domectf/local_writeups) and their A/B artifacts are never touched.

An ``ExperienceRecord`` is a neutral, JSON-serialisable derived artifact grounded in the
authoritative ``SolveResult`` + runtime journals. It is not authoritative over any runtime evidence;
it is future retrieval input only (translated later by a separate knowledge_translation step).
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXPERIENCE_SCHEMA_VERSION = "1.0"

# Distinct provenance kinds so retrieval can always tell experiences apart from external writeups.
SOURCE_SUCCESS = "AGENT_SUCCESS_EXPERIENCE"
SOURCE_FAILURE = "AGENT_FAILURE_EXPERIENCE"

RECORDS_FILE = "records.jsonl"
MANIFEST_FILE = "manifest.json"


@dataclass(frozen=True)
class ExperienceProvenance:
    """Where a derived experience came from; enough to trace back to authoritative runtime state."""

    run_id: str
    session_id: str
    driver: str                       # "internal" | "kiro"
    source_kind: str                  # SOURCE_SUCCESS | SOURCE_FAILURE
    journal_path: str = ""
    verification_evidence_ids: Tuple[str, ...] = ()
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperienceRecord:
    """A neutral, grounded record of one terminal challenge attempt (success or failure)."""

    record_id: str
    source_kind: str                  # SOURCE_SUCCESS | SOURCE_FAILURE
    status: str                       # SolveStatus value (SOLVED / BLOCKED / EXHAUSTED / ...)
    provenance: ExperienceProvenance
    challenge_name: str = ""
    category: str = ""
    # reasoning / trajectory (all grounded in SolveResult traces + journal)
    mechanism: str = ""
    techniques: Tuple[str, ...] = ()
    preconditions: Tuple[str, ...] = ()
    hypotheses: Tuple[Dict[str, Any], ...] = ()          # {id, statement, status}
    hypothesis_transitions: Tuple[Dict[str, Any], ...] = ()  # {hypothesis_id, from?, to, impact}
    discriminating_tests: Tuple[Dict[str, Any], ...] = ()    # {tool, target, objective, observation_class}
    successful_actions: Tuple[Dict[str, Any], ...] = ()
    dead_end_actions: Tuple[Dict[str, Any], ...] = ()
    failure_classes: Tuple[str, ...] = ()                # ResultClass values encountered
    useful_observations: Tuple[Dict[str, Any], ...] = ()
    evidence_refs: Tuple[str, ...] = ()                  # evidence_ids
    disproven: Tuple[str, ...] = ()                      # ONLY authoritative DISPROVES hypotheses
    unresolved: Tuple[str, ...] = ()                     # unresolved hypotheses (kept as unresolved)
    unresolved_blockers: Tuple[str, ...] = ()
    terminal_reason: str = ""
    verification_method: str = ""                        # only for success
    solution_path: str = ""                              # only for success (grounded summary)
    verified_flag: Optional[str] = None                  # ONLY for success; from SolveResult
    writeup_ref: str = ""                                # path to persisted writeup (success)
    writeup_grounded: Optional[bool] = None
    schema_version: str = EXPERIENCE_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data

    def content_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ExperienceStore:
    """Append-only JSONL store + manifest, mirroring the external KnowledgeStore auditable pattern.

    Appends use ``O_APPEND | O_CREAT`` under a process lock so concurrent sessions cannot interleave
    partial lines. Success and failure live in separate subdirectories so their baselines never mix.
    """

    _locks: Dict[str, threading.Lock] = {}
    _locks_guard = threading.Lock()

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._records_path = self.root / RECORDS_FILE
        self._manifest_path = self.root / MANIFEST_FILE

    @classmethod
    def for_kind(cls, base_root: Path, source_kind: str) -> "ExperienceStore":
        sub = "success" if source_kind == SOURCE_SUCCESS else "failure"
        return cls(Path(base_root) / sub)

    def _lock(self) -> threading.Lock:
        key = str(self._records_path.resolve())
        with ExperienceStore._locks_guard:
            lock = ExperienceStore._locks.get(key)
            if lock is None:
                lock = threading.Lock()
                ExperienceStore._locks[key] = lock
            return lock

    def append(self, record: ExperienceRecord) -> Dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        line = (json.dumps(record.to_dict(), sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        with self._lock():
            fd = os.open(str(self._records_path), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
            try:
                os.write(fd, line)
            finally:
                os.close(fd)
            return self._rebuild_manifest()

    def _rebuild_manifest(self) -> Dict[str, Any]:
        raw = self._records_path.read_bytes() if self._records_path.exists() else b""
        count = sum(1 for ln in raw.splitlines() if ln.strip())
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": EXPERIENCE_SCHEMA_VERSION,
            "total_records": count,
            "records_sha256": hashlib.sha256(raw).hexdigest(),
        }
        self._manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        return manifest

    def read_all(self) -> List[Dict[str, Any]]:
        if not self._records_path.exists():
            return []
        out = []
        for ln in self._records_path.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                out.append(json.loads(ln))
        return out

    def read_manifest(self) -> Dict[str, Any]:
        if not self._manifest_path.exists():
            return {}
        return json.loads(self._manifest_path.read_text(encoding="utf-8"))
