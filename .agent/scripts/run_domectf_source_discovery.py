"""DomeCTF historical source discovery + verification (INVENTORY ONLY — no knowledge extraction).

Pipeline:
  reference .docx  ->  structured inventory  ->  respectful HTTP verification  ->  raw cache
                   ->  evidence-based classification  ->  discovered-link inventory
                   ->  coverage + dedup  ->  artifacts

What this script does NOT do (by design / task constraints):
  - no knowledge records, techniques, trajectories, retrieval, solver, benchmark, fine-tuning
  - no arbitrary crawling: it fetches ONLY the explicitly referenced URLs, plus (optionally) the
    same-host "*-writeup.html" links that an explicitly referenced INDEX/OFFICIAL page directly
    lists — and even those are primarily inventoried; a bounded number are fetched for
    accessibility only, with provenance kept distinct.
  - no JS rendering: static HTTP is tried; pages that need JS are flagged render_required=true and
    reported separately (a renderer is NOT invoked here).

Respectful fetch: stdlib urllib, descriptive User-Agent, timeouts, a polite inter-request delay,
records status / final URL / redirect chain / content-type / sha256 / timestamp. Raw bytes are
written once and never overwritten (immutable). Everything lives under the isolated namespace
knowledge/domectf_sources_v1/ and is fully re-runnable.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
import time
import zlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest.domectf_discovery import (  # noqa: E402
    CLS_AMBIGUOUS,
    CLS_INDEX,
    CLS_INDIVIDUAL,
    CLS_OFFICIAL,
    canonical_url,
    classify_content,
    count_scripts,
    derive_accessibility,
    derive_source_type,
    extract_writeup_links,
    parse_reference_docx,
)
from ctf_ingest.models import MediaType, Provenance, RawDocument, SourceType  # noqa: E402
from ctf_ingest.normalize import normalize  # noqa: E402

DOCX = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    AGENT_ROOT.parent / "DomeCTF_CTF_Writeups_Reference_Links (1).docx"
)
NS = AGENT_ROOT / "knowledge" / "domectf_sources_v1"
RAW = NS / "raw"
MANIFESTS = NS / "manifests"
REPORTS = NS / "reports"
CACHE = NS / "cache"  # per-URL fetch metadata; makes re-runs network-free + idempotent

USER_AGENT = (
    "CTF-Research-SourceInventory/1.0 (+respectful verification of explicitly-referenced DomeCTF "
    "writeup URLs; contact: local研究 agent; no crawling)"
).encode("ascii", "ignore").decode("ascii")
TIMEOUT = 25
POLITE_DELAY_S = 1.3
SUBSTANTIVE_MIN = 200          # min stripped body-text chars to count as "meaningful content"
RENDER_SCRIPT_MIN = 3          # >= this many <script> tags with tiny text -> render_required
DISCOVERED_FETCH_CAP = 30      # bound on discovered (non-explicit) writeups fetched for accessibility


# --------------------------------------------------------------------------------------------
# respectful static HTTP fetch
# --------------------------------------------------------------------------------------------

def _make_opener():
    chain: list = []

    class _Recorder(request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            chain.append({"from": req.full_url, "to": newurl, "code": code})
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = request.build_opener(_Recorder)
    return opener, chain


def _decode_body(raw_bytes: bytes, content_encoding: str) -> bytes:
    ce = (content_encoding or "").lower()
    try:
        if "gzip" in ce:
            return gzip.decompress(raw_bytes)
        if "deflate" in ce:
            try:
                return zlib.decompress(raw_bytes)
            except zlib.error:
                return zlib.decompress(raw_bytes, -zlib.MAX_WBITS)
    except Exception:
        return raw_bytes
    return raw_bytes


def _cache_path(url: str) -> Path:
    return CACHE / (hashlib.sha256(url.encode("utf-8")).hexdigest()[:24] + ".json")


def fetch(url: str) -> dict:
    """Cache-first respectful GET: reuse a prior fetch if cached, else fetch once and cache.

    This makes the whole pipeline idempotent and network-free on re-runs (so classification logic
    can be iterated without re-hitting external sites). Network metadata is cached per URL; the raw
    body lives in the immutable raw/ store.
    """
    cp = _cache_path(url)
    if cp.exists():
        meta = json.loads(cp.read_text(encoding="utf-8"))
        raw_file = RAW / _slug("src", url)
        meta["body_bytes"] = raw_file.read_bytes() if raw_file.exists() else b""
        return meta
    res = _fetch_network(url)
    # Immutability: if a raw body was already stored by a prior run, it stays authoritative.
    raw_file = RAW / _slug("src", url)
    if raw_file.exists():
        stored = raw_file.read_bytes()
        if stored != res["body_bytes"]:
            res["body_bytes"] = stored
            res["content_sha256"] = hashlib.sha256(stored).hexdigest()
            res["content_length_bytes"] = len(stored)
            res["stored_raw_differs_from_refetch"] = True
    elif res["body_bytes"]:
        _write_raw_once(_slug("src", url), res["body_bytes"])
    CACHE.mkdir(parents=True, exist_ok=True)
    meta = {k: v for k, v in res.items() if k != "body_bytes"}
    if not cp.exists():
        cp.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    time.sleep(POLITE_DELAY_S)  # politeness only applies to real network fetches
    return res


def _fetch_network(url: str) -> dict:
    """Respectful single GET. Returns a dict with status/final_url/redirects/content/sha256/etc.

    Never raises for HTTP/network errors — they are captured as structured outcomes so that source
    *existence* and source *accessibility* stay separate and no failure is treated as non-existence.
    """
    opener, chain = _make_opener()
    req = request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    })
    retrieved_at = datetime.now(timezone.utc).isoformat()
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
            body = _decode_body(raw, resp.headers.get("Content-Encoding", ""))
            return {
                "ok_transport": True,
                "http_status": resp.status,
                "final_url": resp.geturl(),
                "redirect_chain": chain,
                "content_type": resp.headers.get("Content-Type", ""),
                "content_length_bytes": len(body),
                "content_sha256": hashlib.sha256(body).hexdigest(),
                "retrieved_at": retrieved_at,
                "body_bytes": body,
                "error": None,
            }
    except error.HTTPError as exc:
        try:
            raw = exc.read()
            body = _decode_body(raw, exc.headers.get("Content-Encoding", "") if exc.headers else "")
        except Exception:
            body = b""
        return {
            "ok_transport": True,
            "http_status": exc.code,
            "final_url": getattr(exc, "url", url),
            "redirect_chain": chain,
            "content_type": (exc.headers.get("Content-Type", "") if exc.headers else ""),
            "content_length_bytes": len(body),
            "content_sha256": hashlib.sha256(body).hexdigest() if body else "",
            "retrieved_at": retrieved_at,
            "body_bytes": body,
            "error": f"HTTPError {exc.code} {exc.reason}",
        }
    except (error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        return {
            "ok_transport": False,
            "http_status": None,
            "final_url": url,
            "redirect_chain": chain,
            "content_type": "",
            "content_length_bytes": 0,
            "content_sha256": "",
            "retrieved_at": retrieved_at,
            "body_bytes": b"",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _accessibility(res: dict, body_text: str, html: str) -> tuple[str, bool, bool]:
    """Delegate to the shared, tested classifier logic (keeps script + tests in agreement)."""
    return derive_accessibility(
        ok_transport=res["ok_transport"],
        http_status=res["http_status"],
        final_url=res["final_url"],
        redirect_chain=res["redirect_chain"],
        body_text_len=len(body_text.strip()),
        num_scripts=count_scripts(html),
    )


def _slug(prefix: str, url: str) -> str:
    seg = re.sub(r"[^a-zA-Z0-9._-]+", "_", url.split("//", 1)[-1])[:120].strip("_")
    return f"{prefix}__{seg}.html"


def _write_raw_once(filename: str, body_bytes: bytes) -> str:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / filename
    if not path.exists() and body_bytes:
        path.write_bytes(body_bytes)  # immutable: written once, never overwritten
    return str(path.relative_to(AGENT_ROOT)) if path.exists() else ""


def _normalize_html(url: str, body_bytes: bytes) -> tuple[str, list[str], str, str]:
    """Return (title, headings, body_text, html_str) using the existing normalizer."""
    html = body_bytes.decode("utf-8", "replace")
    doc = RawDocument(
        doc_id=hashlib.sha256(url.encode()).hexdigest()[:16],
        media_type=MediaType.HTML,
        text=html,
        provenance=Provenance(SourceType.HTTP, url, ""),
    )
    w = normalize(doc)
    headings = [s.heading for s in (w.sections or ()) if s.heading]
    return w.title, headings, w.body_text, html


def _verify_one(url: str, *, is_index_like: bool) -> tuple[dict, dict | None]:
    """Fetch + classify one URL. Returns (verification_record, manifest_entry_or_None)."""
    res = fetch(url)
    body_text, html, title, headings = "", "", "", []
    if res["body_bytes"]:
        title, headings, body_text, html = _normalize_html(url, res["body_bytes"])
    status, meaningful, render_required = _accessibility(res, body_text, html)

    classification, evidence = (None, None)
    if meaningful:
        classification, evidence = classify_content(
            url=url, title=title, headings=headings, body_text=body_text, html=html,
            declared_type=derive_source_type(title or url, url),
        )

    redirected = bool(res["redirect_chain"]) or (res["final_url"] and res["final_url"] != url)
    rec = {
        "url": url,
        "final_url": res["final_url"],
        "redirected": redirected,
        "redirect_chain": res["redirect_chain"],
        "http_status": res["http_status"],
        "content_type": res["content_type"],
        "content_length_bytes": res["content_length_bytes"],
        "content_sha256": res["content_sha256"],
        "retrieved_at": res["retrieved_at"],
        "accessibility": status,
        "meaningful_content": meaningful,
        "render_required": render_required,
        "source_exists": "confirmed" if meaningful else "unverified",
        "content_classification": classification,
        "classification_evidence": evidence,
        "page_title": title[:200] if title else "",
        "body_text_len": len(body_text.strip()),
        "transport_error": res["error"],
    }
    manifest_entry = None
    if res["body_bytes"]:
        fname = _slug("src", url)
        rel = _write_raw_once(fname, res["body_bytes"])
        manifest_entry = {
            "source_url": url,
            "final_url": res["final_url"],
            "raw_artifact": rel,
            "sha256": res["content_sha256"],
            "retrieved_at": res["retrieved_at"],
            "http_status": res["http_status"],
            "content_length_bytes": res["content_length_bytes"],
            "content_type": res["content_type"],
            "provenance": "explicit_reference",
        }
    return rec, manifest_entry


# --------------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------------

def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    if not DOCX.exists():
        print(f"ABORT: reference docx not found at {DOCX}")
        return 3
    for d in (RAW, MANIFESTS, REPORTS):
        d.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()
    refs, meta = parse_reference_docx(DOCX)

    # ---- 1. INVENTORY -----------------------------------------------------------------------
    inventory = {
        "generated_at": generated_at,
        "reference_document": DOCX.name,
        "document_meta": meta.to_dict(),
        "total_explicit_references": len(refs),
        "years_inventoried": ["2019", "2020", "2021", "2022", "2023", "2024", "2025"],
        "references": [r.to_dict() for r in refs],
        "years_without_verified_complete_archive": sorted(meta.year_notes.keys()),
    }
    _write_json(REPORTS / "domectf_source_inventory.json", inventory)

    # ---- 2. VERIFY EXPLICIT SOURCES ---------------------------------------------------------
    verifications: list[dict] = []
    manifest_entries: list[dict] = []
    index_like_types = {"OFFICIAL_WRITEUP_INDEX", "WRITEUP_INDEX", "OFFICIAL_EVENT_PAGE"}
    explicit_canon = {canonical_url(r.url) for r in refs}

    for r in refs:
        is_index = r.source_type in index_like_types
        rec, man = _verify_one(r.url, is_index_like=is_index)
        rec.update({"ref_id": r.ref_id, "year": r.year, "declared_source_type": r.source_type,
                    "challenge_name": r.challenge_name})
        verifications.append(rec)
        if man:
            manifest_entries.append(man)
        # reflect verification status back onto the inventory reference
        for inv_ref in inventory["references"]:
            if inv_ref["ref_id"] == r.ref_id:
                inv_ref["verification_status"] = rec["accessibility"]

    # ---- 3. DISCOVERED LINKS (from explicit index/official pages only) ----------------------
    discovered: list[dict] = []
    discovered_seen = set()
    # Map ref_id -> raw html for index-like pages that returned content.
    for r in refs:
        if r.source_type not in index_like_types:
            continue
        vrec = next((v for v in verifications if v["ref_id"] == r.ref_id), None)
        if not vrec or not vrec["meaningful_content"]:
            continue
        raw_file = RAW / _slug("src", r.url)
        if not raw_file.exists():
            continue
        html = raw_file.read_bytes().decode("utf-8", "replace")
        base = vrec["final_url"] or r.url
        for link in extract_writeup_links(html, base):
            durl = link["url"]
            curl = canonical_url(durl)
            if curl in discovered_seen:
                continue
            discovered_seen.add(curl)
            already_explicit = curl in explicit_canon
            discovered.append({
                "originating_url": r.url,
                "originating_ref_id": r.ref_id,
                "discovered_url": durl,
                "challenge_name": None,  # not inferred from URL; anchor text unavailable via static index
                "source_type": derive_source_type("", durl),
                "source_origin": "DISCOVERED_FROM_EXPLICIT_SOURCE",
                "already_in_explicit_references": already_explicit,
                "relevance_reason": "same-host '*-writeup.html' link directly listed on an explicitly referenced index/official page",
                "fetched": False,
                "verification": None,
            })

    # Fetch ONLY discovered individual writeups that are NOT already explicit (bounded, accessibility only).
    to_fetch = [d for d in discovered if not d["already_in_explicit_references"]][:DISCOVERED_FETCH_CAP]
    for d in to_fetch:
        rec, man = _verify_one(d["discovered_url"], is_index_like=False)
        d["fetched"] = True
        d["verification"] = {
            "http_status": rec["http_status"], "final_url": rec["final_url"],
            "accessibility": rec["accessibility"], "meaningful_content": rec["meaningful_content"],
            "render_required": rec["render_required"], "content_classification": rec["content_classification"],
            "content_sha256": rec["content_sha256"], "retrieved_at": rec["retrieved_at"],
        }
        if man:
            man["provenance"] = "discovered_from_explicit_source"
            manifest_entries.append(man)

    # ---- 4. COVERAGE + DEDUP ----------------------------------------------------------------
    coverage = _coverage(refs, verifications)
    dedup = _dedup(refs, verifications, manifest_entries)

    verification_doc = {
        "generated_at": generated_at,
        "fetcher": {"mechanism": "stdlib urllib (respectful static HTTP)", "user_agent": USER_AGENT,
                    "timeout_s": TIMEOUT, "polite_delay_s": POLITE_DELAY_S,
                    "note": "no JS rendering performed; render-required pages flagged, not rendered"},
        "accessibility_status_values": ["ACCESSIBLE", "REDIRECTED", "NOT_FOUND", "ACCESS_BLOCKED",
                                        "NETWORK_FAILURE", "RENDER_REQUIRED", "EMPTY_CONTENT",
                                        "AMBIGUOUS", "OTHER_FAILURE"],
        "total_explicit_references": len(refs),
        "results": verifications,
        "coverage": coverage,
        "deduplication": dedup,
    }
    _write_json(REPORTS / "domectf_source_verification.json", verification_doc)
    _write_json(REPORTS / "domectf_discovered_sources.json", {
        "generated_at": generated_at,
        "note": "sources discovered while verifying explicitly referenced index/official pages; "
                "provenance kept distinct from original document references; not recursively crawled",
        "discovery_scope": "same-host '*-writeup.html' links listed directly on explicit index/official pages",
        "total_discovered": len(discovered),
        "already_in_explicit_references": sum(1 for d in discovered if d["already_in_explicit_references"]),
        "new_discovered": sum(1 for d in discovered if not d["already_in_explicit_references"]),
        "fetched_for_accessibility": sum(1 for d in discovered if d["fetched"]),
        "discovered": discovered,
    })
    _write_json(MANIFESTS / "domectf_source_manifest.json", {
        "generated_at": generated_at,
        "raw_dir": str(RAW.relative_to(AGENT_ROOT)),
        "immutability": "raw artifacts are written once and never overwritten",
        "count": len(manifest_entries),
        "entries": manifest_entries,
    })

    _write_report(generated_at, refs, meta, verifications, coverage, dedup, discovered)

    # ---- console summary --------------------------------------------------------------------
    acc = Counter(v["accessibility"] for v in verifications)
    cls = Counter(v["content_classification"] for v in verifications if v["content_classification"])
    print(f"DomeCTF source discovery complete -> {NS}")
    print(f"  explicit references: {len(refs)} | accessible: {acc.get('ACCESSIBLE', 0)}")
    print(f"  accessibility: {dict(acc)}")
    print(f"  content classification: {dict(cls)}")
    print(f"  discovered links: {len(discovered)} (new: {sum(1 for d in discovered if not d['already_in_explicit_references'])}, "
          f"fetched: {sum(1 for d in discovered if d['fetched'])})")
    print(f"  duplicate URLs: {dedup['duplicate_url_count']} | duplicate content hashes: {dedup['duplicate_content_hash_count']} | redirects: {dedup['redirect_count']}")
    return 0


def _coverage(refs, verifications) -> dict:
    by_year_refs = defaultdict(list)
    for r in refs:
        by_year_refs[str(r.year)].append(r)
    vindex = {v["ref_id"]: v for v in verifications}

    per_year = {}
    for year in ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]:
        yrefs = by_year_refs.get(year, [])
        vlist = [vindex[r.ref_id] for r in yrefs if r.ref_id in vindex]
        per_year[year] = {
            "references_listed": len(yrefs),
            "accessible": sum(1 for v in vlist if v["accessibility"] == "ACCESSIBLE"),
            "inaccessible": sum(1 for v in vlist if v["accessibility"] not in ("ACCESSIBLE",)),
            "individual_writeups": sum(1 for v in vlist if v["content_classification"] == CLS_INDIVIDUAL),
            "indexes": sum(1 for v in vlist if v["content_classification"] == CLS_INDEX),
            "official_event_pages": sum(1 for v in vlist if v["content_classification"] == CLS_OFFICIAL),
            "other_or_unclassified": sum(1 for v in vlist if v["content_classification"] in (None, "D_OTHER_NON_WRITEUP", CLS_AMBIGUOUS)),
            "render_required": sum(1 for v in vlist if v["render_required"]),
        }

    totals = {
        "total_explicit_references": len(refs),
        "total_accessible": sum(1 for v in verifications if v["accessibility"] == "ACCESSIBLE"),
        "total_individual_writeups": sum(1 for v in verifications if v["content_classification"] == CLS_INDIVIDUAL),
        "total_index_or_recap_pages": sum(1 for v in verifications if v["content_classification"] == CLS_INDEX),
        "total_official_pages": sum(1 for v in verifications if v["content_classification"] == CLS_OFFICIAL),
        "total_inaccessible_or_dead": sum(1 for v in verifications if v["accessibility"] in ("NOT_FOUND", "NETWORK_FAILURE", "OTHER_FAILURE")),
        "total_access_blocked": sum(1 for v in verifications if v["accessibility"] == "ACCESS_BLOCKED"),
        "total_render_required": sum(1 for v in verifications if v["render_required"]),
        "total_ambiguous_classifications": sum(1 for v in verifications if v["content_classification"] == CLS_AMBIGUOUS),
    }
    return {"per_year": per_year, "totals": totals}


def _dedup(refs, verifications, manifest_entries) -> dict:
    url_counts = Counter(r.url for r in refs)
    dup_urls = {u: c for u, c in url_counts.items() if c > 1}
    canon_counts = Counter(canonical_url(r.url) for r in refs)
    dup_canon = {u: c for u, c in canon_counts.items() if c > 1}
    hash_counts = Counter(v["content_sha256"] for v in verifications if v["content_sha256"])
    dup_hashes = {h: c for h, c in hash_counts.items() if c > 1}
    # Map duplicate hashes back to the URLs that produced them (provenance preserved, not merged).
    hash_to_urls = defaultdict(list)
    for v in verifications:
        if v["content_sha256"] and v["content_sha256"] in dup_hashes:
            hash_to_urls[v["content_sha256"]].append(v["url"])
    redirects = [{"url": v["url"], "final_url": v["final_url"], "chain": v["redirect_chain"]}
                 for v in verifications if v["redirected"]]
    return {
        "policy": "duplicates are reported with provenance preserved; distinct challenges are never merged",
        "duplicate_url_count": len(dup_urls),
        "duplicate_urls": dup_urls,
        "duplicate_canonical_url_count": len(dup_canon),
        "duplicate_canonical_urls": dup_canon,
        "duplicate_content_hash_count": len(dup_hashes),
        "duplicate_content_hashes": {h: hash_to_urls[h] for h in dup_hashes},
        "redirect_count": len(redirects),
        "redirects": redirects,
    }


def _write_report(generated_at, refs, meta, verifications, coverage, dedup, discovered) -> None:
    acc = Counter(v["accessibility"] for v in verifications)
    cls = Counter(v["content_classification"] for v in verifications if v["content_classification"])
    t = coverage["totals"]
    lines = [
        "# DomeCTF Historical Source Discovery & Verification Report", "",
        f"Generated: {generated_at}", "",
        "## Methodology", "",
        "- Source of truth: the uploaded reference document "
        "`DomeCTF_CTF_Writeups_Reference_Links (1).docx`. Every reference below is parsed directly "
        "from that document (year sections + hyperlink anchor text). Challenge names and authors are "
        "taken verbatim from anchor text — never inferred from URLs.",
        "- Verification: respectful static HTTP (stdlib urllib, descriptive User-Agent, timeouts, a "
        "polite inter-request delay). Only the explicitly referenced URLs were fetched, plus the "
        "same-host `*-writeup.html` links directly listed on explicitly referenced index/official "
        "pages (kept as DISCOVERED, provenance distinct).",
        "- No JS rendering: pages needing JavaScript are flagged `render_required=true` and reported "
        "separately; a renderer was not invoked.",
        "- No knowledge extraction: no technique/knowledge/trajectory/retrieval/solver artifacts were "
        "created. Raw pages are cached immutably under `knowledge/domectf_sources_v1/raw/`.",
        "",
        "## Coverage by year", "",
        "| year | event | refs listed | accessible | individual | index | official | render-req |",
        "|---|---|---|---|---|---|---|---|",
    ]
    event_by_year = {str(r.year): r.event for r in refs}
    for year, c in coverage["per_year"].items():
        lines.append(
            f"| {year} | {event_by_year.get(year, '')} | {c['references_listed']} | {c['accessible']} | "
            f"{c['individual_writeups']} | {c['indexes']} | {c['official_event_pages']} | {c['render_required']} |"
        )
    lines += [
        "",
        "### Years explicitly marked in the document as NOT having a verified complete "
        "challenge-by-challenge public archive", "",
    ]
    for y in sorted(meta.year_notes.keys()):
        lines.append(f"- **{y}** — {meta.year_notes[y]}")
    lines += [
        "",
        "## Totals", "",
        f"- Total explicit references: {t['total_explicit_references']}",
        f"- Total accessible: {t['total_accessible']}",
        f"- Total individual challenge writeups (evidence-classified): {t['total_individual_writeups']}",
        f"- Total index/recap pages: {t['total_index_or_recap_pages']}",
        f"- Total official event pages: {t['total_official_pages']}",
        f"- Total inaccessible/dead (NOT_FOUND/NETWORK/OTHER): {t['total_inaccessible_or_dead']}",
        f"- Total access-blocked: {t['total_access_blocked']}",
        f"- Total render-required (JS): {t['total_render_required']}",
        f"- Total ambiguous classifications: {t['total_ambiguous_classifications']}",
        "",
        f"Accessibility distribution: {dict(acc)}",
        "",
        f"Content classification distribution: {dict(cls)}",
        "",
        "## Discovered sources (from explicit index/official pages)", "",
        f"- Total discovered same-host writeup links: {len(discovered)}",
        f"- Already in explicit references: {sum(1 for d in discovered if d['already_in_explicit_references'])}",
        f"- New (not in document): {sum(1 for d in discovered if not d['already_in_explicit_references'])}",
        f"- Fetched for accessibility (bounded): {sum(1 for d in discovered if d['fetched'])}",
        "",
        "Several of the document's 2021 (`/blog/domectf2021/*`) writeup URLs are dead (they redirect "
        "to the site 404 page). The live challenge writeups were recovered as DISCOVERED links from "
        "the explicitly referenced 2021 index page, at their canonical `/blog/domectf2020/*` paths. "
        "New discovered sources and their evidence-based classification:", "",
        "| discovered URL | accessibility | classification |",
        "|---|---|---|",
    ]
    for d in discovered:
        if d["already_in_explicit_references"]:
            continue
        v = d["verification"] or {}
        lines.append(f"| {d['discovered_url']} | {v.get('accessibility')} | {v.get('content_classification')} |")
    lines += [
        "",
        "## Duplicates", "",
        f"- Duplicate URLs: {dedup['duplicate_url_count']}",
        f"- Duplicate canonical URLs: {dedup['duplicate_canonical_url_count']}",
        f"- Duplicate content hashes: {dedup['duplicate_content_hash_count']}",
        f"- Redirects observed: {dedup['redirect_count']}",
        "",
        "## Render-required / JS sources", "",
    ]
    rr = [v for v in verifications if v["render_required"]]
    if rr:
        for v in rr:
            lines.append(f"- {v['url']} (status {v['http_status']}, text len {v['body_text_len']})")
    else:
        lines.append("- None: all accessible pages served meaningful static HTML.")
    lines += [
        "",
        "## Limitations", "",
        "- Classification is evidence-based from statically retrieved HTML; pages that block "
        "non-browser clients or require JS are reported as ACCESS_BLOCKED / RENDER_REQUIRED rather "
        "than classified, and their existence is left `unverified` (not treated as non-existent).",
        "- Discovered-link scope is intentionally narrow (same-host `*-writeup.html` on explicit "
        "index pages) to avoid becoming a crawler; other in-page links were not inventoried.",
        "- The document itself marks 2022–2025 as lacking a verified complete public writeup archive; "
        "this inventory preserves that and does not attempt an unrestricted search for missing archives.",
        "",
        "## Recommended next step", "",
        "Ready-for-extraction set (NEXT phase — challenge-level raw-source extraction/ingestion into "
        "an isolated namespace, NOT started here):",
        "- 2019: the 3 GitHub writeups (accessible) and the Rahul R walkthrough; the Medium writeup "
        "is ACCESS_BLOCKED to non-browser clients (exists; needs a browser/again later).",
        "- 2020 (c0c0n XIII): the 19 accessible Beagle Security individual writeups.",
        "- 2021 (c0c0n XIV): the 8 challenge writeups are usable via their DISCOVERED canonical "
        "`/blog/domectf2020/*` URLs (the document's `/blog/domectf2021/*` URLs are dead).",
        "- 2022/2023/2024/2025: official event pages only; the document confirms no verified complete "
        "public writeup archive, so there is no challenge-by-challenge set to extract for those years.",
        "",
        "Raw source is cached immutably; no extraction, retrieval, solver, or benchmark work was done.",
    ]
    (REPORTS / "domectf_source_discovery_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
