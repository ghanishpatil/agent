from __future__ import annotations

from ctf_ingest.extract import (
    extract_failures,
    extract_metadata,
    extract_techniques,
    extract_trajectory,
)
from ctf_ingest.models import MediaType, Provenance, RawDocument, SourceType, TrajectoryStepKind
from ctf_ingest.normalize import normalize

from .conftest import CRYPTO_WRITEUP, WEB_WRITEUP


def _writeup(text: str, media: MediaType = MediaType.MARKDOWN):
    return normalize(
        RawDocument(
            doc_id="d",
            media_type=media,
            text=text,
            provenance=Provenance(SourceType.LOCAL_DIRECTORY, "uri", "p.md"),
        )
    )


def test_metadata_extracts_category_flag_and_points() -> None:
    meta = extract_metadata(_writeup(WEB_WRITEUP))
    assert meta.category == "web"
    assert meta.points == 150
    assert "CTF{ssti_is_fun}" in meta.flags
    assert meta.flag_format == "CTF{...}"


def test_techniques_detects_ssti_for_web_writeup() -> None:
    techniques = extract_techniques(_writeup(WEB_WRITEUP))
    ids = {t.technique_id for t in techniques}
    assert "ssti" in ids
    ssti = next(t for t in techniques if t.technique_id == "ssti")
    assert ssti.confidence > 0.4
    assert ssti.evidence


def test_techniques_detects_xor_for_crypto_writeup() -> None:
    ids = {t.technique_id for t in extract_techniques(_writeup(CRYPTO_WRITEUP))}
    assert "xor-cipher" in ids


def test_trajectory_recovers_multiple_reasoning_stages() -> None:
    trajectory = extract_trajectory(_writeup(WEB_WRITEUP))
    kinds = set(trajectory.kinds())
    # The web writeup exercises context, test, observation, interpretation, verification.
    assert TrajectoryStepKind.DISCRIMINATING_TEST in kinds
    assert TrajectoryStepKind.OBSERVATION in kinds
    assert TrajectoryStepKind.VERIFICATION in kinds
    assert 0.0 < trajectory.completeness <= 1.0


def test_failure_correction_extracted_from_crypto_writeup() -> None:
    failures = extract_failures(_writeup(CRYPTO_WRITEUP))
    assert failures
    first = failures[0]
    assert "base64" in first.failed_approach.lower()
    # The correction sentence mentions the real mechanism.
    assert "xor" in (first.correction.lower() + first.failed_approach.lower())


def test_nothing_fabricated_when_text_is_empty() -> None:
    writeup = _writeup("# Empty\n\n")
    meta = extract_metadata(writeup)
    assert meta.flags == ()
    assert extract_techniques(writeup) == ()
    assert extract_failures(writeup) == ()
