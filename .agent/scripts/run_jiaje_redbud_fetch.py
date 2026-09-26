"""Fetch the 22 explicitly-discovered Jia Jie Redbud writeup URLs (fetch-only, no ingestion).

Continuation of the approved Jia Jie discovery experiment. Uses the EXISTING isolated Playwright
JS source (ctf_ingest.js_source.render_urls). Fetches ONLY the exact 22 URLs derivable from
docs/jiaje_js_discovered_links.json — no crawling, enumeration, guessing, or link following.

Saves rendered raw source artifacts under knowledge/jiaje_redbud_v1/raw/. Does NOT build
KnowledgeRecords, does NOT connect to retrieval/solver, does NOT touch prior stores/artifacts.
Fails closed on render errors (recorded separately as failures).

Outputs:
  docs/jiaje_redbud_fetch_report.md
  docs/jiaje_redbud_fetch_manifest.json
  docs/jiaje_redbud_accessibility.json
  docs/jiaje_redbud_failures.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest.js_source import RendererUnavailable, render_urls  # noqa: E402

DISCOVERED = AGENT_ROOT / "docs" / "jiaje_js_discovered_links.json"
RAW_DIR = AGENT_ROOT / "knowledge" / "jiaje_redbud_v1" / "raw"
DOCS = AGENT_ROOT / "docs"
BOOK = "https://jia.je/ctf-writeups/"
AUTHOR = "Jiajie Chen (@jiegec)"
# The two already-ingested technique-reference pages are excluded from the per-challenge set.
EXCLUDE = {
    "https://jia.je/ctf-writeups/misc/solution.html",
    "https://jia.je/ctf-writeups/misc/pyjail.html",
}

# A true navigation/collection hub has LOW body text AND MANY outgoing writeup links (the two
# Redbud index hubs had ~366-860 chars of text and 11-15 links). Individual writeups have
# substantial body text; their small outgoing-link counts are dominated by prev/next chrome
# (~2) plus occasional in-content cross-references, so link-count alone is not a hub signal.
COLLECTION_TEXT_MAX = 900
COLLECTION_LINK_MIN = 8
# Below this rendered body-text length, a page is treated as thin/non-substantive.
SUBSTANTIVE_TEXT_MIN = 250


def _derive_targets() -> list[dict]:
    data = json.loads(DISCOVERED.read_text(encoding="utf-8"))
    seen = set()
    targets: list[dict] = []
    for page, info in data["pages"].items():
        for link in info["links"]:
            href = link["href"]
            if link["classification"] != "internal_book" or not link["in_content"]:
                continue
            path = href.split("#", 1)[0]
            if not path.endswith(".html") or path.rsplit("/", 1)[-1] == "index.html":
                continue
            if href in EXCLUDE or href in seen:
                continue
            seen.add(href)
            targets.append({"url": href, "discovered_from": page, "link_text": link.get("text", "")})
    return targets


def _event_and_challenge(url: str) -> tuple[str, str]:
    rel = url.replace(BOOK, "").split("#", 1)[0]
    parts = rel.split("/")
    top = parts[0]
    event = {
        "puppeteer": "Redbud Puppeteer",
        "summer2026": "Redbud Summer 2026",
    }.get(top)
    if event is None and "sunshine-ctf-2025" in top:
        event = "SunshineCTF 2025"
    event = event or top
    challenge = parts[-1][: -len(".html")] if parts[-1].endswith(".html") else parts[-1]
    # Preserve the week qualifier when explicitly present in the path.
    if len(parts) >= 3 and parts[1].startswith("week"):
        challenge = f"{parts[1]}/{challenge}"
    return event, challenge


def main() -> int:
    targets = _derive_targets()
    urls = [t["url"] for t in targets]
    meta_by_url = {t["url"]: t for t in targets}
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    if len(urls) != 22:
        print(f"ABORT: expected 22 derived URLs, got {len(urls)} — refusing to proceed.")
        return 3

    try:
        results = render_urls(urls, RAW_DIR)
    except RendererUnavailable as exc:
        payload = {"generated_at": generated_at, "status": "FAILED_CLOSED", "reason": str(exc), "urls": urls}
        (DOCS / "jiaje_redbud_failures.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (DOCS / "jiaje_redbud_fetch_report.md").write_text(
            f"# Jia Jie Redbud Fetch Report\n\nSTATUS: FAILED CLOSED — no JS renderer: {exc}\n", encoding="utf-8"
        )
        print("FAILED CLOSED:", exc)
        return 2

    successes, failures = [], []
    for r in results:
        event, challenge = _event_and_challenge(r.url)
        rec = {
            "source_url": r.url,
            "final_url": r.final_url,
            "http_status": r.http_status,
            "retrieved_at": r.retrieved_at,
            "content_sha256": r.content_sha256,
            "rendered_html_bytes": r.rendered_html_bytes,
            "rendered_text_len": r.rendered_text_len,
            "renderer": r.renderer,
            "renderer_version": r.renderer_version,
            "browser_version": r.browser_version,
            "event": event,
            "challenge_id": challenge,
            "discovered_from": meta_by_url[r.url]["discovered_from"],
            "provenance": {"author": AUTHOR, "source_index": BOOK, "license_note": "jia.je CTF writeups by Jiajie Chen"},
            "ok": r.ok,
        }
        if r.ok:
            rec["html_artifact"] = r.html_artifact
            rec["text_artifact"] = r.text_artifact
            rec["outgoing_writeup_link_candidates"] = r.writeup_link_candidates
            rec["page_kind"] = _classify_page(r)
            rec["substantive_writeup"] = rec["page_kind"] == "individual_writeup"
            successes.append(rec)
        else:
            rec["error"] = r.error
            failures.append(rec)

    # Duplicate content-hash detection among successful fetches.
    hash_counts = Counter(rec["content_sha256"] for rec in successes)
    duplicate_hashes = {h: c for h, c in hash_counts.items() if c > 1}

    manifest = {
        "generated_at": generated_at,
        "raw_dir": str(RAW_DIR),
        "urls_requested": len(urls),
        "urls_succeeded": len(successes),
        "urls_failed": len(failures),
        "renderer": f"playwright {results[0].renderer_version} / chromium {results[0].browser_version}" if results else "",
        "records": successes,
        "duplicate_content_hashes": duplicate_hashes,
    }
    (DOCS / "jiaje_redbud_fetch_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (DOCS / "jiaje_redbud_failures.json").write_text(
        json.dumps({"generated_at": generated_at, "count": len(failures), "failures": failures}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # Accessibility + distribution summary.
    status_counts = Counter(rec["http_status"] for rec in successes)
    event_counts = Counter(rec["event"] for rec in successes)
    kind_counts = Counter(rec["page_kind"] for rec in successes)
    accessibility = {
        "generated_at": generated_at,
        "urls_requested": len(urls),
        "urls_succeeded": len(successes),
        "urls_failed": len(failures),
        "http_status_distribution": dict(status_counts),
        "event_distribution": dict(event_counts),
        "page_kind_distribution": dict(kind_counts),
        "rendered_text_len": {rec["challenge_id"]: rec["rendered_text_len"] for rec in successes},
        "duplicate_content_hashes": duplicate_hashes,
        "substantive_writeups": sum(1 for rec in successes if rec["substantive_writeup"]),
    }
    (DOCS / "jiaje_redbud_accessibility.json").write_text(json.dumps(accessibility, indent=2, sort_keys=True), encoding="utf-8")

    _write_report(generated_at, urls, successes, failures, duplicate_hashes, event_counts, kind_counts)

    print(f"Redbud fetch complete: requested={len(urls)} ok={len(successes)} failed={len(failures)}")
    print(f"  events: {dict(event_counts)}")
    print(f"  page kinds: {dict(kind_counts)}")
    print(f"  duplicate content hashes: {len(duplicate_hashes)}")
    return 0


def _classify_page(r) -> str:
    # Hub/collection only when body text is small AND outgoing links are many (index-page shape).
    if r.rendered_text_len < COLLECTION_TEXT_MAX and r.writeup_link_candidates >= COLLECTION_LINK_MIN:
        return "collection_or_navigation"
    if r.rendered_text_len < SUBSTANTIVE_TEXT_MIN:
        return "thin_or_empty"
    return "individual_writeup"


def _write_report(generated_at, urls, successes, failures, duplicate_hashes, event_counts, kind_counts) -> None:
    lines = [
        "# Jia Jie Redbud Fetch Report", "", f"Generated: {generated_at}", "",
        "Fetch-only continuation of the approved discovery experiment. Rendered ONLY the 22 URLs "
        "derived from `jiaje_js_discovered_links.json` using the existing isolated Playwright JS "
        "source. No crawling, no link following, no ingestion, no KnowledgeRecords, no solver.",
        "",
        f"- URLs requested: {len(urls)}",
        f"- URLs succeeded: {len(successes)}",
        f"- URLs failed: {len(failures)}",
        f"- Duplicate content hashes: {len(duplicate_hashes)}",
        f"- Event distribution: {dict(event_counts)}",
        f"- Page-kind distribution: {dict(kind_counts)}",
        "",
        "## Are the 22 URLs individual writeups or navigation/collection pages?",
        "",
    ]
    individual = [r for r in successes if r["page_kind"] == "individual_writeup"]
    collection = [r for r in successes if r["page_kind"] == "collection_or_navigation"]
    thin = [r for r in successes if r["page_kind"] == "thin_or_empty"]
    lines += [
        f"- individual writeups (substantive): {len(individual)}",
        f"- collection/navigation pages: {len(collection)}",
        f"- thin/near-empty pages: {len(thin)}",
        "",
        "## Per-URL results",
        "",
        "| event | challenge | status | text len | outgoing writeup links | kind |",
        "|---|---|---|---|---|---|",
    ]
    for rec in successes:
        lines.append(
            f"| {rec['event']} | {rec['challenge_id']} | {rec['http_status']} | "
            f"{rec['rendered_text_len']} | {rec['outgoing_writeup_link_candidates']} | {rec['page_kind']} |"
        )
    if failures:
        lines += ["", "## Failures (fail-closed, recorded separately)", ""]
        for rec in failures:
            lines.append(f"- {rec['source_url']} — {rec.get('error','')}")
    (DOCS / "jiaje_redbud_fetch_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
