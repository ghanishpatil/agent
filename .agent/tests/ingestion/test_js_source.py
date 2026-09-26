from __future__ import annotations

from pathlib import Path

import pytest

from ctf_ingest.js_source import (
    DiscoveredLink,
    RendererUnavailable,
    _is_writeup_candidate,
    classify_link,
    render_urls,
)

PAGE = "https://jia.je/ctf-writeups/puppeteer/index.html"


# -- Pure classification (no browser) --------------------------------------------------------


def test_classify_internal_book():
    link = classify_link("https://jia.je/ctf-writeups/puppeteer/week0/easy-random-1.html", PAGE)
    assert link.classification == "internal_book"


def test_classify_internal_other():
    link = classify_link("https://jia.je/about/", PAGE)
    assert link.classification == "internal_other"


def test_classify_external():
    link = classify_link("https://github.com/jiegec", PAGE)
    assert link.classification == "external"


def test_classify_anchor():
    link = classify_link("https://jia.je/ctf-writeups/puppeteer/index.html#week-0", PAGE)
    assert link.classification == "anchor"


def test_writeup_candidate_true_for_individual_page():
    link = DiscoveredLink(
        "https://jia.je/ctf-writeups/puppeteer/week1/rsa-all-in-one.html", "RSA", "internal_book", True
    )
    assert _is_writeup_candidate(link, PAGE) is True


def test_writeup_candidate_excludes_index_hubs():
    link = DiscoveredLink(
        "https://jia.je/ctf-writeups/summer2026/index.html", "Redbud Summer 2026", "internal_book", True
    )
    assert _is_writeup_candidate(link, PAGE) is False


def test_writeup_candidate_excludes_external_and_out_of_content():
    ext = DiscoveredLink("https://github.com/x", "gh", "external", True)
    chrome = DiscoveredLink("https://jia.je/ctf-writeups/misc/pyjail.html", "Pyjail", "internal_book", False)
    assert _is_writeup_candidate(ext, PAGE) is False
    assert _is_writeup_candidate(chrome, PAGE) is False  # not in content area


# -- Offline render smoke test (proves JS execution). Skips if no browser. -------------------


def _browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except Exception:
        return False
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            return bool(p.chromium.executable_path) and Path(p.chromium.executable_path).exists()
    except Exception:
        return False


browser = pytest.mark.skipif(not _browser_available(), reason="no Playwright Chromium browser")


@browser
def test_render_executes_javascript_and_captures_injected_content(tmp_path: Path):
    page = tmp_path / "p.html"
    page.write_text(
        "<!doctype html><html><head><title>t</title></head><body>"
        "<div class='md-content'><article id='c'>STATIC_ONLY</article></div>"
        "<script>document.getElementById('c').insertAdjacentText('beforeend',' JS_INJECTED_MARKER');"
        "var a=document.createElement('a');a.href='https://jia.je/ctf-writeups/x/chal.html';"
        "a.textContent='chal';document.querySelector('article').appendChild(a);</script>"
        "</body></html>",
        encoding="utf-8",
    )
    results = render_urls([page.as_uri()], tmp_path / "out", wait_until="load")
    assert len(results) == 1
    r = results[0]
    assert r.ok is True
    # The rendered artifact must contain the JS-injected content (proves JS ran).
    rendered_text = Path(r.text_artifact).read_text(encoding="utf-8")
    assert "JS_INJECTED_MARKER" in rendered_text
    assert r.rendered_html_bytes > 0
    assert r.content_sha256
    assert r.renderer == "playwright-chromium"
    assert any(l.text == "chal" for l in r.discovered_links)


@browser
def test_render_per_url_fails_closed_on_bad_target(tmp_path: Path):
    # A non-existent local file URL: the per-URL render fails closed (ok=False, no content).
    bad = (tmp_path / "does-not-exist.html").as_uri()
    results = render_urls([bad], tmp_path / "out", wait_until="load", timeout_ms=8000)
    assert results[0].ok is False
    assert results[0].error
    assert results[0].content_sha256 == ""
