# AGENT_ARCHITECTURE

The **actual** architecture as implemented in this repository. Every component is labeled:

- **IMPLEMENTED** — code exists and is exercised by the test suite.
- **FROZEN** — implemented AND fingerprint-locked; must not change without explicit authorization.
- **EXPERIMENTAL** — implemented and additive, outside the frozen solver; used for ingestion/evaluation only.
- **PLANNED** — described/intended, NOT yet implemented.

Planned architecture is never described as implemented.

---

## 1. Frozen solver core — `.agent/src/ctf_agent/` (FROZEN, 45 .py files)

Mandated pipeline, preserved end to end, no component bypasses it:

```
Action -> Observation -> Result Classification -> Evidence (+provenance)
      -> Hypothesis Impact -> State Update -> Verification / Continue / STOP
```

| Component | File | Status |
|---|---|---|
| Typed state models + enums | `models.py` | FROZEN |
| Result classifier (`ExecutionResult`→`ResultClassification`) | `classifier.py` | FROZEN |
| Conservative hypothesis impact | `impact.py` | FROZEN |
| Evidence ledger (provenance; current > historical) | `evidence.py` | FROZEN |
| Immutable hypothesis state | `hypothesis.py` | FROZEN |
| Hypothesis engine / board | `hypothesis_engine.py` | FROZEN |
| Failure memory (advisory priors, append-only) | `failure_memory.py` | FROZEN |
| Verification (trusted-tool proofs, STOP-on-verified, anti-spray) | `verification.py` | FROZEN |
| Action deduplication (semantic fingerprint + state digest) | `deduplication.py` | FROZEN |
| Trust Kernel (atomic transition; no executor/planner inside) | `kernel.py` | FROZEN |
| Regression replay of 12 Phase-1 failures | `regression.py` | FROZEN |
| Reasoning loop | `loop.py` | FROZEN |
| Action planner | `planner.py` | FROZEN |
| Advisory memory retrieval | `memory_retrieval.py` | FROZEN |
| Context model | `context.py` | FROZEN |
| Proposals / metrics / journal / LLM boundary | `proposals.py`, `metrics.py`, `journal.py`, `llm_boundary.py` | FROZEN |
| Adapters (file/http/subprocess + base) | `adapters/` | FROZEN |
| Autonomy layer (solver, control, understanding, resources, reasoning, evaluation, baseline, contracts) | `autonomy/` | FROZEN |
| Specialists: web, crypto, pwn, reverse, forensics (+ base/brain/registry/selection/metrics) | `specialists/` | FROZEN |

Trust properties (FROZEN): LLM output cannot directly mutate trusted state; only an authoritative
discriminating contradiction yields `DISPROVES`; only a verification gate yields a verified flag.

## 2. Frozen benchmark — `.agent/src/ctf_bench/` (FROZEN)

- `phase5_benchmark.py` — the single source of truth for the Phase 5 evaluation cases
  (KNOWN / NOVEL / ADVERSARIAL / HELD_OUT). Consumed by both the harness and the tests.
- Results/baseline artifacts: `.agent/docs/phase5_results.json`, `docs/phase5_baseline.json`,
  freeze manifest `docs/phase5_freeze.md`. FROZEN.

## 3. Ingestion pipeline — `.agent/src/ctf_ingest/` (EXPERIMENTAL, additive)

`ctf_agent` must not import this package.

| Module | Role | Status |
|---|---|---|
| `models.py` | `KnowledgeRecord`, `Technique`, 11-stage `ReasoningTrajectory`, `FailureCorrection`, `Provenance` | IMPLEMENTED |
| `sources.py` | Local dir / HTTP / cached-HTTP sources (explicit fetcher, no silent scraping) | IMPLEMENTED |
| `js_source.py` | Playwright JS renderer (fail-closed) for JS-only pages | IMPLEMENTED |
| `normalize.py`, `parser.py` | HTML/markdown → title/sections/body | IMPLEMENTED |
| `extract.py` | Generic technique table + flag/category/metadata extraction | IMPLEMENTED |
| `redbud_extract.py` | Jia Jie Redbud challenge-level extraction (heading→stage, E/I/M provenance) | IMPLEMENTED |
| `domectf_discovery.py` | DomeCTF source discovery/verification/classification | IMPLEMENTED |
| `domectf_extract.py` | DomeCTF challenge-level extraction (mirrors `redbud_extract.py`) | IMPLEMENTED |
| `dedup.py` | Exact + near-duplicate detection (provenance preserved, never merges distinct challenges) | IMPLEMENTED |
| `store.py` | `KnowledgeStore` (records.jsonl + manifest); `records_from_store` | IMPLEMENTED |
| `retrieval.py` | `KnowledgeRetriever` / `RetrievalQuery` | IMPLEMENTED |
| `advisory_projection.py` | Project retrieved knowledge as advisory memory refs | IMPLEMENTED |
| `pipeline.py` | Ingestion orchestration | IMPLEMENTED |

## 4. Evaluation harnesses — `.agent/src/ctf_experiment/` (EXPERIMENTAL, additive)

| Module | Role | Status |
|---|---|---|
| `knowledge_solver.py` | `solve_with_knowledge`: frozen solver composition + ONE substitution (augmented reasoning source); `retriever=None` reproduces frozen behavior | IMPLEMENTED |
| `knowledge_reasoning.py` | `KnowledgeAugmentedReasoningSource`: retrieved knowledge → typed candidate hypotheses only; budgeted escalation; `_WEB_TESTS` bridge | IMPLEMENTED |
| `knowledge_dependent_benchmark_v2.py` / `knowledge_dependent_harness_v2.py` | Control/treatment A/B with strict knowledge-attribution + safety invariants | IMPLEMENTED |
| `knowledge_dependent_benchmark.py` / `knowledge_dependent_harness.py` | v1 (observability-only baseline) | IMPLEMENTED |
| `ab_harness.py`, `retrieval_eval.py`, `corpus_analysis.py`, `labeled.py` | A/B on Phase 5 benchmark, retrieval quality, corpus stats/dedup | IMPLEMENTED |
| `domectf_eval.py` | DomeCTF retrieval + A/B/C/D evaluation (this track) | IMPLEMENTED |

### Knowledge→action bridge (important, measured constraint)
`KnowledgeAugmentedReasoningSource._WEB_TESTS` maps only the technique_ids **`ssti`** and
**`sql-injection`** to executable discriminating actions, because the only executable evaluation
environment is a web probe. Retrieved knowledge for any other mechanism (pwn/crypto/forensics/osint/
hardware/reverse) can be ranked and proposed but has **no executable environment** in the current
harness, so it cannot produce a knowledge-attributable verified solve. This is a property of the
current integration surface — see `AGENT_STATUS.md` for the DomeCTF evaluation result and caveats.

## 5. Knowledge corpora — `.agent/knowledge/` (EXPERIMENTAL data, generated)

`local_writeups/` (32), `jiaje_v1/` (4), `jiaje_redbud_v1/store/` (22), `domectf_v1/store/` (32),
`domectf_sources_v1/` (source inventory, 40 refs / 49 raw), `domectf_eval_v1/` (evaluation outputs),
plus raw caches `_jiaje_cache/`, `_jiaje_js_cache/`. Provenance-preserving; extraction labels
EXPLICIT / INFERRED / MISSING.

## 6. Integration status (explicit)

- Retrieval is **NOT** wired into the production frozen solver. It is exercised only through
  `solve_with_knowledge` inside the experiment harnesses. (IMPLEMENTED as experiment; not integrated.)
- Advisory memory in the frozen solver is observability-only (v1 result: KNOWLEDGE-SAFE /
  NON-CONTRIBUTING). The knowledge→hypothesis integration that can convert knowledge into a verified
  solve exists only in the EXPERIMENTAL `ctf_experiment` layer.

## 7. PLANNED (not implemented)

- **Real-world CTF solving harness/adapters** for live challenges — PLANNED (this is the stated next
  objective; no live-challenge execution architecture exists yet).
- Executable environments / typed discriminating tests for non-web mechanisms (pwn/crypto/forensics/
  osint/hardware/reverse) that would let non-web retrieved knowledge become attributable — PLANNED.
- Retrieval-dilution mitigation for combined multi-corpus retrieval — PLANNED.
- Any LLM fine-tuning or reinforcement learning — NOT planned / explicitly out of scope.
