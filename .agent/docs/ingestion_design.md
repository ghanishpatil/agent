# External CTF Writeup Ingestion — Design and Experiment Plan

This is the post-Phase-5 knowledge-expansion subsystem. It is **additive and standalone**:
`ctf_agent` does not import `ctf_ingest`, and retrieval is **not** wired into the frozen
solver in this phase. The goal of this stage is to build the ingestion pipeline and a
real knowledge store, so a later, explicitly-approved step can measure whether external
knowledge helps the frozen agent on the frozen benchmark.

## Freeze contract

The solver is frozen per `docs/phase5_freeze.md` (aggregate SHA-256
`ead35256…dfdb88`, 45 files). Nothing in this phase modifies `ctf_agent`, the protected
trees (`.agent_audit`, `.kiro`, `writeups`), or the benchmark. The `writeups/` tree is
used only as read-only ingestion input; its hash is unchanged
(`9015ffb5…221d5`, 32 files).

## Pipeline

```
URL / Git repo / local dir
        │  (sources.py)
        ▼
   Crawler  ──► RawDocument + Provenance
        │  (parser.py + normalize.py)
        ▼
   Parser / Normalization  ──► NormalizedWriteup (headed sections, clean body)
        │  (extract.py)
        ▼
   Extraction
     • challenge metadata   (category, points, difficulty, flag format, flags)
     • techniques           (keyword-scored, with evidence spans)
     • reasoning trajectory (the 11-stage sequence below)
     • failure / correction (dead-ends and the fix that followed)
        │  (dedup.py)
        ▼
   Deduplication  ──► exact (content hash) + near-duplicate (token Jaccard)
        │  (models.py Provenance carried end-to-end)
        ▼
   Provenance
        │  (store.py)
        ▼
   Knowledge Store  ──► records.jsonl + manifest.json (counts + integrity)
```

### Reasoning trajectory (the point of the whole exercise)

Each writeup is mined not just for `challenge → solution → flag` but for the trajectory:

```
challenge context → observed clue → candidate mechanisms → hypothesis →
discriminating test → observation → interpretation → hypothesis update →
next action → exploit/solution → verification
```

`TrajectoryStepKind` enumerates these 11 stages. Extraction is heuristic (heading cues +
sentence cue phrases) and conservative: unrecoverable stages are simply absent, and
`ReasoningTrajectory.completeness` reports the fraction of distinct stages recovered.
Nothing is fabricated — no flag, technique, or step is emitted without supporting text.

## Modules

| module | responsibility |
|---|---|
| `ctf_ingest/models.py` | JSON-serialisable dataclasses + schema version |
| `ctf_ingest/sources.py` | `LocalDirectorySource`, `GitRepositorySource` (clone), `HttpSource` (explicit fetcher) |
| `ctf_ingest/parser.py` | markdown/text/HTML → headed sections + clean body |
| `ctf_ingest/normalize.py` | `RawDocument` → `NormalizedWriteup` |
| `ctf_ingest/extract.py` | metadata / technique / trajectory / failure extraction |
| `ctf_ingest/dedup.py` | exact + near-duplicate detection |
| `ctf_ingest/store.py` | JSONL records + manifest with sha256 integrity |
| `ctf_ingest/pipeline.py` | orchestration + convenience entry points |

Runners: `scripts/ingest_writeups.py` (local corpus).

## No silent scraping

`GitRepositorySource` clones only when iterated and accepts an injectable git runner (so
it is testable offline). `HttpSource` requires an explicit `fetcher` callable — the
subsystem never performs implicit network egress. Ingesting a public collection such as
a Jia Jie mirror is done by cloning the repo (or pointing at a local checkout) and
walking it; no site is scraped without an explicit caller decision.

## Provenance and licensing

Every `RawDocument` and `KnowledgeRecord` carries `Provenance`
(source type, URI, document path, retrieval time, revision, content SHA-256, and a
free-form license note). Attribution and integrity travel with every extracted fact.

## Current knowledge store (local baseline corpus)

Running `scripts/ingest_writeups.py` over the workspace `writeups/` tree produced
`.agent/knowledge/local_writeups/`:

- documents seen: 32 · records written: 32 · unique: 32 · duplicates: 0
- categories: crypto 12, web 7, pwn 4, reverse 3, misc 3, unknown 3
- records with an extracted failure/correction: 6
- average trajectory completeness: 0.284

The modest completeness is expected and honest: real writeups vary widely in structure,
and the heuristic extractor only records stages it can actually find. This is a signal to
improve extraction, not something to inflate.

## The experiment (later, explicitly-approved step)

The comparison isolates one variable — advisory knowledge — against the frozen solver and
frozen benchmark:

```
            SAME frozen benchmark (ctf_bench.build_phase5_cases)
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                             ▼
  Phase 5 agent (baseline)              Phase 5 agent + external knowledge
        │                                             │
        ▼                                             ▼
   docs/phase5_results.json                    augmented results
```

Protocol:
1. Do not modify `ctf_agent`. Expose retrieved knowledge only through the existing
   advisory memory boundary (retrieval stays advisory; current evidence still wins;
   no trust boundary changes).
2. Run the identical `EvaluationHarness` on the identical cases.
3. Compare per-kind solve/verified rates — especially HELD_OUT — plus false-verification
   and false-disproof (which must not increase), duplicate-action rate, and actions/solve.
4. Attribute each solve's knowledge source so we can tell reasoning from recognition.

Decision rule:
- If retrieval alone materially improves held-out verified solves without raising
  false-verification, retrieval is the win and fine-tuning may be unnecessary.
- If retrieval helps little, that is a real (reportable) negative result.

Fine-tuning is only considered after this retrieval-only comparison, and is out of scope
here.

## Limitations

- Extraction is heuristic (keyword/section cues), English-oriented, and tuned for common
  markdown writeup shapes; trajectory completeness on arbitrary corpora is modest.
- Near-duplicate detection uses token Jaccard, not semantic similarity.
- HTML parsing is a lightweight tag strip, not a full DOM parser.
- No retrieval integration and no evaluation of downstream solver impact yet — that is
  the explicitly-separated next step.
