from __future__ import annotations

from pathlib import Path

from ctf_ingest.dedup import Deduplicator, jaccard, tokenize
from ctf_ingest.models import (
    ChallengeMetadata,
    KnowledgeRecord,
    Provenance,
    ReasoningTrajectory,
    SourceType,
)
from ctf_ingest.store import KnowledgeStore


def test_jaccard_bounds() -> None:
    assert jaccard(set(), set()) == 1.0
    assert jaccard({"a"}, set()) == 0.0
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_exact_duplicate_detected() -> None:
    dedup = Deduplicator()
    first = dedup.evaluate("r1", "hashA", "some text about xor cipher")
    assert not first.is_duplicate
    dedup.accept("r1", "hashA", "some text about xor cipher")
    second = dedup.evaluate("r2", "hashA", "different text entirely")
    assert second.is_duplicate
    assert second.duplicate_of == "r1"
    assert second.reason == "exact content hash"


def test_near_duplicate_detected_by_token_overlap() -> None:
    dedup = Deduplicator(near_threshold=0.8)
    base = "the server side template injection evaluated seven times seven equals fortynine"
    dedup.accept("r1", "h1", base)
    near = base + " extra"
    decision = dedup.evaluate("r2", "h2", near)
    assert decision.is_duplicate
    assert decision.duplicate_of == "r1"
    assert decision.similarity >= 0.8


def test_unique_document_not_flagged() -> None:
    dedup = Deduplicator(near_threshold=0.9)
    dedup.accept("r1", "h1", "buffer overflow rop chain gadget libc")
    decision = dedup.evaluate("r2", "h2", "classical caesar cipher rotation alphabet")
    assert not decision.is_duplicate
    assert decision.duplicate_of is None


def _record(record_id: str, category: str, duplicate_of=None) -> KnowledgeRecord:
    return KnowledgeRecord(
        record_id=record_id,
        content_hash=f"hash-{record_id}",
        provenance=Provenance(SourceType.LOCAL_DIRECTORY, "uri", f"{record_id}.md"),
        metadata=ChallengeMetadata(name=record_id, category=category),
        trajectory=ReasoningTrajectory(completeness=0.5),
        duplicate_of=duplicate_of,
    )


def test_store_writes_records_and_manifest(tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path / "kstore")
    manifest = store.write(
        [
            _record("r1", "web"),
            _record("r2", "crypto"),
            _record("r3", "web", duplicate_of="r1"),
        ]
    )
    assert manifest["total_records"] == 3
    assert manifest["unique_records"] == 2
    assert manifest["duplicate_records"] == 1
    assert manifest["by_category"] == {"crypto": 1, "web": 1}
    assert manifest["records_sha256"]

    rows = list(store.read_all())
    assert len(rows) == 3
    assert store.read_manifest()["unique_records"] == 2
