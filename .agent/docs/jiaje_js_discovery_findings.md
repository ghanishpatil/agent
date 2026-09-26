# Jia Jie Redbud JS-Fetch Discovery Findings

Objective: determine what actual CTF challenge/writeup content exists behind the two
JS-rendered Redbud pages. **Discovery / fetch-only.** Nothing was ingested; no KnowledgeRecords
were built; `knowledge/jiaje_v1`, the local store, the frozen solver, the Phase 5 benchmark/
results, and the existing static ingestion behavior were not modified.

## Method and guarantees

- New, isolated module `ctf_ingest/js_source.py` renders a headless browser (Playwright
  Chromium). Playwright is imported lazily, so it does not affect the static pipeline.
- Fetched **only** the two explicitly-discovered URLs. No crawling, no link following.
- **Fail-closed**: if the renderer were unavailable or a page failed to render, the result is
  recorded as an error with no content — never invented. (Both pages rendered successfully.)
- Rendered HTML + visible text saved as **source artifacts**; no extraction into knowledge.
- Renderer/version recorded: Playwright 1.61.0, Chromium 149.0.7827.55.

## Static vs JS accessibility

| page | static extracted text | static raw HTML | JS rendered text | JS rendered HTML | writeup-link candidates (JS) |
|---|---|---|---|---|---|
| puppeteer/index.html | 43 chars (title only) | 23,243 bytes | 860 chars | 36,763 bytes | 15 |
| summer2026/index.html | 45 chars (title only) | 19,634 bytes | 366 chars | 33,171 bytes | 11 |

Note: the server *did* return ~20 KB of HTML statically, but the static **text fetcher** used
for the earlier ingestion extracted only the page title (43–45 chars). The JS render exposes
the actual content and, crucially, the in-page navigation to individual writeups. So the earlier
gap was a limitation of the static text-extraction path, not an access restriction.

Robots/access: no `robots.txt` (HTTP 404) at site or book root; HTTP 200 for both pages; no
restriction encountered or bypassed.

## What is actually behind the two pages

Both pages are **navigation hubs** that link to individual challenge writeups which are **not
listed in the `ctf-writeups` sitemap** (the sitemap has only 5 entries). The JS render exposed
these per-challenge pages as links (recorded as DISCOVERED, **not fetched**):

### Redbud Puppeteer — 13 individual writeups (weekly CTF)
- week0: `easy-random-1.html`, `easy-random-2.html`, `the-old-gods-are-whispering.html`
- week1: `easy-pyjail-1.html`, `easy-random-3.html`, `easy-re-1.html`, `rosetta-3.html`, `rsa-all-in-one.html`
- week2: `easy-random-4.html`, `ecdsa-nonce-reuse.html`
- week3: `easy-random-5.html`, `rsa-partial-factorization.html`
- week4: `easy-random-6.html`

(Topics span PRNG attacks, pyjail, reversing, classical encodings, and RSA/ECDSA — descriptions
are in Chinese on the source pages.)

### Redbud Summer 2026 — 8 individual pwn writeups
- `ret2shellcode.html`, `ret2shellcode-orw.html`, `baby_rop.html`, `babysyscall.html`,
  `jarvisoj_x64.html`, `stack_pivot.html`, `setcontext.html`, `paragraph.html`

### Cross-event link discovered (not under the two pages' own dirs)
- `2025-09-27-sunshine-ctf-2025/jupiter.html` — linked from the Summer 2026 page, revealing a
  **further event directory** (`sunshine-ctf-2025`) in the book that is also absent from the
  sitemap and top nav. Recorded as discovered, not fetched, not explored.

**Total newly-discovered individual writeup pages: 22** (13 + 8 + 1), plus the two already-known
`misc/` reference pages (`solution.html`, `pyjail.html`) which also appear as in-content links.

## Answer to the objective

The two Redbud pages are **hubs, not stubs**. Behind them lie **at least ~21–22 individual CTF
challenge writeups** (13 Puppeteer + 8 Summer 2026, plus a link into a third event,
`sunshine-ctf-2025`) — real pages that the static text fetcher never surfaced and that are not
in the `ctf-writeups` sitemap. The earlier four-page ingestion therefore captured **0 of these
per-challenge writeups**; it stored only the hub titles.

This confirms the source-discovery audit's suspicion with concrete evidence: `jiaje_v1`
under-represents Jia Jie's Redbud writeup corpus by roughly 20+ individual challenge writeups,
and those writeups are reachable only through JS-rendered navigation.

## Discovered-but-not-fetched policy

Every per-challenge URL above is recorded in `docs/jiaje_js_discovered_links.json` with
`fetched: false`. This run did not fetch, render, or ingest any of them. Obtaining their content
would be a separate, explicitly-approved fetch of that enumerated list (still under the same
respectful, fail-closed, provenance-recording discipline), followed by a separate ingestion
decision — none of which was performed here.

## Artifacts

- rendered source: `knowledge/_jiaje_js_cache/ctf-writeups_puppeteer_index.rendered.{html,txt}`,
  `..._summer2026_index.rendered.{html,txt}`
- JS fetch report: `docs/jiaje_js_fetch_report.md`
- discovered-link inventory: `docs/jiaje_js_discovered_links.json`
- provenance/integrity manifest: `docs/jiaje_js_provenance_manifest.json`
- static-vs-JS accessibility comparison: `docs/jiaje_js_accessibility_comparison.json`
- code: `ctf_ingest/js_source.py`; runner `scripts/run_jiaje_js_fetch.py`
- tests: `tests/ingestion/test_js_source.py`

## Limitations

- Only the two hub pages were rendered; the 22 individual writeup pages were enumerated but not
  rendered (per fetch-only scope).
- The `sunshine-ctf-2025` event directory is known only via one inbound link; its full page list
  is not enumerated (would require rendering that hub, out of scope here).
