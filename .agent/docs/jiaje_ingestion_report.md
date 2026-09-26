# Jia Jie External CTF Knowledge Ingestion — Report

First external-knowledge ingestion experiment. Source: **Jiajie Chen (@jiegec)**,
<https://jia.je/ctf-writeups/index.html>. All work extends the existing `ctf_ingest`
pipeline; nothing in `ctf_agent`, the Phase 5 benchmark/results, or prior
retrieval/knowledge experiment result artifacts was modified.

## Access and scope

- `https://jia.je/robots.txt` returned HTTP 404 → no crawl restriction. No access controls
  were bypassed.
- The CTF book's own sitemap (`/ctf-writeups/sitemap.xml`) enumerated exactly four content
  pages plus the index. Only those were fetched; nothing beyond the Jia Jie source was
  scraped. No directly-referenced external writeup required resolution.
- Retrieval was an explicit, recorded out-of-band step; the pipeline itself performs no
  network I/O. Fetched text is cached under `knowledge/_jiaje_cache/` with a provenance
  manifest (URL, retrieval timestamp, sha256, author).

## Pipeline extension (no second architecture)

Added one source, `ctf_ingest.sources.CachedHttpSource`, which emits `HTTP`-provenance
`RawDocument`s (source URL, retrieved_at, content sha256, author/license, static-content
flag) from the cache. Everything else reuses the existing normalize → extract → dedup →
`KnowledgeStore` pipeline unchanged.

## Separate versioned store

Jia Jie was ingested into `knowledge/jiaje_v1/` (records.jsonl + manifest.json). It is
**not** mixed into the local store; the local store is byte-identical to before.

## Ingestion result

- 4 documents fetched, 4 records written, 4 unique, 0 intra-run duplicates.
- Two pages carry rich static content: `misc/solution.html` (a technique-by-solution
  taxonomy spanning AI/Crypto/Forensics/Misc/Pwn/Reverse/Web) and `misc/pyjail.html` (a
  detailed pyjail technique collection with per-CTF requirements).
- Two pages (`puppeteer/index.html`, `summer2026/index.html`) are JS-rendered event
  landing pages that yielded no static prose. They are recorded with full provenance and
  flagged `has_static_content=false` — no content was invented for them.

## Provenance

Provenance completeness is **1.0** for the Jia Jie corpus (every record carries source URL,
retrieval timestamp, content sha256, document path, and author) versus **0.8** for the local
corpus (which lacks source URLs). See `jiaje_integrity_manifest.json`.

## Duplicate detection vs the local corpus

Exact + near-duplicate (token-Jaccard ≥ 0.9) detection against all 32 local records found
**0 duplicates** (`jiaje_duplicate_report.json`). Note: the local corpus contains a
`_reference/jiegec-technique-index.md` derived from the same author, but its phrasing differs
enough that it did not cross the near-duplicate threshold. Provenance was preserved for every
record regardless (nothing discarded).

## Extraction quality (explicit / inferred / missing — nothing invented)

`jiaje_extraction_quality.json`. Per-field verdicts across the 4 records:

| field | explicit | inferred | missing |
|---|---|---|---|
| event/challenge metadata | 4 | 0 | 0 |
| challenge description/context | 4 | 0 | 0 |
| category | 2 | 0 | 2 |
| techniques/mechanisms | 2 | 0 | 2 |
| observed clues | 0 | 0 | 4 |
| hypotheses | 0 | 0 | 4 |
| discriminating tests | 0 | 0 | 4 |
| observations | 0 | 0 | 4 |
| interpretations | 0 | 0 | 4 |
| hypothesis updates | 0 | 0 | 4 |
| next actions | 1 | 0 | 3 |
| exploit/solution | 1 | 0 | 3 |
| verification | 0 | 0 | 4 |
| failures/corrections | 0 | 0 | 4 |

Honest characterization: Jia Jie's CTF pages are **technique catalogs**, not step-by-step
solve narratives. Technique/metadata extraction is strong; the reasoning-trajectory stages
(clues → hypothesis → discriminating test → observation → interpretation → update →
verification) are largely **absent in the source** and are therefore marked missing, never
fabricated.

## Retrieval quality on the new corpus

Labeled evaluation (`jiaje_retrieval_quality.json`), k=3: precision@3 = 0.50,
recall@3 = 1.00, MRR = 1.00. Both labeled queries retrieved their gold document at rank 1;
precision is capped by the tiny gold sets (1 relevant doc each).

## Corpus comparison (local vs Jia Jie)

`jiaje_corpus_comparison.json`.

| dimension | local | Jia Jie |
|---|---|---|
| documents | 32 | 4 |
| unique challenges | 32 | 4 |
| distinct techniques | 20 | 17 |
| techniques unique to Jia Jie | — | 0 (all 17 shared with local) |
| mean trajectory completeness | 0.284 | 0.068 |
| failure/correction coverage | 0.19 | 0.00 |
| provenance completeness | 0.80 | 1.00 |
| cross-corpus duplicate rate | — | 0.00 |

Jia Jie adds **breadth of technique references with perfect provenance**, but **not
reasoning-trajectory depth or failure/correction data** (its format doesn't contain those),
and it introduces **no techniques the local corpus lacks** in this small slice.

## Controlled 3-config knowledge-dependent evaluation

`jiaje_three_config_results.json`. The frozen solver + frozen v2 harness were run with three
knowledge sources, varying only the retriever. Restricted to the two cases with well-defined
semantics under a global corpus retriever: the easy/fast baseline and the knowledge-dependent
SSTI case. (The adversarial per-case cases remain validated in the immutable v2 experiment.)

| config | knowledge-dependent | easy case retrievals | KAVS | safety |
|---|---|---|---|---|
| local | BLOCKED | 0 | 0 | preserved |
| jiaje | **SOLVED** | 0 | **1** | preserved |
| local + jiaje | BLOCKED | 0 | 0 | preserved |

Findings:
- **Jia Jie supplies actionable knowledge.** Its consolidated taxonomy surfaces the SSTI
  mechanism; the solver retrieved it, formed the `web-ssti` candidate hypothesis (alongside a
  `web-sqli` candidate that evidence then ruled out), ran the discriminating test, obtained
  supporting evidence, and reached an independently kernel-verified solve — a solve the
  baseline cannot reach. This is a genuine, correctly-attributed, knowledge-attributable
  verified solve.
- **The local corpus did not surface SSTI** for the underspecified query: its SSTI knowledge
  is buried in individual web writeups that did not rank in the top-k, so the case stayed
  BLOCKED.
- **Naive combination introduced retrieval noise.** With local + Jia Jie, the many local web
  records outranked the single misc-categorized Jia Jie taxonomy doc, crowding it out, and the
  case stayed BLOCKED. This is a concrete caution: merging corpora without ranking/routing
  improvements can *lose* a useful signal.
- **Easy challenges stayed fast** in every config: 0 retrievals, no escalation.
- **All safety invariants preserved** in every config: no false verification, no false
  disproof, no blind guessing, no budget violations, no executed duplicate actions, stopping
  correct.

## Efficiency (treatment arm, knowledge-dependent case, jiaje config)

retrieval calls = 1 · retrieved records = 3 · knowledge-derived hypotheses = 2 · actions = 4 ·
unnecessary retrievals = 0 · time-to-first-action and time-to-verified in the tens of ms
(deterministic counts are the reliable figures; wall-clock varies per run). Easy case: 0
retrievals, 0 knowledge hypotheses.

## Verdict on the objective

Jia Jie's writeups **do add useful, correctly-attributed, actionable CTF knowledge** — its
technique taxonomy supplied a mechanism that produced a safe, kernel-verified solve the
baseline could not reach — **without slowing easy challenges and without any safety
violation**. The value is **technique breadth with excellent provenance**, not
reasoning-trajectory or failure/correction depth (absent in the source). The main risk
surfaced is **retrieval noise when corpora are merged naively**, which crowded out the useful
Jia Jie signal; this argues for category-aware routing / ranking before connecting a combined
corpus to the solver. Per the plan, the full corpus is **not** connected to the solver beyond
this controlled evaluation.

## Artifacts

- `docs/jiaje_ingestion_statistics.json`
- `docs/jiaje_integrity_manifest.json`
- `docs/jiaje_duplicate_report.json`
- `docs/jiaje_extraction_quality.json`
- `docs/jiaje_retrieval_quality.json`
- `docs/jiaje_corpus_comparison.json`
- `docs/jiaje_three_config_results.json`
- store: `knowledge/jiaje_v1/`; cache + provenance manifest: `knowledge/_jiaje_cache/`
- code: `ctf_ingest/sources.py::CachedHttpSource`, `ctf_experiment/corpus_analysis.py`,
  `scripts/run_jiaje_ingestion.py`
- tests: `tests/ingestion/test_cached_http_source.py`,
  `tests/experiment/test_corpus_analysis.py`, `tests/experiment/test_jiaje_ingestion.py`

## Limitations

- Static fetch cannot render the two JS-only event pages; their writeups (if any) are not
  captured. Recorded honestly as empty-content with provenance.
- The web technique→discriminating-test mapping used by the solver integration covers SSTI and
  SQLi; other retrieved techniques are catalogued but not yet actionable in the solver.
- The corpus is a small slice of one author's site; conclusions are about the ingestion/
  retrieval mechanics and this controlled benchmark, not general CTF-solving ability.
