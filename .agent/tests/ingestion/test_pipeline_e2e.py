from __future__ import annotations

import shutil
from pathlib import Path

from ctf_ingest import IngestionPipeline, KnowledgeStore, LocalDirectorySource
from ctf_ingest.pipeline import ingest_local_directory


def test_end_to_end_ingest_produces_store_with_provenance(writeups_dir: Path, tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path / "kstore")
    source = LocalDirectorySource(writeups_dir, license_note="test-corpus")
    records, report = IngestionPipeline().run([source], store)

    assert report.documents_seen == 3
    assert report.records_written == 3
    assert report.unique_records == 3
    assert report.duplicate_records == 0

    # Every record keeps provenance and at least the web one has a full-ish trajectory.
    assert all(r.provenance.document_path for r in records)
    web = next(r for r in records if r.metadata.category == "web")
    assert web.metadata.flags == ("CTF{ssti_is_fun}",)
    assert web.trajectory.completeness > 0.0
    assert any(t.technique_id == "ssti" for t in web.techniques)

    manifest = store.read_manifest()
    assert manifest["unique_records"] == 3
    assert "web" in manifest["by_category"]
    assert manifest["records_with_failures"] >= 1  # crypto writeup has a base64 dead-end


def test_duplicate_writeup_is_linked_not_dropped(writeups_dir: Path, tmp_path: Path) -> None:
    # Duplicate one writeup verbatim into another folder.
    dup_dir = writeups_dir / "mirror"
    dup_dir.mkdir()
    shutil.copyfile(writeups_dir / "web" / "ssti.md", dup_dir / "ssti_copy.md")

    store = KnowledgeStore(tmp_path / "kstore")
    _records, report = IngestionPipeline().run(
        [LocalDirectorySource(writeups_dir)], store
    )
    assert report.documents_seen == 4
    assert report.duplicate_records == 1
    assert report.unique_records == 3
    assert report.duplicate_pairs and report.duplicate_pairs[0]["duplicate_of"]


def test_convenience_ingest_local_directory(writeups_dir: Path, tmp_path: Path) -> None:
    report = ingest_local_directory(writeups_dir, tmp_path / "kstore2", license_note="corpus")
    assert report.records_written == 3
    assert report.manifest["unique_records"] == 3
