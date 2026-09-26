"""Tests for the DomeCTF source-discovery layer (ctf_ingest.domectf_discovery).

These lock in the network-free, deterministic behaviour that keeps the inventory honest:
- docx parsing yields the document's own year grouping and takes names/authors from anchor text;
- source_type derivation is host/anchor driven;
- accessibility mapping keeps existence vs accessibility separate and detects soft-404s;
- content classification requires solution evidence (never "individual" from a title alone) and is
  not fooled by navigation-chrome link counts.
"""

from __future__ import annotations

from pathlib import Path

from ctf_ingest.domectf_discovery import (
    CLS_INDEX,
    CLS_INDIVIDUAL,
    CLS_OFFICIAL,
    CLS_OTHER,
    GITHUB_WRITEUP,
    INDIVIDUAL_WRITEUP,
    MEDIUM_WRITEUP,
    OFFICIAL_EVENT_PAGE,
    OFFICIAL_WRITEUP_INDEX,
    WRITEUP_INDEX,
    canonical_url,
    classify_content,
    derive_accessibility,
    derive_challenge_and_author,
    derive_source_type,
    extract_writeup_links,
    is_soft_404,
    parse_reference_docx,
)

# The uploaded reference document lives at the workspace root (parent of the .agent package root).
_DOCX = Path(__file__).resolve().parents[3] / "DomeCTF_CTF_Writeups_Reference_Links (1).docx"


# --- source_type derivation ------------------------------------------------------------------

def test_source_type_by_host_and_anchor():
    assert derive_source_type("Weapon Store — Ashish Rana (GitHub)",
                              "https://github.com/aencode/domectf/blob/master/x.md") == GITHUB_WRITEUP
    assert derive_source_type("The Matrix — Parinay Bansal (Medium)",
                              "https://medium.com/bugbountywriteup/x") == MEDIUM_WRITEUP
    assert derive_source_type("Official DomeCTF 2022 page",
                              "https://india.c0c0n.org/2022/DomeCTF/") == OFFICIAL_EVENT_PAGE
    assert derive_source_type("City", "https://beaglesecurity.com/blog/domectf2020/city-writeup.html") == INDIVIDUAL_WRITEUP
    assert derive_source_type("DomeCTF 2020 — Beagle Security archive",
                              "https://beaglesecurity.com/blog/tag/domectf2020/") == WRITEUP_INDEX
    assert derive_source_type("DOME CTF 2020 — official recap / writeup index",
                              "https://beaglesecurity.com/blog/domectf2020/c0c0n-XIII-dome-ctf-2020.html") == OFFICIAL_WRITEUP_INDEX


def test_challenge_and_author_only_from_anchor_for_individual_types():
    ch, au = derive_challenge_and_author("Weapon Store \u2014 Ashish Rana (GitHub)", "https://github.com/x", GITHUB_WRITEUP)
    assert ch == "Weapon Store" and au == "Ashish Rana"
    # Index/official references name no single challenge.
    ch2, au2 = derive_challenge_and_author("DOME CTF 2020 — official recap / writeup index", "https://beaglesecurity.com/x", OFFICIAL_WRITEUP_INDEX)
    assert ch2 is None and au2 is None
    # Bare challenge name, no author.
    ch3, au3 = derive_challenge_and_author("City", "https://beaglesecurity.com/blog/domectf2020/city-writeup.html", INDIVIDUAL_WRITEUP)
    assert ch3 == "City" and au3 is None


# --- accessibility mapping (existence vs accessibility; soft-404) -----------------------------

def test_soft_404_detection_direct_and_via_redirect():
    assert is_soft_404("https://beaglesecurity.com/404", [])
    assert is_soft_404("https://x.com/final", [{"to": "https://beaglesecurity.com/404", "code": 302}])
    assert not is_soft_404("https://x.com/blog/city-writeup.html", [])


def test_accessibility_status_mapping():
    ok = derive_accessibility(ok_transport=True, http_status=200, final_url="https://x/p",
                              redirect_chain=[], body_text_len=2000, num_scripts=1)
    assert ok == ("ACCESSIBLE", True, False)
    blocked = derive_accessibility(ok_transport=True, http_status=403, final_url="https://x/p",
                                   redirect_chain=[], body_text_len=0, num_scripts=0)
    assert blocked[0] == "ACCESS_BLOCKED"
    soft = derive_accessibility(ok_transport=True, http_status=200, final_url="https://x/404",
                                redirect_chain=[], body_text_len=50, num_scripts=1)
    assert soft[0] == "NOT_FOUND"
    net = derive_accessibility(ok_transport=False, http_status=None, final_url="https://x",
                               redirect_chain=[], body_text_len=0, num_scripts=0)
    assert net[0] == "NETWORK_FAILURE"
    render = derive_accessibility(ok_transport=True, http_status=200, final_url="https://x/p",
                                  redirect_chain=[], body_text_len=20, num_scripts=5)
    assert render == ("RENDER_REQUIRED", False, True)


# --- content classification (evidence-driven; chrome-link resistant) --------------------------

_WRITEUP_HTML = ("<html><head><title>City Write-up</title></head><body>"
                 "<h1>City</h1><p>We solve this by crafting an exploit payload; the flag is here.</p>"
                 "<pre>python solve.py</pre>"
                 # site-nav chrome: many *-writeup.html links, present on every page
                 + "".join(f'<a href="/blog/domectf2020/x{i}-writeup.html">x{i}</a>' for i in range(20))
                 + "</body></html>")


def test_individual_writeup_not_misclassified_by_nav_links():
    body = "We solve this by crafting an exploit payload; the flag is here. " * 10
    cls, ev = classify_content(url="https://beaglesecurity.com/blog/domectf2020/city-writeup.html",
                               title="City Write-up", headings=["City"], body_text=body,
                               html=_WRITEUP_HTML, declared_type=INDIVIDUAL_WRITEUP)
    assert cls == CLS_INDIVIDUAL
    assert ev["num_writeup_links"] >= 20  # chrome links recorded but not decisive
    assert ev["has_solution_content"] is True


def test_index_page_is_link_list_without_solution_content():
    html = "<html><body><h1>DomeCTF 2020 writeups</h1>" + "".join(
        f'<a href="/blog/domectf2020/x{i}-writeup.html">x{i}</a>' for i in range(20)) + "</body></html>"
    body = "DomeCTF 2020 writeups index. " * 20
    cls, ev = classify_content(url="https://beaglesecurity.com/blog/tag/domectf2020/",
                               title="DomeCTF 2020", headings=[], body_text=body, html=html,
                               declared_type=WRITEUP_INDEX)
    assert cls == CLS_INDEX
    assert ev["has_solution_content"] is False


def test_official_host_is_official():
    cls, _ = classify_content(url="https://india.c0c0n.org/2022/DomeCTF/", title="DomeCTF 2022",
                              headings=[], body_text="Register for the schedule and rules." * 5,
                              html="<html><body>event</body></html>", declared_type=OFFICIAL_EVENT_PAGE)
    assert cls == CLS_OFFICIAL


def test_title_alone_does_not_make_individual():
    # A page titled like a challenge but with no solution content and no index structure is NOT
    # classified as an individual writeup.
    cls, ev = classify_content(url="https://example.com/city", title="City Challenge",
                               headings=["City"], body_text="This page just mentions the City challenge name." * 5,
                               html="<html><body><p>nothing here</p></body></html>",
                               declared_type=INDIVIDUAL_WRITEUP)
    assert cls == CLS_OTHER
    assert ev["has_solution_content"] is False


# --- discovered-link extraction + canonicalisation --------------------------------------------

def test_extract_writeup_links_same_host_only():
    html = ('<a href="/blog/domectf2020/city-writeup.html">c</a>'
            '<a href="https://other.com/x-writeup.html">o</a>'
            '<a href="/blog/domectf2020/tpm-writeup.html#frag">t</a>')
    links = extract_writeup_links(html, "https://beaglesecurity.com/blog/domectf2020/index.html")
    urls = {l["url"] for l in links}
    assert "https://beaglesecurity.com/blog/domectf2020/city-writeup.html" in urls
    assert "https://beaglesecurity.com/blog/domectf2020/tpm-writeup.html" in urls  # fragment stripped
    assert all("other.com" not in u for u in urls)  # cross-host excluded


def test_canonical_url_conservative():
    assert canonical_url("https://WWW.Example.com/a/") == "https://example.com/a"
    # distinct paths are never collapsed
    assert canonical_url("https://x.com/a") != canonical_url("https://x.com/b")


# --- end-to-end docx parse (uses the real uploaded document) ----------------------------------

def test_parse_reference_docx_grouping_and_counts():
    if not _DOCX.exists():
        import pytest
        pytest.skip("reference docx not present in this checkout")
    refs, meta = parse_reference_docx(_DOCX)
    assert len(refs) == 40
    by_year = {}
    for r in refs:
        by_year[str(r.year)] = by_year.get(str(r.year), 0) + 1
    assert by_year == {"2019": 6, "2020": 22, "2021": 9, "2022": 1, "2023": 1, "2025": 1}
    # the document explicitly marks these years as lacking a verified complete archive
    assert set(meta.year_notes.keys()) == {"2022", "2023", "2024", "2025"}
    # names/authors come from anchor text (differ from URL slugs)
    unlockme = next(r for r in refs if r.url.endswith("United_States_Play_Store.md"))
    assert unlockme.challenge_name == "UnlockMe CTF" and unlockme.source_author == "Ashish Rana"
