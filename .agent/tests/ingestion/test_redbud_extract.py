"""Tests for the Redbud challenge-level extraction layer (ctf_ingest.redbud_extract).

These lock in the grounding rules that keep the extraction honest:
- Bilingual (Chinese/English) heading -> trajectory-stage mapping is deterministic and
  first-match ordered.
- Chrome/non-reasoning headings never become stages.
- Reasoning-only stages are recorded ONLY from headings (never fabricated from prose), while
  concrete artifacts (code block, flag string) may register EXPLOIT_SOLUTION / VERIFICATION.
- Field provenance is EXPLICIT / INFERRED / MISSING, and category is INFERRED (no explicit label).
- A "genuine trajectory" requires a context -> reasoning -> solution/verification chain, not a
  bare technique/command listing.
"""

from __future__ import annotations

from ctf_ingest.models import TrajectoryStepKind
from ctf_ingest.redbud_extract import (
    EXPLICIT,
    EXTRACTION_VERSION,
    INFERRED,
    MISSING,
    build_extraction,
    map_heading_to_stage,
)


# --- heading -> stage mapping ----------------------------------------------------------------

def test_chinese_headings_map_to_expected_stages():
    assert map_heading_to_stage("题目描述") is TrajectoryStepKind.CHALLENGE_CONTEXT
    assert map_heading_to_stage("攻击思路") is TrajectoryStepKind.HYPOTHESIS
    assert map_heading_to_stage("攻击脚本") is TrajectoryStepKind.EXPLOIT_SOLUTION
    assert map_heading_to_stage("验证") is TrajectoryStepKind.VERIFICATION


def test_english_headings_map_to_expected_stages():
    assert map_heading_to_stage("Description") is TrajectoryStepKind.CHALLENGE_CONTEXT
    assert map_heading_to_stage("Approach") is TrajectoryStepKind.HYPOTHESIS
    assert map_heading_to_stage("Exploit") is TrajectoryStepKind.EXPLOIT_SOLUTION
    assert map_heading_to_stage("Analysis") is TrajectoryStepKind.INTERPRETATION


def test_chrome_headings_are_skipped():
    for chrome in ("Comments", "总结", "Summary", "Cite this"):
        assert map_heading_to_stage(chrome) is None


def test_empty_or_unknown_heading_is_none():
    assert map_heading_to_stage("") is None
    assert map_heading_to_stage("   ") is None
    assert map_heading_to_stage("随便一个不相关标题") is None


# --- full extraction on synthetic HTML -------------------------------------------------------

_KW = dict(
    source_url="https://jia.je/ctf-writeups/puppeteer/week0/synthetic.html",
    raw_artifact_relpath="raw/synthetic.rendered.html",
    content_sha256="deadbeef",
    event="Redbud Puppeteer",
    challenge_id="synthetic",
    author="Jiajie Chen",
    retrieved_at="2026-09-25T00:00:00+00:00",
)

RICH_HTML = """<html><head><title>Easy Random 1 Writeup</title></head><body>
<h1>Easy Random 1</h1>
<h2>题目描述</h2>
<p>服务端使用 glibc random() 生成 token，我们需要预测下一个输出。</p>
<h2>攻击思路</h2>
<p>Hypothesis: glibc random() is a predictable PRNG; recover its state.</p>
<h2>分析</h2>
<p>random() 使用一个可恢复的内部状态。</p>
<h2>攻击脚本</h2>
<pre><code>from pwn import *
# recover state and predict
</code></pre>
<h2>验证</h2>
<p>The flag is flag{glibc_random_predicted}.</p>
<h2>Comments</h2>
<p>chrome</p>
</body></html>
"""


def test_rich_writeup_yields_genuine_trajectory():
    ext = build_extraction(RICH_HTML, **_KW)
    kinds = {s.kind for s in ext.record.trajectory.steps}
    assert TrajectoryStepKind.CHALLENGE_CONTEXT in kinds
    assert TrajectoryStepKind.HYPOTHESIS in kinds
    assert TrajectoryStepKind.INTERPRETATION in kinds
    assert TrajectoryStepKind.EXPLOIT_SOLUTION in kinds
    assert TrajectoryStepKind.VERIFICATION in kinds
    assert ext.genuine_trajectory is True
    # completeness is fraction of the 11-stage canonical order that is present.
    assert 0.0 < ext.record.trajectory.completeness <= 1.0


def test_extraction_records_provenance_and_version():
    ext = build_extraction(RICH_HTML, **_KW)
    fp = ext.field_provenance
    # category is never claimed EXPLICIT (no explicit label in Redbud pages).
    assert fp["category"] == INFERRED
    assert fp["event"] == EXPLICIT
    assert fp["challenge_name"] == EXPLICIT
    assert fp["challenge_description_context"] == EXPLICIT  # heading present
    assert fp["exploit_solution_mechanism"] == EXPLICIT
    assert fp["verification_method"] == EXPLICIT
    assert ext.record.schema_version == EXTRACTION_VERSION
    assert ext.record.provenance.content_sha256 == "deadbeef"
    assert ext.record.provenance.source_uri.startswith("https://jia.je/")


# --- headingless code dump (pwn-style) -------------------------------------------------------

CODEDUMP_HTML = """<html><head><title>ret2shellcode</title></head><body>
<h1>ret2shellcode</h1>
<p>反编译：</p>
<pre><code>ssize_t vuln(){ char buf[256]; read(0, buf, 0x200); }</code></pre>
<h2>Comments</h2>
</body></html>
"""


def test_codedump_registers_solution_but_not_genuine_trajectory():
    ext = build_extraction(CODEDUMP_HTML, **_KW)
    kinds = {s.kind for s in ext.record.trajectory.steps}
    # A concrete code block is present -> EXPLOIT_SOLUTION is allowed even without a heading.
    assert TrajectoryStepKind.EXPLOIT_SOLUTION in kinds
    # But there is no context/hypothesis/interpretation heading -> not a genuine trajectory.
    assert TrajectoryStepKind.CHALLENGE_CONTEXT not in kinds
    assert ext.genuine_trajectory is False


def test_codedump_reasoning_fields_are_missing_not_fabricated():
    ext = build_extraction(CODEDUMP_HTML, **_KW)
    fp = ext.field_provenance
    # No heading denotes these reasoning stages, and we must not invent them.
    assert fp["challenge_description_context"] == MISSING
    assert fp["initial_hypotheses"] == MISSING
    assert fp["interpretations"] == MISSING
    assert fp["important_clues"] == MISSING
    # Concrete artifact IS present, so commands/tools is explicit.
    assert fp["commands_tools"] == EXPLICIT


# --- no-fabrication guard on a prose-only page (no headings, no code, no flag) ----------------

PLAIN_HTML = """<html><head><title>Some Notes</title></head><body>
<h1>Some Notes</h1>
<p>This paragraph merely discusses an approach in prose but has no section headings,
no code block, and no flag string.</p>
<h2>Comments</h2>
</body></html>
"""


def test_prose_only_page_has_no_reasoning_stages():
    ext = build_extraction(PLAIN_HTML, **_KW)
    kinds = {s.kind for s in ext.record.trajectory.steps}
    assert kinds == set()  # nothing fabricated from prose
    assert ext.genuine_trajectory is False
    assert ext.record.trajectory.completeness == 0.0
