from __future__ import annotations

from pathlib import Path

from ctf_ingest import GitRepositorySource, HttpSource, LocalDirectorySource, MediaType, SourceType


def test_local_directory_source_walks_only_text_documents(writeups_dir: Path) -> None:
    docs = list(LocalDirectorySource(writeups_dir).documents())
    paths = sorted(doc.provenance.document_path for doc in docs)
    assert paths == ["crypto/xor.md", "forensics/pcap.html", "web/ssti.md"]
    # The binary artifact.bin is excluded.
    assert all(not p.endswith(".bin") for p in paths)


def test_local_source_sets_provenance_and_media_type(writeups_dir: Path) -> None:
    docs = {d.provenance.document_path: d for d in LocalDirectorySource(writeups_dir).documents()}
    html = docs["forensics/pcap.html"]
    assert html.media_type is MediaType.HTML
    assert html.provenance.source_type is SourceType.LOCAL_DIRECTORY
    assert html.provenance.content_sha256
    assert docs["web/ssti.md"].media_type is MediaType.MARKDOWN


def test_doc_ids_are_stable_and_unique(writeups_dir: Path) -> None:
    first = {d.doc_id for d in LocalDirectorySource(writeups_dir).documents()}
    second = {d.doc_id for d in LocalDirectorySource(writeups_dir).documents()}
    assert first == second
    assert len(first) == 3


def test_http_source_requires_explicit_fetcher() -> None:
    calls = []

    def fetcher(url: str) -> str:
        calls.append(url)
        return f"<h1>{url}</h1>"

    docs = list(HttpSource(["http://example.invalid/a"], fetcher).documents())
    assert calls == ["http://example.invalid/a"]
    assert docs[0].provenance.source_type is SourceType.HTTP


def test_git_source_uses_injected_runner_and_reports_provenance(tmp_path: Path) -> None:
    checkout_root = {}

    def fake_git(args, cwd):
        if args[0] == "clone":
            dest = Path(args[-1])
            (dest).mkdir(parents=True, exist_ok=True)
            (dest / "writeup.md").write_text(
                "# Repo Writeup\n\nCategory: crypto\n\nThe flag is CTF{from_git}.\n",
                encoding="utf-8",
            )
            checkout_root["dest"] = dest
            return ""
        if args[0] == "rev-parse":
            return "abc123\n"
        return ""

    source = GitRepositorySource("https://example.invalid/repo.git", git_runner=fake_git)
    docs = list(source.documents())
    assert len(docs) == 1
    assert docs[0].provenance.source_type is SourceType.GIT_REPOSITORY
    assert docs[0].provenance.revision == "abc123"
    assert docs[0].provenance.source_uri == "https://example.invalid/repo.git"


def test_git_source_clone_failure_yields_nothing(tmp_path: Path) -> None:
    def failing_git(args, cwd):
        raise RuntimeError("clone denied")

    source = GitRepositorySource("https://example.invalid/repo.git", git_runner=failing_git)
    assert list(source.documents()) == []
    assert "clone denied" in source.last_error
