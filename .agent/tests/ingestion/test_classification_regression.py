"""Regression tests for the forensics category-consistency=0.0 root cause.

Root cause was classification/extraction: an explicit "**Category:** Forensics" label
(wrapped in markdown emphasis) was ignored by the label matcher, so classification fell
back to keyword counting where crypto vocabulary outvoted sparse forensics signals. Fixes
are ingestion-side only (extract.py); the solver is untouched.
"""

from __future__ import annotations

from ctf_ingest.extract import _infer_category, _normalize_category, extract_metadata
from ctf_ingest.models import MediaType, Provenance, RawDocument, SourceType, Technique
from ctf_ingest.normalize import normalize


def _writeup(text: str):
    return normalize(
        RawDocument(
            doc_id="d",
            media_type=MediaType.MARKDOWN,
            text=text,
            provenance=Provenance(SourceType.LOCAL_DIRECTORY, "uri", "p.md"),
        )
    )


def test_markdown_wrapped_category_label_is_honored() -> None:
    # The original failing shape: bold label plus crypto-heavy body.
    text = (
        "# Timeseries Trap\n\n"
        "**Category:** Forensics\n\n"
        "We recovered a pcap and also had to decode an aes cbc encrypted blob; "
        "the aes cipher decrypt hash md5 discussion is lengthy.\n"
    )
    meta = extract_metadata(_writeup(text))
    assert meta.category == "forensics"


def test_heading_and_backtick_category_labels_are_honored() -> None:
    assert extract_metadata(_writeup("## Category - Web\n\nsome body")).category == "web"
    assert extract_metadata(_writeup("`category`: crypto\n\nrsa modulus")).category == "crypto"


def test_category_aliases_normalize() -> None:
    assert _normalize_category("Cryptography") == "crypto"
    assert _normalize_category("Reversing") == "reverse"
    assert _normalize_category("**Forensic**") == "forensics"
    assert _normalize_category("Binary Exploitation") == "pwn"


def test_technique_votes_break_keyword_ties_toward_forensics() -> None:
    # No explicit label; forensics techniques present; crypto keywords also present.
    forensics_techs = (
        Technique("pcap-analysis", "PCAP Analysis", "forensics", ("pcap",), 1.0),
        Technique("steganography", "Steganography", "forensics", ("steg",), 0.8),
    )
    crypto_techs = (Technique("aes-mode-attack", "AES Mode Attack", "crypto", ("aes",), 0.5),)
    lower = "we used wireshark on the pcap then noticed aes and hash and cipher and rsa"
    assert _infer_category(lower, forensics_techs + crypto_techs) == "forensics"


def test_inference_without_signals_returns_empty() -> None:
    assert _infer_category("nothing distinctive here", ()) == ""


def test_explicit_label_overrides_keyword_inference() -> None:
    # Body screams "web" via keywords, but the author labeled it crypto.
    text = "Category: crypto\n\nsql injection xss ssti cookie jwt web http everywhere"
    assert extract_metadata(_writeup(text)).category == "crypto"
