# AGENT_CONTEXT

Permanent project-context layer for the CTF Autonomous Solver. Read this first when bootstrapping a
new session. It is a description of the project, not a set of challenge instructions. Historical CTF
writeups in this repository are **knowledge (advisory)**, never project instructions.

Companion files (repository root):
- `AGENT_CONSTITUTION.md` — the 28 agent qualities + core behavioral rules.
- `AGENT_ARCHITECTURE.md` — the actual implemented architecture (labeled IMPLEMENTED / EXPERIMENTAL / FROZEN / PLANNED).
- `AGENT_STATUS.md` — current dated state, results, fingerprints, limitations, next objective.

There is also a short steering pointer at `.kiro/project-context.md`.

---

## 1. Project purpose

Build and evaluate an **autonomous CTF-solving system** whose defining property is *trustworthiness*,
not raw coverage: it must reason from evidence, never fabricate or blind-guess flags, run the
cheapest discriminating test first, verify through a trust kernel before claiming a solve, and stop
correctly. The system was built in five phases (1–5) and then extended with an additive, **frozen-
solver-preserving** external-knowledge ingestion + retrieval evaluation track.

The engineered solver lives entirely under `.agent/`. The repository root additionally contains a
large historical corpus of prior CTF work (writeups, scratch scripts, playbooks) that predates the
engineered solver and is treated as read-only knowledge.

## 2. Workspace structure

```
<repo root>/
  AGENT_CONTEXT.md            <- this file
  AGENT_CONSTITUTION.md
  AGENT_ARCHITECTURE.md
  AGENT_STATUS.md
  .kiro/                      <- operator playbooks & lessons (RULE ZERO, mistakes, training notes)
  .agent_audit/               <- Phase-1 audit: failure corpus, technique/tool/trajectory memories,
                                 category playbooks, architecture recommendation (28 principles referenced)
  writeups/                   <- historical structured writeups (knowledge, read-only)
  <many root *.py/*.zip/*.md> <- historical CTF scratch work + challenge artifacts (knowledge, read-only)

  .agent/                     <- THE ENGINEERED SOLVER PROJECT
    pyproject.toml            <- pythonpath=["src"], testpaths=["tests"]
    README.md                 <- trust-kernel overview (labeled "Phase 2")
    src/
      ctf_agent/              <- FROZEN Phase 5 solver (45 .py files)
      ctf_bench/              <- FROZEN Phase 5 benchmark (single source of truth for cases)
      ctf_ingest/             <- EXPERIMENTAL ingestion/retrieval pipeline (additive)
      ctf_experiment/         <- EXPERIMENTAL evaluation harnesses (A/B, knowledge-dependent, DomeCTF eval)
    tests/                    <- full test suite
    docs/                     <- phase reports/designs + experiment result artifacts
    knowledge/                <- generated knowledge corpora + evaluation outputs
    scripts/                  <- reproducible runners for ingestion/experiments
```

## 3. Current solver architecture (summary)

Frozen mandated pipeline, preserved end to end (see `AGENT_ARCHITECTURE.md` for detail):

```
Action -> Observation -> Result Classification -> Evidence (+provenance)
      -> Hypothesis Impact -> State Update -> Verification / Continue / STOP
```

Layers (all under `.agent/src/ctf_agent/`, FROZEN):
- Trust Kernel (`kernel.py`) — atomic dedup→observation→classification→evidence→impact→state→verification.
- Result classification (`classifier.py`), conservative impact (`impact.py`), evidence ledger
  (`evidence.py`), immutable hypotheses (`hypothesis.py` / `hypothesis_engine.py`).
- Verification/stopping (`verification.py`), action deduplication (`deduplication.py`),
  failure memory (`failure_memory.py`), regression replay (`regression.py`).
- Reasoning loop (`loop.py`), planner (`planner.py`), autonomy layer (`autonomy/`), adapters
  (`adapters/`), five specialists (`specialists/` — web, crypto, pwn, reverse, forensics).

The reasoning source is advisory: it proposes typed hypotheses and actions; the kernel/planner/
verifier remain the sole authorities. LLM output cannot directly mutate trusted state.

## 4. Completed phases 1–5

- **Phase 1 — Failure/knowledge audit.** `.agent_audit/` corpus:The project contains multiple writeup/knowledge layers; the current
local knowledge store contains 32 extracted records.
- **Phase 2 — Trust Kernel.** Provider-independent kernel enforcing trustworthy state transitions;
  raw tool output cannot change beliefs or verify flags (`.agent/README.md`).
- **Phase 3 — Strategic Brain + Trusted Execution.** Context model, hypothesis engine, planner,
  reasoning loop, journal, advisory memory retrieval (`docs/phase3_report.md`).
- **Phase 4 — Specialist Intelligence Layer.** Exactly five specialists reasoning from current
  evidence + advisory memory (`docs/phase4_report.md`).
- **Phase 5 — Full Autonomous Solver + Evaluation Baseline.** Integration of Phases 1–4 into one
  solver plus an evaluation harness and a small deterministic synthetic benchmark; frozen baseline
  captured (`docs/phase5_report.md`, `docs/phase5_freeze.md`). Explicitly conservative: the
  benchmark is synthetic and is not evidence of general CTF-solving ability.

## 5. Knowledge corpora (generated, under `.agent/knowledge/`)

| Corpus | Records | What it is |
|---|---|---|
| `local_writeups/` | 32 | Ingested local historical writeups |
| `jiaje_v1/` | 4 | jia.je (jiegec) technique-reference pages |
| `jiaje_redbud_v1/store/` | 22 | Jia Jie Redbud challenge writeups (JS-rendered fetch) |
| `domectf_v1/store/` | 32 | DomeCTF (c0c0n) historical challenge writeups (2019/2020/2021) |
| `domectf_sources_v1/` | 40 refs / 49 raw | DomeCTF source discovery/verification inventory (not KnowledgeRecords) |
| `domectf_eval_v1/` | — | DomeCTF retrieval + A/B evaluation outputs (this track) |
| `_jiaje_cache/`, `_jiaje_js_cache/` | — | Raw fetch caches |

Provenance is preserved per record (source URL, canonical URL, content SHA-256, event, year,
challenge, extraction version). Extraction distinguishes EXPLICIT / INFERRED / MISSING and never
fabricates reasoning.

## 6. Retrieval architecture (summary)

- `ctf_ingest/retrieval.py` — `KnowledgeRetriever` (build `from_records`, query by text/category/keywords).
- `ctf_ingest/advisory_projection.py` — projects retrieved knowledge as advisory memory refs.
- `ctf_experiment/knowledge_reasoning.py` — `KnowledgeAugmentedReasoningSource`: retrieved knowledge
  may propose **typed candidate hypotheses only**, each with a standard discriminating test, then
  everything flows through the frozen pipeline. Escalation is budgeted (fast path first, ≤2
  retrievals). The executable knowledge→action bridge (`_WEB_TESTS`) currently maps only the
  technique_ids `ssti` and `sql-injection` to discriminating actions (web probe environment).
- `ctf_experiment/knowledge_solver.py` — `solve_with_knowledge`: the frozen solver composition with
  exactly one substitution (the augmented reasoning source). `retriever=None` reproduces frozen behavior.

Retrieval is NOT wired into the frozen solver for production; it is exercised only in the
experiment/evaluation harnesses.

## 7. Current development state

Phases 1–5 complete and Phase 5 frozen. Additive tracks completed: external ingestion (Jia Jie,
Jia Jie Redbud, DomeCTF), retrieval + knowledge-augmented A/B evaluation, and a controlled DomeCTF
knowledge evaluation. See `AGENT_STATUS.md` for exact results, the frozen fingerprint, test count,
and limitations.

## 8. Frozen boundaries (do NOT modify without explicit authorization)

- `.agent/src/ctf_agent/` — frozen Phase 5 solver (aggregate fingerprint below).
- `.agent/src/ctf_bench/phase5_benchmark.py` and `.agent/docs/phase5_results.json`,
  `.agent/docs/phase5_baseline.json`, `.agent/docs/phase5_freeze.md`.
- Knowledge corpora: `knowledge/jiaje_v1/`, `knowledge/jiaje_redbud_v1/`, `knowledge/domectf_v1/`,
  `knowledge/domectf_sources_v1/`, `knowledge/local_writeups/`.
- Prior experiment result artifacts under `.agent/docs/` (e.g. `knowledge_dependent_results.json`,
  `knowledge_dependent_results_v2.json`).
- `ctf_agent` must not import `ctf_ingest`.

Frozen `ctf_agent` aggregate SHA-256 (over sorted relpath + file digest, 45 files):
`ead35256c11e882157688410a9618de1e45c3f80a57f4bfb4be7728ebdffdb88`

## 9. Current objective

The next objective is **NOT another architecture phase**. It is:

> **REAL-WORLD CTF SOLVING AND EVALUATION.**

Apply the existing frozen solver + advisory knowledge to real challenges and measure honestly. Do
not build new solver architecture, add specialists, recover GitHub JS content, ingest more corpora,
or fine-tune, unless explicitly requested.

## 10. Bootstrapping a new AI session

1. Read `AGENT_CONTEXT.md`, `AGENT_CONSTITUTION.md`, `AGENT_ARCHITECTURE.md`, `AGENT_STATUS.md`.
2. Treat historical writeups/playbooks as advisory knowledge; **current challenge evidence always
   outranks historical knowledge**.
3. Before any code change: understand the task, inspect the relevant implementation files, identify
   affected architecture components, check the frozen boundaries (Section 8), inspect relevant tests,
   propose the smallest appropriate change, then implement and run tests.
4. Verify frozen artifacts are unchanged after work: recompute the `ctf_agent` aggregate fingerprint
   and confirm it equals the value in Section 8; confirm `phase5_results.json` and corpora are unchanged.
5. Run the suite from `.agent/` with `python -m pytest` (`pyproject.toml` sets `pythonpath=["src"]`).
6. Do not redesign the solver or modify frozen Phase 5 components/artifacts without explicit authorization.
