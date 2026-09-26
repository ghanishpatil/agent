from __future__ import annotations

from ctf_ingest.models import MediaType
from ctf_ingest.parser import parse_sections, strip_html
from ctf_ingest.normalize import normalize
from ctf_ingest.models import Provenance, RawDocument, SourceType


def _doc(text: str, media: MediaType) -> RawDocument:
    return RawDocument(
        doc_id="d1",
        media_type=media,
        text=text,
        provenance=Provenance(SourceType.LOCAL_DIRECTORY, "uri", "p.md"),
    )


def test_parse_atx_headings_into_sections() -> None:
    title, sections = parse_sections(
        "# Title\n\nintro\n\n## Recon\n\nlooked around\n\n## Flag\n\nCTF{x}",
        MediaType.MARKDOWN,
    )
    assert title == "Title"
    headings = [s.heading for s in sections]
    assert headings == ["Title", "Recon", "Flag"]
    recon = next(s for s in sections if s.heading == "Recon")
    assert "looked around" in recon.body


def test_setext_headings_are_detected() -> None:
    title, sections = parse_sections("My Writeup\n==========\n\nbody text here", MediaType.MARKDOWN)
    assert title == "My Writeup"
    assert sections[0].body.strip() == "body text here"


def test_strip_html_removes_tags_and_scripts() -> None:
    cleaned = strip_html("<h1>Hi</h1><script>evil()</script><p>body</p>")
    assert "evil" not in cleaned
    assert "Hi" in cleaned and "body" in cleaned


def test_normalize_produces_hash_and_title() -> None:
    writeup = normalize(_doc("# Alpha\n\nsome content about xor", MediaType.MARKDOWN))
    assert writeup.title == "Alpha"
    assert writeup.normalized_sha256
    assert "xor" in writeup.body_text


def test_document_with_no_headings_becomes_single_section() -> None:
    _title, sections = parse_sections("just a paragraph with no headings", MediaType.TEXT)
    assert len(sections) == 1
    assert "paragraph" in sections[0].body
