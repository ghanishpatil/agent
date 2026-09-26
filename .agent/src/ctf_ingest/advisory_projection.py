"""Project ingested knowledge into the solver's existing AdvisoryMemory on-disk format.

The frozen solver reads advisory memory from a directory via ``AdvisoryMemory`` with these
relative files:
    knowledge/technique_memory.jsonl
    trajectories/trajectories.jsonl
    tools/tool_memory.jsonl
    failures/failures.jsonl

This module converts ``KnowledgeRecord``s into technique + trajectory rows in that schema,
and builds an *augmented* memory directory that layers external knowledge on top of a COPY
of an existing audit corpus. The source audit tree is never modified (it is copied first).

Projected rows are advisory-only by construction: they enter the solver solely through the
``AdvisoryMemory`` boundary, whose ``AdvisoryBundle`` can never become a hypothesis, action,
or evidence. We do not synthesise ``cheap_tests``/``discriminating_tests`` — fabricating
tests would risk steering the solver on unverified guesses — so those remain empty.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Sequence

from .models import KnowledgeRecord, TrajectoryStepKind

TECHNIQUE_REL = Path("knowledge/technique_memory.jsonl")
TRAJECTORY_REL = Path("trajectories/trajectories.jsonl")


def _confidence_label(value: float) -> str:
    if value >= 0.8:
        return "external:high"
    if value >= 0.55:
        return "external:medium"
    return "external:low"


def project_technique_rows(records: Sequence[KnowledgeRecord]) -> List[Dict]:
    rows: List[Dict] = []
    for record in records:
        if record.duplicate_of is not None:
            continue
        example = f"{record.title} [{record.provenance.document_path or record.provenance.source_uri}]"
        for technique in record.techniques:
            rows.append(
                {
                    "id": f"EXT-{record.record_id}-{technique.technique_id}",
                    "technique": technique.name,
                    "category": technique.category or record.metadata.category,
                    "confidence": _confidence_label(technique.confidence),
                    "indicators": list(technique.keywords),
                    "cheap_tests": [],
                    "discriminating_tests": [],
                    "examples": [example],
                    "advisory_source": "external_writeups",
                }
            )
    return rows


def _key_insight(record: KnowledgeRecord) -> str:
    priority = (
        TrajectoryStepKind.EXPLOIT_SOLUTION,
        TrajectoryStepKind.INTERPRETATION,
        TrajectoryStepKind.HYPOTHESIS,
    )
    for kind in priority:
        for step in record.trajectory.steps:
            if step.kind is kind and step.text:
                return step.text
    return record.summary[:200]


def project_trajectory_rows(records: Sequence[KnowledgeRecord]) -> List[Dict]:
    rows: List[Dict] = []
    for record in records:
        if record.duplicate_of is not None or not record.trajectory.steps:
            continue
        rows.append(
            {
                "id": f"EXT-{record.record_id}",
                "challenge": record.title,
                "category": record.metadata.category,
                "key_insight": _key_insight(record),
                "generalizes": ", ".join(t.name for t in record.techniques),
                "source": record.provenance.document_path or record.provenance.source_uri,
                "advisory_source": "external_writeups",
            }
        )
    return rows


def write_external_memory(records: Sequence[KnowledgeRecord], dest: Path) -> Path:
    """Write a fresh advisory-memory dir containing ONLY the projected external knowledge."""
    dest = Path(dest)
    (dest / "knowledge").mkdir(parents=True, exist_ok=True)
    (dest / "trajectories").mkdir(parents=True, exist_ok=True)
    _write_jsonl(dest / TECHNIQUE_REL, project_technique_rows(records))
    _write_jsonl(dest / TRAJECTORY_REL, project_trajectory_rows(records))
    return dest


def build_augmented_memory(
    audit_root: Path, records: Sequence[KnowledgeRecord], dest: Path
) -> Path:
    """Copy ``audit_root`` to ``dest`` then append external knowledge rows.

    ``audit_root`` is treated as read-only and is never modified. If ``audit_root`` does not
    exist, an external-only memory dir is produced instead.
    """
    audit_root = Path(audit_root)
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    if audit_root.is_dir():
        shutil.copytree(audit_root, dest)
    else:
        dest.mkdir(parents=True, exist_ok=True)
    (dest / "knowledge").mkdir(parents=True, exist_ok=True)
    (dest / "trajectories").mkdir(parents=True, exist_ok=True)
    _append_jsonl(dest / TECHNIQUE_REL, project_technique_rows(records))
    _append_jsonl(dest / TRAJECTORY_REL, project_trajectory_rows(records))
    return dest


def _write_jsonl(path: Path, rows: Sequence[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )


def _append_jsonl(path: Path, rows: Sequence[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    addition = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    path.write_text(existing + addition, encoding="utf-8")
