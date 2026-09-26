"""Tests for the DomeCTF challenge-level extraction layer (ctf_ingest.domectf_extract).

These lock in the honesty rules mirrored from the Redbud layer:
- English heading -> trajectory-stage mapping is deterministic; site/GitHub chrome never maps;
- category is EXPLICIT only from a real "is a <category> challenge" statement (generic filler like
  "CTF" is rejected), else technique-vote INFERRED, else MISSING;
- reasoning-only stages are never fabricated (a description->exploit jump leaves them MISSING),
  while a concrete code block / flag may register SOLUTION / VERIFICATION;
- author/challenge/E/I/M provenance behave as specified.
"""

from __future__ import annotations

from ctf_ingest.domectf_extract import (
    EXPLICIT,
    EXTRACTION_VERSION,
    INFERRED,
    MISSING,
    build_extraction,
    canonical_link,
    category_from_statement,
    map_heading_to_stage,
)
from ctf_ingest.models import TrajectoryStepKind

_KW = dict(
    source_url="https://beaglesecurity.com/blog/domectf2020/city-writeup.html",
    canonical_url="https://beaglesecurity.com/blog/domectf2020/city-writeup.html",
    raw_artifact_relpath="knowledge/domectf_sources_v1/raw/x.html",
    content_sha256="deadbeef",
    event="c0c0n XIII",
    year=2020,
    challenge_id="city",
    reference_author="",
    reference_challenge_name="City",
    source_origin="explicit_reference",
    retrieved_at="2026-09-25T00:00:00+00:00",
)


# --- heading -> stage mapping ----------------------------------------------------------------

def test_beagle_headings_map_to_expected_stages():
    assert map_heading_to_stage("Story") is TrajectoryStepKind.CHALLENGE_CONTEXT
    assert map_heading_to_stage("Solution") is TrajectoryStepKind.EXPLOIT_SOLUTION
    assert map_heading_to_stage("Analysis") is TrajectoryStepKind.INTERPRETATION
    assert map_heading_to_stage("Approach") is TrajectoryStepKind.HYPOTHESIS


def test_chrome_headings_are_skipped():
    for chrome in ("Related Articles", "Navigation Menu", "Footer", "Breadcrumbs",
                   "File metadata and controls", "Latest commit", "Comments"):
        assert map_heading_to_stage(chrome) is None


# --- category statement parsing --------------------------------------------------------------

def test_category_statement_accepts_real_categories():
    assert category_from_statement("City is a pwn challenge that was part of DOME CTF 2020") == "pwn"
    assert category_from_statement("The Spy is a OSINT challenge") == "osint"
    assert category_from_statement("TPM is a hardware challenge") == "hardware"
    assert category_from_statement("X is a cryptography challenge") == "crypto"


def test_category_statement_rejects_generic_filler():
    # "CTF challenge" / "base challenge" are not real categories.
    assert category_from_statement("ISS is a CTF challenge that was part of DomeCTF 2021") == ""
    assert category_from_statement("It is a base challenge") == ""
    assert category_from_statement("no category statement here") == ""


def test_canonical_link_extraction():
    html = '<link rel="canonical" href="https://beaglesecurity.com/blog/domectf2020/the-spy-writeup.html">'
    assert canonical_link(html) == "https://beaglesecurity.com/blog/domectf2020/the-spy-writeup.html"
    assert canonical_link("<html></html>") == ""


# --- full extraction on synthetic Beagle-style HTML ------------------------------------------

BEAGLE_HTML = """<html><head><title>City Writeup</title>
<meta name="author" content="Manindar Mohan">
<meta name="description" content="City is a pwn challenge that was part of DOME CTF 2020.">
<link rel="canonical" href="https://beaglesecurity.com/blog/domectf2020/city-writeup.html">
</head><body>
<h1>City Writeup</h1>
<h2>Story</h2><p>The participant is given an executable and must exploit it.</p>
<h2>Solution</h2><p>Overflow the buffer and jump to the win function.</p>
<pre>python -c 'print("A"*40)' | nc host 1337</pre>
<p>We get the flag domectf{buffer_overflow_win}.</p>
<h2>Related Articles</h2><p>chrome nav</p>
</body></html>
"""


def test_beagle_extraction_context_solution_verification_but_not_genuine():
    ext = build_extraction(BEAGLE_HTML, **_KW)
    kinds = {s.kind for s in ext.record.trajectory.steps}
    assert TrajectoryStepKind.CHALLENGE_CONTEXT in kinds   # Story
    assert TrajectoryStepKind.EXPLOIT_SOLUTION in kinds     # Solution
    assert TrajectoryStepKind.VERIFICATION in kinds         # flag present
    # No explicit hypothesis/interpretation heading -> honest: not a genuine reasoning chain.
    assert ext.genuine_trajectory is False
    assert ext.record.metadata.category == "pwn"
    assert ext.record.provenance.extra["author"] == "Manindar Mohan"
    assert ext.record.schema_version == EXTRACTION_VERSION
    assert ext.record.metadata.flags == ("domectf{buffer_overflow_win}",)


def test_beagle_extraction_field_provenance():
    ext = build_extraction(BEAGLE_HTML, **_KW)
    fp = ext.field_provenance
    assert fp["event"] == EXPLICIT
    assert fp["year"] == EXPLICIT
    assert fp["challenge_name"] == EXPLICIT
    assert fp["author"] == EXPLICIT                 # from page meta
    assert fp["category"] == EXPLICIT               # stated "is a pwn challenge"
    assert fp["challenge_description_context"] == EXPLICIT   # Story
    assert fp["solution_mechanism"] == EXPLICIT
    assert fp["verification_method"] == EXPLICIT
    # reasoning-only stages are honestly MISSING (never fabricated)
    assert fp["initial_hypotheses"] == MISSING
    assert fp["interpretations"] == MISSING
    assert fp["discriminating_tests"] == MISSING
    assert fp["failures_corrections"] == MISSING


# --- no-fabrication guard: description-only page (no code, no flag, no reasoning heading) ------

DESC_ONLY_HTML = """<html><head><title>Foo Writeup</title>
<meta name="author" content="A. Author"></head><body>
<h1>Foo Writeup</h1>
<h2>Story</h2><p>A short description of the challenge with no solution content at all.</p>
<h2>Related Articles</h2><p>chrome</p>
</body></html>
"""


def test_description_only_page_has_no_solution_or_reasoning():
    kw = dict(_KW, reference_challenge_name="Foo", challenge_id="foo")
    ext = build_extraction(DESC_ONLY_HTML, **kw)
    kinds = {s.kind for s in ext.record.trajectory.steps}
    assert kinds == {TrajectoryStepKind.CHALLENGE_CONTEXT}   # only Story; nothing fabricated
    assert ext.field_provenance["solution_mechanism"] == MISSING
    assert ext.field_provenance["verification_method"] == MISSING
    assert ext.genuine_trajectory is False


# --- category falls back to INFERRED (technique vote) when not explicitly stated --------------

INFER_HTML = """<html><head><title>Bar Writeup</title></head><body>
<h1>Bar Writeup</h1>
<h2>Story</h2><p>A web app.</p>
<h2>Solution</h2><p>We used SQL injection with union select to dump the database.</p>
<pre>' UNION SELECT username,password FROM users-- -</pre>
</body></html>
"""


def test_category_inferred_from_techniques_when_not_stated():
    kw = dict(_KW, reference_challenge_name="Bar", challenge_id="bar")
    ext = build_extraction(INFER_HTML, **kw)
    assert ext.field_provenance["category"] == INFERRED
    assert ext.record.metadata.category == "web"
    tech_ids = {t.technique_id for t in ext.record.techniques}
    assert "sqli" in tech_ids or "sql-injection" in tech_ids
