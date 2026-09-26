"""Normalization stage: RawDocument -> NormalizedWriteup (headed sections + clean body)."""

from __future__ import annotations

import hashlib

from .models import NormalizedWriteup, RawDocument
from .parser import clean_body, parse_sections


def normalize(document: RawDocument) -> NormalizedWriteup:
    title, sections = parse_sections(document.text, document.media_type)
    body_text = clean_body(
        "\n\n".join(
            part for part in (section.body for section in sections) if part
        )
        or document.text
    )
    normalized_sha = hashlib.sha256(body_text.encode("utf-8")).hexdigest()
    return NormalizedWriteup(
        doc_id=document.doc_id,
        title=title or document.provenance.document_path or document.doc_id,
        sections=sections,
        body_text=body_text,
        provenance=document.provenance,
        normalized_sha256=normalized_sha,
    )
