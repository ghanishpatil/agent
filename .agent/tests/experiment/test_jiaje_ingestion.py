from __future__ import annotations

from pathlib import Path

import pytest

from ctf_ingest import CachedHttpSource, IngestionPipeline, KnowledgeStore
from ctf_ingest.models import SourceType

CACHE = Path(__file__).resolve().parents[2] / "knowledge" / "_jiaje_cache"

pytestmark = pytest.mark.skipif(
    not (CACHE / "manifest.json").exists(), reason="Jia Jie cache not present"
)


def _ingest(tmp_path: Path):
    store = KnowledgeStore(tmp_path / "jiaje")
    records, report = IngestionPipeline().run([CachedHttpSource(CACHE)], store)
    return records, report


def test_jiaje_ingestion_is_deterministic_and_has_http_provenance(tmp_path: Path) -> None:
    r1, rep1 = _ingest(tmp_path / "a")
    r2, _ = _ingest(tmp_path / "b")
    assert rep1.documents_seen == 4
    assert [r.record_id for r in r1] == [r.record_id for r in r2]  # deterministic ids
    assert [r.content_hash for r in r1] == [r.content_hash for r in r2]
    for r in r1:
        assert r.provenance.source_type is SourceType.HTTP
        assert r.provenance.source_uri.startswith("https://jia.je/ctf-writeups/")
        assert r.provenance.retrieved_at
        assert r.provenance.content_sha256
        assert r.provenance.extra.get("author") == "Jiajie Chen (@jiegec)"


def test_jiaje_rich_pages_extract_techniques_but_no_invented_trajectory(tmp_path: Path) -> None:
    records, _ = _ingest(tmp_path)
    by_src = {r.provenance.source_uri.split("/")[-1]: r for r in records}
    solution = by_src.get("solution.html")
    assert solution is not None
    # The technique taxonomy yields broad technique coverage...
    assert len(solution.techniques) >= 5
    # ...but it is a catalog, not a solve narrative: trajectory stays sparse (not fabricated).
    assert solution.trajectory.completeness < 0.5
    # JS-only pages carry provenance but little/no extracted content.
    empty = by_src.get("index.html")
    if empty is not None:
        assert empty.techniques == ()
