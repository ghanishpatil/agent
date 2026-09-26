from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ctf_ingest.advisory_projection import (
    build_augmented_memory,
    project_technique_rows,
    project_trajectory_rows,
    write_external_memory,
)


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).replace("\\", "/").encode())
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def test_projected_technique_rows_match_advisory_schema(labeled_corpus) -> None:
    rows = project_technique_rows(labeled_corpus)
    assert rows
    row = rows[0]
    for key in ("id", "technique", "category", "confidence", "indicators", "cheap_tests", "discriminating_tests", "examples"):
        assert key in row
    # We never fabricate tests.
    assert row["cheap_tests"] == []
    assert row["discriminating_tests"] == []
    assert row["confidence"].startswith("external:")


def test_projected_trajectory_rows_carry_source_and_insight(labeled_corpus) -> None:
    rows = project_trajectory_rows(labeled_corpus)
    # Only records with trajectory steps are projected.
    assert all(r["source"] for r in rows)
    assert all(r["advisory_source"] == "external_writeups" for r in rows)


def test_write_external_memory_creates_advisory_files(labeled_corpus, tmp_path: Path) -> None:
    dest = write_external_memory(labeled_corpus, tmp_path / "ext")
    tech = (dest / "knowledge" / "technique_memory.jsonl").read_text(encoding="utf-8")
    assert tech.strip()
    for line in tech.splitlines():
        json.loads(line)  # each line is valid JSON


def test_build_augmented_memory_does_not_mutate_audit(labeled_corpus, tmp_path: Path) -> None:
    # Construct a fake audit tree and confirm it is untouched after augmentation.
    audit = tmp_path / "audit"
    (audit / "knowledge").mkdir(parents=True)
    (audit / "trajectories").mkdir(parents=True)
    (audit / "knowledge" / "technique_memory.jsonl").write_text(
        json.dumps({"id": "T-1", "technique": "orig", "category": "web", "indicators": []}) + "\n",
        encoding="utf-8",
    )
    (audit / "trajectories" / "trajectories.jsonl").write_text("", encoding="utf-8")
    before = _tree_hash(audit)

    dest = build_augmented_memory(audit, labeled_corpus, tmp_path / "aug")
    after = _tree_hash(audit)
    assert before == after  # audit tree is read-only

    # Augmented tree keeps the original row AND adds external rows.
    aug_tech = (dest / "knowledge" / "technique_memory.jsonl").read_text(encoding="utf-8")
    assert '"technique": "orig"' in aug_tech or '"technique":"orig"' in aug_tech
    assert "external_writeups" in aug_tech
    assert len(aug_tech.strip().splitlines()) > 1


def test_build_augmented_memory_without_audit_produces_external_only(labeled_corpus, tmp_path: Path) -> None:
    dest = build_augmented_memory(tmp_path / "missing_audit", labeled_corpus, tmp_path / "aug2")
    tech = (dest / "knowledge" / "technique_memory.jsonl").read_text(encoding="utf-8")
    assert "external_writeups" in tech
