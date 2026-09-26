# Jia Jie Source Discovery Audit (read-only)

Purpose: determine whether the previous four-page ingestion (`knowledge/jiaje_v1`) actually
covered Jiajie Chen's (@jiegec) relevant public CTF writeup corpus, or only a subset/index.

Scope discipline: only pages reachable through the site's own index structures (sitemaps,
category index) were inspected. No search engines, no GitHub, no third-party mirrors, no
arbitrary crawling. Nothing was ingested. `knowledge/jiaje_v1`, the local store, the frozen
solver, and existing results were not modified. No URLs were invented — every URL below has
explicit discovery provenance.

Audit date: 2026-09-25 (UTC). Fetcher: the out-of-band static HTTP fetcher (no JavaScript
execution), the same accessibility class as the pipeline's `CachedHttpSource`.

## Discovery method (how each URL was found)

| # | URL | how discovered (provenance) |
|---|---|---|
| S0 | https://jia.je/ctf-writeups/index.html | given by task |
| S1 | https://jia.je/ctf-writeups/sitemap.xml | standard sitemap convention at the book root; confirmed to exist |
| S2 | https://jia.je/sitemap.xml | standard sitemap convention at the site root; confirmed to exist |
| S3 | https://jia.je/ctf-writeups/search/search_index.json | probed by MkDocs convention → HTTP 404 (absent) |
| S4 | https://jia.je/robots.txt | standard convention → HTTP 404 (checked in prior task) |
| S5 | https://jia.je/ctf-writeups/robots.txt | standard convention → HTTP 404 (absent) |

All content URLs below were discovered **only** from S1 (book sitemap) or S2 (site sitemap).

## The CTF book sitemap (S1) — authoritative page list for the book

`https://jia.je/ctf-writeups/sitemap.xml` (559 bytes) lists exactly **5** URLs:

| URL | represents | prior ingest |
|---|---|---|
| /ctf-writeups/index.html | book landing/navigation page | fetched (nav only) |
| /ctf-writeups/misc/solution.html | "Writeups by Solution" — a technique taxonomy/index | ingested |
| /ctf-writeups/misc/pyjail.html | pyjail technique collection (per-CTF snippets) | ingested |
| /ctf-writeups/puppeteer/index.html | "Redbud Puppeteer" event page | ingested (title only) |
| /ctf-writeups/summer2026/index.html | "Redbud Summer 2026" event page | ingested (title only) |

There are **no child/nested writeup URLs** under `puppeteer/` or `summer2026/` in the sitemap.
The book sitemap is a Zensical-generated, build-time artifact and is treated as the
authoritative enumeration of the book's pages.

## The main site sitemap (S2) — CTF footprint on the blog

`https://jia.je/sitemap.xml` (70,833 bytes, 532 `<loc>` entries; the personal blog, a separate
deploy from the book). CTF-relevant entries found by searching the sitemap:

| URL | represents | how discovered |
|---|---|---|
| https://jia.je/ctf/2018/10/04/2018-10-04-thuctf-2018-and-teaser-dragon-ctf-2018/ | one blog post tagged `ctf` | S2 |
| https://jia.je/category/ctf/ | the `ctf` category index | S2 |
| https://jia.je/series/ | series index (no CTF series present) | S2 |
| https://jia.je/crypto/2020/05/21/ecc-curves/ · /crypto/2023/07/14/ecdsa/ · /crypto/2023/07/23/montgomery-mul-mod/ | crypto **concept tutorials**, not CTF writeups | S2 |

The blog sitemap contains **exactly one** `/ctf/` post and **zero** `ctf-writeups` URLs (the
book is a separate deploy with its own sitemap). `/category/ctf/` (fetched) lists exactly that
one 2018 post.

## FETCHED / PARSED / NOT ACCESSIBLE (this audit)

| URL | DISCOVERED | FETCHED | PARSED (usable content) | classification |
|---|---|---|---|---|
| ctf-writeups/sitemap.xml | S1 conv. | yes (559 B) | yes (5 URLs) | index |
| sitemap.xml | S2 conv. | yes (70 KB) | yes (532 URLs) | index |
| misc/solution.html | S1 | yes | yes — technique taxonomy | **technique-book page** |
| misc/pyjail.html | S1 | yes | yes — pyjail collection (~35 challenge snippets) | **technique-book page** |
| puppeteer/index.html | S1 | yes (146 B) | **no — title only** | **NOT ACCESSIBLE (JS-rendered)** |
| summer2026/index.html | S1 | yes (148 B) | **no — title only** | **NOT ACCESSIBLE (JS-rendered)** |
| ctf-writeups/index.html | S0 | yes (134 B) | no — nav only | NOT ACCESSIBLE (JS-rendered nav) |
| /ctf/2018/.../thuctf-2018... | S2 | yes (770 B) | yes — but non-technical reflection | blog musing (not a technical writeup) |
| /category/ctf/ | S2 | yes (570 B) | yes — lists 1 post | index |
| search_index.json | S3 conv. | HTTP 404 | — | absent |
| robots.txt (site) | S4 conv. | HTTP 404 | — | absent (no restriction) |
| robots.txt (book) | S5 conv. | HTTP 404 | — | absent (no restriction) |

## Robots / access restrictions

No `robots.txt` at the site root or the book root (both HTTP 404) → **no crawl restrictions
encountered**. No access controls, auth walls, or rate blocks were hit. No restriction was
bypassed. The only "inaccessible" content is due to **client-side (JavaScript) rendering**, not
access policy.

## Are the four ingested pages the complete corpus?

**Classification of the four ingested pages: a TECHNIQUE-BOOK subset plus two JS-inaccessible
event stubs — NOT a complete per-challenge writeup corpus.**

- They **are** the complete set of *content URLs* the book's own sitemap exposes (there are no
  additional book pages we missed at the URL level; the sitemap has exactly these 5 entries and
  we ingested the 4 non-index ones). So at the **URL-enumeration** level, nothing in the book's
  sitemap was skipped.
- But by **content type**, two of the four (`solution.html`, `pyjail.html`) are
  **technique-index / technique-book pages** — a taxonomy of techniques and a pyjail collection
  — not individual event writeups. They aggregate references to dozens of challenges as inline
  snippets, each with a "Details here" link whose target is **not** exposed by the site's own
  sitemap (so those detailed targets are either JS-nav-only or external, and were not, and could
  not be, enumerated within scope).
- The other two (`puppeteer`, `summer2026`) are **event pages whose actual writeup content is
  JS-rendered** and was therefore captured as **title-only** in `jiaje_v1`. Their substantive
  content is effectively **missing** from the store.
- The single blog `/ctf/` post (2018 THUCTF) is a **personal reflection in Chinese with no
  technical solutions** (it explicitly defers to others' writeups); it was not ingested and is
  low value as a technical writeup.

## Estimated / confirmed number of individual challenges/writeups

- **Confirmed CTF-related pages on jia.je (site's own sitemaps):** 4 book content pages + 1 blog
  post = **5** pages total.
- **Individual challenge writeups as separate ingestible pages:** **0 confirmed** beyond the
  aggregation pages. The book sitemap exposes no per-challenge URLs.
- **Challenges referenced as inline snippets** (not separate pages): `pyjail.html` alone
  references ~**35** named challenges (jailCTF 2024–2026, SECCON 13/14, LACTF 2025, ImaginaryCTF,
  TCP1P, Dice, Sekai, HITCON, etc.); `solution.html` references dozens more techniques. These are
  **inside** the two technique pages already ingested, not separate documents.
- **Event challenge counts for Redbud Puppeteer / Redbud Summer 2026:** **UNKNOWN via static
  fetch** — the content is JS-rendered and returned zero challenge text. Cannot be counted without
  a JavaScript-capable fetch, and no per-challenge URLs are exposed by the sitemap.

## URLs that would need ingestion to obtain the actual writeup content

Within the site's own structures, to improve coverage one would need the **rendered** content of:

1. https://jia.je/ctf-writeups/puppeteer/index.html — event writeups (JS-rendered)
2. https://jia.je/ctf-writeups/summer2026/index.html — event writeups (JS-rendered)
3. https://jia.je/ctf-writeups/index.html — the book navigation (JS-rendered), to confirm whether
   the nav exposes any per-challenge pages beyond the sitemap (the sitemap says it does not)

Optionally (low value, statically fetchable): the 2018 `/ctf/` blog post.

None of these can be obtained by inventing URLs; items 1–3 require executing the page JavaScript
to reveal content (and potentially additional nav links).

## Can the existing respectful CachedHttpSource fetch these?

**No — not the JS content.** `CachedHttpSource` reads previously-fetched static text and executes
no JavaScript; the out-of-band static fetcher used for caching also executes no JavaScript.
Therefore the Redbud event content and the book nav are **not obtainable** through the current
respectful static path. Static pages (e.g., the 2018 blog post) **are** fetchable. Capturing the
JS-rendered content would require a JavaScript-capable fetcher (e.g., a headless browser) — a
new capability, out of scope here — used with the same respectful, provenance-recording
discipline.

## Answer to the audit question

> "Did our previous four-page ingestion actually cover Jia Jie Chen's relevant public CTF
> writeup corpus?"

**Partially, and mostly as an index/technique-book — not as a per-challenge writeup corpus.**

- At the **URL level**, the ingestion covered **all four content URLs the book's sitemap
  exposes** (nothing enumerable was skipped), plus it correctly did not fabricate URLs.
- At the **content level**, coverage is **incomplete**: two of the four pages are
  technique-index/technique-book pages (valuable for technique breadth, which the earlier
  corpus comparison already showed), and the two Redbud **event writeup pages were captured as
  title-only because their content is JavaScript-rendered** and inaccessible to the static
  fetcher. The substantive per-challenge Redbud writeup content is therefore **not represented**
  in `jiaje_v1`.
- One additional CTF-tagged blog post exists (2018 THUCTF) and was not ingested; it is a
  non-technical reflection and is not material to a technique/writeup corpus.

**Conclusion:** `jiaje_v1` should be regarded as a **technique-book/index subset** of Jia Jie's
public CTF material, **not** a complete per-challenge writeup corpus. The gap is caused by
client-side rendering of the event pages, not by missed URLs or access restrictions. Closing it
requires a JavaScript-capable fetch of the two Redbud event pages (and the book nav to confirm
no further pages), performed under the same respectful, provenance-recording discipline. No such
fetch or ingestion was performed in this audit.
