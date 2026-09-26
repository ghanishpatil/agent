"""DomeCTF historical source discovery/verification (inventory only — NO knowledge extraction).

This module is deliberately additive and isolated. It performs the deterministic, network-free
parts of the DomeCTF source-discovery task:

- ``parse_reference_docx``  : parse the uploaded reference .docx into structured references, grouped
                              by the document's own year sections, taking challenge names / authors
                              strictly from the hyperlink anchor text (never inferred from URLs).
- ``derive_source_type``    : map an anchor + URL to an apparent source_type (the taxonomy value).
- ``classify_content``      : evidence-based A/B/C/D classification of a *fetched* page. It never
                              calls the network and never decides "individual writeup" from a title
                              alone — it requires content evidence and records that evidence.
- ``extract_writeup_links`` : find (but never follow) same-site DomeCTF writeup links on an index
                              page, for the DISCOVERED inventory.

The actual (respectful) HTTP fetching lives in the driver script, mirroring the project's existing
"explicit fetcher, no silent scraping" design (see HttpSource). This module has no network side
effects, so importing it — e.g. during the test run — is safe and deterministic.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# ---- source_type taxonomy (exact values required by the task) --------------------------------
OFFICIAL_EVENT_PAGE = "OFFICIAL_EVENT_PAGE"
OFFICIAL_WRITEUP_INDEX = "OFFICIAL_WRITEUP_INDEX"
WRITEUP_INDEX = "WRITEUP_INDEX"
INDIVIDUAL_WRITEUP = "INDIVIDUAL_WRITEUP"
GITHUB_WRITEUP = "GITHUB_WRITEUP"
MEDIUM_WRITEUP = "MEDIUM_WRITEUP"
BLOG_WRITEUP = "BLOG_WRITEUP"
SOURCE_TYPE_OTHER = "OTHER"
SOURCE_TYPE_UNKNOWN = "UNKNOWN"

# ---- content classification categories (section 5: A/B/C/D) ----------------------------------
CLS_INDIVIDUAL = "A_INDIVIDUAL_WRITEUP"
CLS_INDEX = "B_MULTI_CHALLENGE_INDEX"
CLS_OFFICIAL = "C_OFFICIAL_EVENT_PAGE"
CLS_OTHER = "D_OTHER_NON_WRITEUP"
CLS_AMBIGUOUS = "AMBIGUOUS"

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

_YEAR_HEADER_RE = re.compile(r"^\s*(20\d{2})\b(.*)$")
_NO_ARCHIVE_RE = re.compile(r"did not find|no verified|was not identified|not verified", re.IGNORECASE)


@dataclass
class Reference:
    ref_id: str
    year: Optional[int]
    event: str
    challenge_name: Optional[str]
    url: str
    source_title: str
    source_author: Optional[str]
    source_type: str
    original_reference: bool = True
    provenance: str = "uploaded reference document: DomeCTF_CTF_Writeups_Reference_Links (1).docx"
    verification_status: str = "PENDING"
    section_note: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class DocMeta:
    title: str = ""
    subtitle: str = ""
    intro: str = ""
    year_notes: Dict[str, str] = field(default_factory=dict)
    study_order: List[str] = field(default_factory=list)
    verification_note: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


# --------------------------------------------------------------------------------------------
# docx parsing
# --------------------------------------------------------------------------------------------

def _para_runs(para, rels: Dict[str, str]):
    """Yield ('text', str) and ('link', (anchor_text, target)) tuples in document order."""
    import xml.etree.ElementTree as ET  # local import keeps module import light

    for child in para:
        tag = child.tag
        if tag == f"{_W}hyperlink":
            rid = child.get(f"{_R}id")
            target = rels.get(rid, "")
            text = "".join(t.text or "" for t in child.iter(f"{_W}t"))
            yield ("link", (text.strip(), target))
        elif tag == f"{_W}r":
            text = "".join(t.text or "" for t in child.iter(f"{_W}t"))
            if text:
                yield ("text", text)


def parse_reference_docx(path) -> Tuple[List[Reference], DocMeta]:
    """Parse the reference .docx into (references, doc_meta), grouped by its year sections.

    Deterministic and network-free. The URL set, year grouping, challenge names and authors are all
    taken directly from the document (anchor text + section headers), so the inventory is a faithful,
    reproducible projection of the source document rather than an inferred reconstruction.
    """
    import xml.etree.ElementTree as ET

    z = zipfile.ZipFile(path)
    rels_xml = z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
    rels = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels_xml))
    root = ET.fromstring(z.read("word/document.xml").decode("utf-8", "replace"))

    refs: List[Reference] = []
    meta = DocMeta()
    cur_year: Optional[int] = None
    cur_event = ""
    pending_note = ""
    seq = 0
    paras = list(root.iter(f"{_W}p"))
    section_mode = "header"  # header | study_order

    for para in paras:
        runs = list(_para_runs(para, rels))
        full = "".join(r[1] if r[0] == "text" else r[1][0] for r in runs).strip()
        links = [r[1] for r in runs if r[0] == "link" and r[1][1].lower().startswith("http")]

        if not full and not links:
            continue

        # Document header / intro lines (before the first year section).
        if cur_year is None and not links:
            if not meta.title:
                meta.title = full
            elif not meta.subtitle:
                meta.subtitle = full
            elif not meta.intro:
                meta.intro = full

        ym = _YEAR_HEADER_RE.match(full)
        if ym and not links:
            cur_year = int(ym.group(1))
            cur_event = ym.group(2).strip(" —-\u2014").strip()
            pending_note = ""
            section_mode = "header"
            continue

        if full.lower().startswith("quick study order"):
            section_mode = "study_order"
            continue
        if full.lower().startswith("source verification note"):
            meta.verification_note = full
            section_mode = "note"
            continue

        if section_mode == "study_order" and not links:
            meta.study_order.append(full)
            continue

        # A plain descriptive/"no archive" note within a year section.
        if not links:
            if cur_year is not None and _NO_ARCHIVE_RE.search(full):
                meta.year_notes[str(cur_year)] = full
                pending_note = full
            elif cur_year is not None and not pending_note:
                pending_note = full  # e.g., "Official Beagle Security archive + individual ..."
            continue

        # One or more hyperlinks on this line -> one reference each.
        for anchor, target in links:
            seq += 1
            stype = derive_source_type(anchor, target)
            challenge, author = derive_challenge_and_author(anchor, target, stype)
            refs.append(
                Reference(
                    ref_id=f"domectf-ref-{seq:03d}",
                    year=cur_year,
                    event=cur_event or (f"DomeCTF {cur_year}" if cur_year else ""),
                    challenge_name=challenge,
                    url=target,
                    source_title=anchor,
                    source_author=author,
                    source_type=stype,
                    section_note=pending_note or None,
                )
            )
    return refs, meta


# --------------------------------------------------------------------------------------------
# source_type + challenge/author derivation (deterministic, anchor + host driven)
# --------------------------------------------------------------------------------------------

def derive_source_type(anchor: str, url: str) -> str:
    host = urlparse(url).netloc.lower()
    a = anchor.lower()
    path = urlparse(url).path.lower()

    if "c0c0n.org" in host:
        return OFFICIAL_EVENT_PAGE
    # Index / recap / archive language in the anchor.
    is_indexish = any(k in a for k in ("index", "recap", "archive"))
    is_official_indexish = "official" in a and any(k in a for k in ("index", "event", "recap"))
    if "github.com" in host:
        return GITHUB_WRITEUP
    if "medium.com" in host:
        return MEDIUM_WRITEUP
    if "beaglesecurity.com" in host:
        if "/tag/" in path:
            return WRITEUP_INDEX
        if is_official_indexish or "writeup index" in a or "event/writeup" in a:
            return OFFICIAL_WRITEUP_INDEX
        if is_indexish:
            return WRITEUP_INDEX
        if path.endswith("-writeup.html"):
            return INDIVIDUAL_WRITEUP
        return BLOG_WRITEUP
    # Other hosts (appfabs recap/index, rahulr.in walkthrough, ...).
    if is_indexish:
        return WRITEUP_INDEX
    if "walkthrough" in a:
        return BLOG_WRITEUP
    return BLOG_WRITEUP if host else SOURCE_TYPE_UNKNOWN


_INDIVIDUAL_TYPES = {INDIVIDUAL_WRITEUP, GITHUB_WRITEUP, MEDIUM_WRITEUP}
_HOST_HINT_RE = re.compile(r"\s*\((github|medium|blog)\)\s*$", re.IGNORECASE)


def derive_challenge_and_author(anchor: str, url: str, source_type: str) -> Tuple[Optional[str], Optional[str]]:
    """Take challenge name + author only from the anchor text, and only for individual writeups.

    Index / official / walkthrough references do not name a single challenge, so both stay None.
    """
    if source_type not in _INDIVIDUAL_TYPES:
        return None, None
    text = anchor.strip()
    author = None
    challenge = text
    # Anchor convention in the doc: "<Challenge> — <Author> (<Host>)".
    for dash in ("\u2014", " - ", " – "):
        if dash in text:
            left, right = text.split(dash, 1)
            challenge = left.strip()
            author = _HOST_HINT_RE.sub("", right).strip() or None
            break
    challenge = challenge.strip()
    return (challenge or None), author


# --------------------------------------------------------------------------------------------
# content-based classification (evidence-driven; requires a fetched page)
# --------------------------------------------------------------------------------------------

_WRITEUP_LINK_RE = re.compile(r'href=["\']([^"\']+?-writeup\.html)(?:[#?][^"\']*)?["\']', re.IGNORECASE)
_ANY_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
_CODE_RE = re.compile(r"<pre[\s>]|<code[\s>]|```")
_SCRIPT_RE = re.compile(r"<script[\s>]", re.IGNORECASE)
_SOLUTION_CUE_RE = re.compile(r"\bflag\b|\bpayload\b|\bexploit\b|\bsolution\b|\bwe (?:solve|got|found)\b", re.IGNORECASE)
_EVENT_CUE_RE = re.compile(r"register|schedule|sponsor|leaderboard|rules|prize|agenda|conference", re.IGNORECASE)

# Verification thresholds (shared so the driver and tests agree).
SUBSTANTIVE_MIN = 200   # min stripped body-text chars to count as "meaningful content"
RENDER_SCRIPT_MIN = 3   # >= this many <script> tags on a near-empty page -> render_required


def is_soft_404(final_url: str, redirect_chain) -> bool:
    """True if the request landed on a site 404 page (directly or via a redirect hop to '/404').

    Some sites answer moved/removed writeups with HTTP 200 on a '/404' page (a "soft 404"); treating
    those as accessible would be wrong, so we surface them as NOT_FOUND.
    """
    def _is404(u: str) -> bool:
        path = urlparse(u or "").path.rstrip("/").lower()
        return path.endswith("/404") or path == "/404"

    if _is404(final_url):
        return True
    for hop in redirect_chain or ():
        if _is404(hop.get("to", "")):
            return True
    return False


def derive_accessibility(
    *,
    ok_transport: bool,
    http_status: Optional[int],
    final_url: str,
    redirect_chain,
    body_text_len: int,
    num_scripts: int,
) -> Tuple[str, bool, bool]:
    """Map a fetch outcome to (accessibility_status, meaningful_content, render_required).

    Keeps source *accessibility* (this result) separate from source *existence*: a blocked/failed
    fetch is never treated as proof the source does not exist.
    """
    if not ok_transport:
        return "NETWORK_FAILURE", False, False
    if http_status in (404, 410) or is_soft_404(final_url, redirect_chain):
        return "NOT_FOUND", False, False
    if http_status in (401, 403, 429):
        return "ACCESS_BLOCKED", False, False
    if http_status is not None and http_status >= 500:
        return "OTHER_FAILURE", False, False
    if http_status is not None and 300 <= http_status < 400:
        return "REDIRECTED", False, False
    # 2xx
    if body_text_len < SUBSTANTIVE_MIN and num_scripts >= RENDER_SCRIPT_MIN:
        return "RENDER_REQUIRED", False, True
    if body_text_len < SUBSTANTIVE_MIN:
        return "EMPTY_CONTENT", False, False
    return "ACCESSIBLE", True, False


def count_scripts(html: str) -> int:
    return len(_SCRIPT_RE.findall(html or ""))


def classify_content(
    *,
    url: str,
    title: str,
    headings: List[str],
    body_text: str,
    html: str,
    declared_type: str,
) -> Tuple[str, Dict[str, object]]:
    """Classify a fetched page into A/B/C/D (or AMBIGUOUS), recording the evidence used.

    Design notes grounded in the actual corpus:
    - Never returns INDIVIDUAL from a title alone — it requires solution-bearing content (a code
      block, or solution/exploit/flag cues).
    - The raw count of ``*-writeup.html`` links is NOT a reliable index signal on some hosts (e.g.
      Beagle Security renders a constant "related writeups" nav sidebar on *every* page, individual
      writeups included). So the A/B discriminator is the presence of the page's OWN solution
      content: an index/recap page lists writeups but carries no solution content of its own. The
      link count is still recorded as evidence for transparency.
    """
    host = urlparse(url).netloc.lower()
    text_len = len(body_text.strip())
    writeup_links = sorted(set(_WRITEUP_LINK_RE.findall(html)))
    n_writeup_links = len(writeup_links)
    n_headings = len(headings)
    has_code = bool(_CODE_RE.search(html))
    n_solution_cues = len(_SOLUTION_CUE_RE.findall(body_text))
    n_event_cues = len(_EVENT_CUE_RE.findall(body_text))
    has_solution_content = has_code or n_solution_cues >= 1

    evidence = {
        "host": host,
        "title": title[:200],
        "text_length": text_len,
        "num_headings": n_headings,
        "num_writeup_links": n_writeup_links,
        "has_code_block": has_code,
        "solution_cue_hits": n_solution_cues,
        "event_cue_hits": n_event_cues,
        "has_solution_content": has_solution_content,
        "declared_source_type": declared_type,
        "link_count_note": "num_writeup_links may include site-navigation chrome; solution content is the primary A/B discriminator",
    }

    # Not enough content retrieved to classify on evidence.
    if text_len < 120 and not has_code:
        return CLS_AMBIGUOUS, {**evidence, "reason": "insufficient retrieved content to classify"}

    # C. Official event page: the official conference host.
    if "c0c0n.org" in host:
        return CLS_OFFICIAL, {**evidence, "reason": "official conference host (c0c0n.org)"}

    # B. Multi-challenge index/collection: lists many per-challenge writeups but carries no
    #    solution content of its own.
    if n_writeup_links >= 5 and not has_solution_content:
        return CLS_INDEX, {**evidence, "reason": f"{n_writeup_links} per-writeup links and no own solution content", "writeup_links_sample": writeup_links[:10]}

    # A. Individual writeup: substantial single-page solution-bearing content.
    if has_solution_content and text_len >= 500:
        return CLS_INDIVIDUAL, {**evidence, "reason": "solution-bearing single-page content (code/exploit/flag)"}

    # C (fallback). Event-info page: event language, no solution content, not a link index.
    if n_event_cues >= 2 and not has_solution_content and n_writeup_links < 5:
        return CLS_OFFICIAL, {**evidence, "reason": "event-info language without solution content or index structure"}

    # D. Other non-writeup material: readable, no solution content, not an index.
    if not has_solution_content and n_writeup_links < 5:
        return CLS_OTHER, {**evidence, "reason": "readable page without solution content or index structure"}

    return CLS_AMBIGUOUS, {**evidence, "reason": "signals conflict; needs manual review"}


def extract_writeup_links(html: str, base_url: str) -> List[Dict[str, str]]:
    """Return same-site '*-writeup.html' links found on an index page (never followed here).

    Only same-host DomeCTF-looking writeup links are returned, so this stays an inventory helper,
    not a crawler. Fragment/query stripped; de-duplicated; absolute-ized against ``base_url``.
    """
    from urllib.parse import urljoin

    base_host = urlparse(base_url).netloc.lower()
    out: List[Dict[str, str]] = []
    seen = set()
    for href in _WRITEUP_LINK_RE.findall(html):
        absolute = urljoin(base_url, href).split("#", 1)[0]
        if urlparse(absolute).netloc.lower() != base_host:
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        slug = urlparse(absolute).path.rsplit("/", 1)[-1]
        out.append({"url": absolute, "path_slug": slug})
    return out


def canonical_url(url: str) -> str:
    """A conservative canonical form for duplicate detection: lowercase host, strip fragment,
    trailing slash, and a leading 'www.'. Does NOT merge distinct paths."""
    p = urlparse(url)
    host = p.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = p.path.rstrip("/") or "/"
    return f"{p.scheme.lower()}://{host}{path}"
