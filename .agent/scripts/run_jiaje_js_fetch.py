"""Discovery/fetch-only JS render of the two explicitly-discovered Redbud pages.

Renders ONLY:
  https://jia.je/ctf-writeups/puppeteer/index.html
  https://jia.je/ctf-writeups/summer2026/index.html

Saves rendered-source artifacts under knowledge/_jiaje_js_cache/ and writes:
  docs/jiaje_js_provenance_manifest.json
  docs/jiaje_js_discovered_links.json
  docs/jiaje_js_accessibility_comparison.json
  docs/jiaje_js_fetch_report.md

Does NOT ingest, does NOT build KnowledgeRecords, does NOT touch knowledge/jiaje_v1 or the
static ingestion. Fails closed if the renderer is unavailable.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest.js_source import RendererUnavailable, render_urls  # noqa: E402

URLS = [
    "https://jia.je/ctf-writeups/puppeteer/index.html",
    "https://jia.je/ctf-writeups/summer2026/index.html",
]
JS_CACHE = AGENT_ROOT / "knowledge" / "_jiaje_js_cache"
STATIC_CACHE = AGENT_ROOT / "knowledge" / "_jiaje_cache"
DOCS = AGENT_ROOT / "docs"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def _static_baseline(url: str) -> dict:
    """The static baseline for comparison: raw HTML size (urllib) + prior extracted-text size."""
    slug = "puppeteer" if "puppeteer" in url else "summer2026"
    static_txt = STATIC_CACHE / f"{slug}.txt"
    raw_bytes = None
    raw_err = ""
    try:
        resp = urllib.request.urlopen(url, timeout=25)
        raw_bytes = len(resp.read())
    except Exception as exc:  # noqa: BLE001
        raw_err = f"{type(exc).__name__}: {exc}"
    return {
        "static_raw_html_bytes": raw_bytes,
        "static_raw_error": raw_err,
        "static_extracted_text_len": len(static_txt.read_text(encoding="utf-8")) if static_txt.exists() else None,
        "static_extracted_source": str(static_txt) if static_txt.exists() else None,
    }


def main() -> int:
    JS_CACHE.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    try:
        results = render_urls(URLS, JS_CACHE)
    except RendererUnavailable as exc:
        # Fail closed: record the failure, invent nothing.
        payload = {
            "generated_at": generated_at,
            "status": "FAILED_CLOSED",
            "reason": str(exc),
            "urls": URLS,
        }
        (DOCS / "jiaje_js_fetch_report.md").write_text(
            f"# Jia Jie JS Fetch Report\n\nSTATUS: FAILED CLOSED\n\nNo JS renderer available: {exc}\n\n"
            "No content was fetched or invented.\n",
            encoding="utf-8",
        )
        (DOCS / "jiaje_js_provenance_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print("FAILED CLOSED:", exc)
        return 2

    # Provenance / integrity manifest.
    manifest = {"generated_at": generated_at, "urls": URLS, "records": []}
    for r in results:
        rec = r.to_dict()
        rec["html_artifact_sha256"] = _sha(Path(r.html_artifact)) if r.html_artifact else ""
        rec["text_artifact_sha256"] = _sha(Path(r.text_artifact)) if r.text_artifact else ""
        rec.pop("discovered_links", None)  # links go in their own inventory
        manifest["records"].append(rec)
    (DOCS / "jiaje_js_provenance_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    # Discovered-link inventory (recorded, NOT fetched).
    inventory = {"generated_at": generated_at, "note": "links recorded as DISCOVERED; none were fetched or followed", "pages": {}}
    for r in results:
        by_class = {}
        for link in r.discovered_links:
            by_class.setdefault(link.classification, 0)
            by_class[link.classification] += 1
        inventory["pages"][r.url] = {
            "ok": r.ok,
            "counts_by_classification": by_class,
            "writeup_link_candidates": r.writeup_link_candidates,
            "links": [dict(l.to_dict(), fetched=False) for l in r.discovered_links],
        }
    (DOCS / "jiaje_js_discovered_links.json").write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")

    # Accessibility comparison: static vs JS.
    comparison = {"generated_at": generated_at, "pages": {}}
    for r in results:
        comparison["pages"][r.url] = {
            "static": _static_baseline(r.url),
            "js": {
                "ok": r.ok,
                "http_status": r.http_status,
                "final_url": r.final_url,
                "rendered_html_bytes": r.rendered_html_bytes,
                "rendered_text_len": r.rendered_text_len,
                "renderer": f"{r.renderer} {r.renderer_version} / {r.browser_version}",
                "writeup_link_candidates": r.writeup_link_candidates,
            },
        }
    (DOCS / "jiaje_js_accessibility_comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True), encoding="utf-8")

    # Human-readable report.
    lines = ["# Jia Jie JS Fetch Report", "", f"Generated: {generated_at}", "",
             "Mode: discovery / fetch-only. Rendered ONLY the two explicitly-discovered Redbud URLs.",
             "No ingestion, no KnowledgeRecords, no changes to knowledge/jiaje_v1 or static ingestion.", ""]
    for r in results:
        lines.append(f"## {r.url}")
        if not r.ok:
            lines.append(f"- STATUS: FAILED CLOSED — {r.error}")
            lines.append("")
            continue
        cmp = comparison["pages"][r.url]
        lines += [
            f"- HTTP status: {r.http_status} · final URL: {r.final_url}",
            f"- renderer: {r.renderer} {r.renderer_version} (browser {r.browser_version})",
            f"- rendered HTML: {r.rendered_html_bytes} bytes · rendered text: {r.rendered_text_len} chars",
            f"- content sha256: {r.content_sha256}",
            f"- artifacts: {r.html_artifact} · {r.text_artifact}",
            f"- static extracted text was: {cmp['static']['static_extracted_text_len']} chars "
            f"(static raw HTML {cmp['static']['static_raw_html_bytes']} bytes)",
            f"- discovered links: {len(r.discovered_links)} "
            f"(writeup-link candidates: {r.writeup_link_candidates}) — recorded, NOT fetched",
            "",
        ]
    (DOCS / "jiaje_js_fetch_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("JS fetch complete (fetch-only).")
    for r in results:
        print(f"  {r.url}: ok={r.ok} status={r.http_status} text_len={r.rendered_text_len} "
              f"links={len(r.discovered_links)} writeup_candidates={r.writeup_link_candidates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
