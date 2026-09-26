"""Ingestion source adapters (the crawler layer).

Each adapter yields ``RawDocument`` objects with attached ``Provenance``. Supported:

- ``LocalDirectorySource``  — walk a local tree of writeups (read-only).
- ``GitRepositorySource``   — clone a public repo (e.g. a Jia Jie mirror) then walk it.
- ``HttpSource``            — pluggable single-URL fetch; requires an explicit fetcher
                              callable, so nothing is scraped implicitly.

Adapters never modify their inputs. The local writeups tree is treated as read-only.
"""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Iterator, Optional, Protocol, Sequence

from .models import MediaType, Provenance, RawDocument, SourceType

DEFAULT_EXTENSIONS = (".md", ".markdown", ".txt", ".rst", ".html", ".htm")

_MEDIA_BY_SUFFIX = {
    ".md": MediaType.MARKDOWN,
    ".markdown": MediaType.MARKDOWN,
    ".rst": MediaType.MARKDOWN,
    ".txt": MediaType.TEXT,
    ".html": MediaType.HTML,
    ".htm": MediaType.HTML,
}


def media_type_for(path: Path) -> MediaType:
    return _MEDIA_BY_SUFFIX.get(path.suffix.lower(), MediaType.UNKNOWN)


def _doc_id(source_uri: str, relpath: str) -> str:
    return hashlib.sha256(f"{source_uri}::{relpath}".encode("utf-8")).hexdigest()[:16]


def _read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        try:
            return path.read_bytes().decode("utf-8", "replace")
        except OSError:
            return None


class Source(Protocol):
    """A crawler source that yields raw writeup documents."""

    def documents(self) -> Iterator[RawDocument]:
        ...


class LocalDirectorySource:
    def __init__(
        self,
        root: Path,
        *,
        extensions: Sequence[str] = DEFAULT_EXTENSIONS,
        source_uri: Optional[str] = None,
        license_note: str = "",
        revision: str = "",
    ) -> None:
        self.root = Path(root)
        self.extensions = tuple(e.lower() for e in extensions)
        self.source_uri = source_uri or self.root.as_uri() if self.root.exists() else str(self.root)
        self.license_note = license_note
        self.revision = revision

    def documents(self) -> Iterator[RawDocument]:
        if not self.root.is_dir():
            return
        retrieved_at = datetime.now(timezone.utc).isoformat()
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in self.extensions:
                continue
            text = _read_text(path)
            if text is None:
                continue
            relpath = str(path.relative_to(self.root)).replace("\\", "/")
            content_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
            yield RawDocument(
                doc_id=_doc_id(self.source_uri, relpath),
                media_type=media_type_for(path),
                text=text,
                byte_length=len(text.encode("utf-8")),
                provenance=Provenance(
                    source_type=SourceType.LOCAL_DIRECTORY,
                    source_uri=self.source_uri,
                    document_path=relpath,
                    retrieved_at=retrieved_at,
                    revision=self.revision,
                    content_sha256=content_sha,
                    license_note=self.license_note,
                ),
            )


class GitRepositorySource:
    """Clone a git repository (shallow) into a temp dir, then walk it as a local source.

    Nothing is fetched until ``documents()`` is iterated. Requires ``git`` on PATH. If the
    clone fails, no documents are yielded (the error is surfaced via ``last_error``).
    """

    def __init__(
        self,
        repo_url: str,
        *,
        extensions: Sequence[str] = DEFAULT_EXTENSIONS,
        license_note: str = "",
        git_runner: Optional[Callable[[Sequence[str], Path], str]] = None,
    ) -> None:
        self.repo_url = repo_url
        self.extensions = tuple(e.lower() for e in extensions)
        self.license_note = license_note
        self._git_runner = git_runner or _default_git_runner
        self.last_error: str = ""

    def _resolve_revision(self, checkout: Path) -> str:
        try:
            return self._git_runner(["rev-parse", "HEAD"], checkout).strip()
        except Exception:  # noqa: BLE001 - revision is best-effort provenance
            return ""

    def documents(self) -> Iterator[RawDocument]:
        with tempfile.TemporaryDirectory(prefix="ctf_ingest_git_") as tmp:
            checkout = Path(tmp) / "repo"
            try:
                self._git_runner(
                    ["clone", "--depth", "1", self.repo_url, str(checkout)], Path(tmp)
                )
            except Exception as exc:  # noqa: BLE001 - clone failure must not crash pipeline
                self.last_error = str(exc)
                return
            revision = self._resolve_revision(checkout)
            local = LocalDirectorySource(
                checkout,
                extensions=self.extensions,
                source_uri=self.repo_url,
                license_note=self.license_note,
                revision=revision,
            )
            for document in local.documents():
                # Rewrite the provenance source type to GIT_REPOSITORY.
                provenance = Provenance(
                    source_type=SourceType.GIT_REPOSITORY,
                    source_uri=self.repo_url,
                    document_path=document.provenance.document_path,
                    retrieved_at=document.provenance.retrieved_at,
                    revision=revision,
                    content_sha256=document.provenance.content_sha256,
                    license_note=self.license_note,
                )
                yield RawDocument(
                    doc_id=document.doc_id,
                    media_type=document.media_type,
                    text=document.text,
                    byte_length=document.byte_length,
                    provenance=provenance,
                )


class HttpSource:
    """Single/multi URL source. A fetcher must be supplied explicitly; no implicit scraping.

    ``fetcher(url) -> str`` returns the document body. This keeps network egress an explicit,
    caller-controlled decision (honouring the project's no-silent-scraping constraint).
    """

    def __init__(
        self,
        urls: Iterable[str],
        fetcher: Callable[[str], str],
        *,
        media_type: MediaType = MediaType.HTML,
        license_note: str = "",
    ) -> None:
        self.urls = tuple(urls)
        self.fetcher = fetcher
        self.media_type = media_type
        self.license_note = license_note

    def documents(self) -> Iterator[RawDocument]:
        retrieved_at = datetime.now(timezone.utc).isoformat()
        for url in self.urls:
            text = self.fetcher(url)
            content_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
            yield RawDocument(
                doc_id=_doc_id(url, ""),
                media_type=self.media_type,
                text=text,
                byte_length=len(text.encode("utf-8")),
                provenance=Provenance(
                    source_type=SourceType.HTTP,
                    source_uri=url,
                    retrieved_at=retrieved_at,
                    content_sha256=content_sha,
                    license_note=self.license_note,
                ),
            )


class CachedHttpSource:
    """Emit HTTP-provenance documents from a locally cached fetch.

    The cache directory holds one text file per fetched page plus a ``manifest.json`` recording,
    per document, the original URL, retrieval timestamp, sha256, title, author, and whether the
    page had static (non-JS) content. This lets ingestion carry true HTTP provenance (source URL,
    author, retrieved_at, content hash) without the pipeline itself performing network I/O — the
    fetch is an explicit, recorded, out-of-band step (no implicit scraping).
    """

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = Path(cache_dir)

    def _manifest(self) -> dict:
        path = self.cache_dir / "manifest.json"
        if not path.exists():
            return {}
        import json

        return json.loads(path.read_text(encoding="utf-8"))

    def documents(self) -> Iterator[RawDocument]:
        manifest = self._manifest()
        author = str(manifest.get("author", ""))
        license_note = str(manifest.get("license_note", ""))
        source_index = str(manifest.get("source", ""))
        for entry in manifest.get("documents", ()):
            filename = entry.get("filename", "")
            file_path = self.cache_dir / filename
            text = _read_text(file_path)
            if text is None:
                continue
            content_sha = entry.get("sha256") or hashlib.sha256(text.encode("utf-8")).hexdigest()
            yield RawDocument(
                doc_id=_doc_id(entry.get("url", filename), filename),
                media_type=MediaType.TEXT,
                text=text,
                byte_length=len(text.encode("utf-8")),
                provenance=Provenance(
                    source_type=SourceType.HTTP,
                    source_uri=entry.get("url", ""),
                    document_path=filename,
                    retrieved_at=entry.get("retrieved_at", manifest.get("retrieved_at", "")),
                    revision=entry.get("version", ""),
                    content_sha256=content_sha,
                    license_note=license_note,
                    extra={
                        "author": author,
                        "title": entry.get("title", ""),
                        "category_hint": entry.get("category_hint", ""),
                        "has_static_content": str(entry.get("has_static_content", "")),
                        "source_index": source_index,
                    },
                ),
            )


def _default_git_runner(args: Sequence[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
