from __future__ import annotations

import json
from pathlib import Path

from ctf_ingest import CachedHttpSource
from ctf_ingest.models import SourceType


def _make_cache(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.txt").write_text("Category: web\n\nSSTI via jinja2 template injection {{7*7}}", encoding="utf-8")
    (root / "b.txt").write_text("Redbud Puppeteer", encoding="utf-8")
    manifest = {
        "source": "https://example.invalid/index.html",
        "author": "Test Author (@t)",
        "license_note": "test",
        "retrieved_at": "2026-09-25T00:00:00+00:00",
        "documents": [
            {"filename": "a.txt", "url": "https://example.invalid/a.html", "title": "A",
             "category_hint": "web", "retrieved_at": "2026-09-25T00:00:00+00:00",
             "sha256": "deadbeef", "has_static_content": True},
            {"filename": "b.txt", "url": "https://example.invalid/b.html", "title": "B",
             "category_hint": "misc", "retrieved_at": "2026-09-25T00:00:00+00:00",
             "sha256": "cafebabe", "has_static_content": False},
        ],
    }
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


def test_cached_http_source_yields_http_provenance(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path / "cache")
    docs = list(CachedHttpSource(cache).documents())
    assert len(docs) == 2
    a = next(d for d in docs if d.provenance.document_path == "a.txt")
    assert a.provenance.source_type is SourceType.HTTP
    assert a.provenance.source_uri == "https://example.invalid/a.html"
    assert a.provenance.retrieved_at == "2026-09-25T00:00:00+00:00"
    assert a.provenance.content_sha256  # carried from manifest
    assert a.provenance.extra["author"] == "Test Author (@t)"
    assert a.provenance.extra["has_static_content"] == "True"


def test_cached_http_source_empty_when_no_manifest(tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    assert list(CachedHttpSource(tmp_path / "empty").documents()) == []
