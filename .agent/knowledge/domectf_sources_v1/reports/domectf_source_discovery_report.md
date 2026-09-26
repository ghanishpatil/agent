# DomeCTF Historical Source Discovery & Verification Report

Generated: 2026-09-25T07:32:46.487244+00:00

## Methodology

- Source of truth: the uploaded reference document `DomeCTF_CTF_Writeups_Reference_Links (1).docx`. Every reference below is parsed directly from that document (year sections + hyperlink anchor text). Challenge names and authors are taken verbatim from anchor text — never inferred from URLs.
- Verification: respectful static HTTP (stdlib urllib, descriptive User-Agent, timeouts, a polite inter-request delay). Only the explicitly referenced URLs were fetched, plus the same-host `*-writeup.html` links directly listed on explicitly referenced index/official pages (kept as DISCOVERED, provenance distinct).
- No JS rendering: pages needing JavaScript are flagged `render_required=true` and reported separately; a renderer was not invoked.
- No knowledge extraction: no technique/knowledge/trajectory/retrieval/solver artifacts were created. Raw pages are cached immutably under `knowledge/domectf_sources_v1/raw/`.

## Coverage by year

| year | event | refs listed | accessible | individual | index | official | render-req |
|---|---|---|---|---|---|---|---|
| 2019 | c0c0n XII | 6 | 4 | 4 | 0 | 0 | 0 |
| 2020 | c0c0n XIII | 22 | 21 | 19 | 2 | 0 | 0 |
| 2021 | c0c0n XIV | 9 | 1 | 0 | 1 | 0 | 0 |
| 2022 | c0c0n XV | 1 | 1 | 0 | 0 | 1 | 0 |
| 2023 | c0c0n XVI | 1 | 1 | 0 | 0 | 1 | 0 |
| 2024 |  | 0 | 0 | 0 | 0 | 0 | 0 |
| 2025 | DomeCTF 2025 | 1 | 1 | 0 | 0 | 1 | 0 |

### Years explicitly marked in the document as NOT having a verified complete challenge-by-challenge public archive

- **2022** — Note: I did not find a verified public, complete challenge-by-challenge writeup archive for 2022.
- **2023** — Note: I did not find a verified public, complete challenge-by-challenge writeup archive for 2023.
- **2024** — No verified public, complete DomeCTF challenge-by-challenge writeup archive was identified in the earlier search.
- **2025** — Note: I did not find a verified public, complete challenge-by-challenge writeup archive for 2025.

## Totals

- Total explicit references: 40
- Total accessible: 29
- Total individual challenge writeups (evidence-classified): 23
- Total index/recap pages: 3
- Total official event pages: 3
- Total inaccessible/dead (NOT_FOUND/NETWORK/OTHER): 9
- Total access-blocked: 1
- Total render-required (JS): 0
- Total ambiguous classifications: 0

Accessibility distribution: {'REDIRECTED': 1, 'ACCESSIBLE': 29, 'ACCESS_BLOCKED': 1, 'NOT_FOUND': 9}

Content classification distribution: {'A_INDIVIDUAL_WRITEUP': 23, 'B_MULTI_CHALLENGE_INDEX': 3, 'C_OFFICIAL_EVENT_PAGE': 3}

## Discovered sources (from explicit index/official pages)

- Total discovered same-host writeup links: 29
- Already in explicit references: 19
- New (not in document): 10
- Fetched for accessibility (bounded): 10

Several of the document's 2021 (`/blog/domectf2021/*`) writeup URLs are dead (they redirect to the site 404 page). The live challenge writeups were recovered as DISCOVERED links from the explicitly referenced 2021 index page, at their canonical `/blog/domectf2020/*` paths. New discovered sources and their evidence-based classification:

| discovered URL | accessibility | classification |
|---|---|---|
| https://beaglesecurity.com/blog/domectf2020/leaked-list-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/the-spy-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/lockbox-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/murder-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/farness-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/jot-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/iss-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/rocket-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |
| https://beaglesecurity.com/blog/domectf2020/domectf2020/seo-writeup.html | NOT_FOUND | None |
| https://beaglesecurity.com/blog/domectf2020/seo-writeup.html | ACCESSIBLE | A_INDIVIDUAL_WRITEUP |

## Duplicates

- Duplicate URLs: 0
- Duplicate canonical URLs: 0
- Duplicate content hashes: 1
- Redirects observed: 12

## Render-required / JS sources

- None: all accessible pages served meaningful static HTML.

## Limitations

- Classification is evidence-based from statically retrieved HTML; pages that block non-browser clients or require JS are reported as ACCESS_BLOCKED / RENDER_REQUIRED rather than classified, and their existence is left `unverified` (not treated as non-existent).
- Discovered-link scope is intentionally narrow (same-host `*-writeup.html` on explicit index pages) to avoid becoming a crawler; other in-page links were not inventoried.
- The document itself marks 2022–2025 as lacking a verified complete public writeup archive; this inventory preserves that and does not attempt an unrestricted search for missing archives.

## Recommended next step

Ready-for-extraction set (NEXT phase — challenge-level raw-source extraction/ingestion into an isolated namespace, NOT started here):
- 2019: the 3 GitHub writeups (accessible) and the Rahul R walkthrough; the Medium writeup is ACCESS_BLOCKED to non-browser clients (exists; needs a browser/again later).
- 2020 (c0c0n XIII): the 19 accessible Beagle Security individual writeups.
- 2021 (c0c0n XIV): the 8 challenge writeups are usable via their DISCOVERED canonical `/blog/domectf2020/*` URLs (the document's `/blog/domectf2021/*` URLs are dead).
- 2022/2023/2024/2025: official event pages only; the document confirms no verified complete public writeup archive, so there is no challenge-by-challenge set to extract for those years.

Raw source is cached immutably; no extraction, retrieval, solver, or benchmark work was done.