from __future__ import annotations

from ctf_ingest.models import (
    ChallengeMetadata,
    FailureCorrection,
    KnowledgeRecord,
    Provenance,
    ReasoningTrajectory,
    SourceType,
    Technique,
    TrajectoryStep,
    TrajectoryStepKind,
)
from ctf_experiment.corpus_analysis import (
    EXPLICIT,
    INFERRED,
    MISSING,
    compare_corpora,
    corpus_stats,
    cross_corpus_duplicates,
    extraction_quality,
)


def _rec(rid, category, title, techniques=(), steps=(), failures=(), *, http=False, summary="body"):
    prov = (
        Provenance(SourceType.HTTP, f"https://x/{rid}", f"{rid}.html", "2026-01-01T00:00:00+00:00",
                   "", f"sha-{rid}", "note", {"author": "A"})
        if http else
        Provenance(SourceType.LOCAL_DIRECTORY, "corpus", f"{rid}.md", "", "", f"sha-{rid}")
    )
    return KnowledgeRecord(
        record_id=rid, content_hash=f"ch-{rid}", provenance=prov,
        metadata=ChallengeMetadata(name=title, category=category),
        techniques=tuple(Technique(t, t, category, (t,), 0.8) for t in techniques),
        trajectory=ReasoningTrajectory(steps=tuple(steps), completeness=0.1 * len(steps)),
        failures=tuple(failures), title=title, summary=summary,
    )


def test_corpus_stats_counts_and_coverage():
    recs = [
        _rec("r1", "web", "A", techniques=("ssti", "xss")),
        _rec("r2", "crypto", "B", techniques=("rsa-attack",), failures=(FailureCorrection("x"),)),
    ]
    stats = corpus_stats(recs)
    assert stats["documents"] == 2
    assert stats["distinct_techniques"] == 3
    assert stats["failure_correction_coverage"] == 0.5
    assert 0.0 <= stats["provenance_completeness"] <= 1.0


def test_cross_corpus_duplicate_preserves_provenance_and_flags_match():
    local = [_rec("L1", "web", "Shared Title", summary="identical body about ssti jinja template")]
    # near-identical new record (same title+summary) -> should be flagged, not dropped
    new = [_rec("N1", "web", "Shared Title", summary="identical body about ssti jinja template", http=True)]
    report = cross_corpus_duplicates(local, new, near_threshold=0.8)
    assert report["duplicate_count"] == 1
    assert report["provenance_preserved"] is True
    assert report["duplicate_matches"][0]["duplicate_of"] == "L1"


def test_cross_corpus_unique_new_record_not_flagged():
    local = [_rec("L1", "web", "Alpha", summary="sql injection union select rows")]
    new = [_rec("N1", "crypto", "Beta", summary="rsa small exponent lattice attack", http=True)]
    report = cross_corpus_duplicates(local, new)
    assert report["duplicate_count"] == 0


def test_extraction_quality_marks_missing_not_invented():
    # A technique-catalog style record: techniques present, but NO reasoning stages.
    rec = _rec("r1", "misc", "Pyjail", techniques=("ssti",), http=True,
               summary="python jail escape techniques")
    raw = {"r1": "Category: misc\n\npython jail escape"}
    eq = extraction_quality([rec], raw)
    fields = eq["per_record"][0]["fields"]
    assert fields["techniques_mechanisms"] == EXPLICIT
    assert fields["category"] == EXPLICIT  # explicit label present in raw text
    # Reasoning stages absent -> MISSING, never invented.
    for stage in ("hypotheses", "discriminating_tests", "observations", "interpretations",
                  "hypothesis_updates", "verification"):
        assert fields[stage] == MISSING
    assert fields["failures_corrections"] == MISSING


def test_extraction_quality_category_inferred_without_label():
    rec = _rec("r1", "web", "T", techniques=("ssti",), http=True)
    eq = extraction_quality([rec], {"r1": "no label here, just prose about templates"})
    assert eq["per_record"][0]["fields"]["category"] == INFERRED


def test_compare_corpora_shape():
    local = corpus_stats([_rec("L1", "web", "A", techniques=("ssti",))])
    new = corpus_stats([_rec("N1", "misc", "B", techniques=("rsa-attack",), http=True)])
    cmp = compare_corpora(local, new)
    assert cmp["documents"] == {"local": 1, "jiaje": 1}
    assert "rsa-attack" in cmp["techniques_only_in_jiaje"]
    assert cmp["provenance_completeness"]["jiaje"] >= cmp["provenance_completeness"]["local"]
