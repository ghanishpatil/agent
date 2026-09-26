# Retrieval Layer + Knowledge-Augmented A/B Experiment — Report

This phase builds an advisory **retrieval layer** over the ingested knowledge store,
integrates it at the solver's **existing advisory-memory boundary without modifying
`ctf_agent`**, and runs a controlled **A/B experiment** on the exact frozen Phase 5
benchmark. It also produces an **independent retrieval-quality evaluation**. The question:
does external knowledge improve verified solving without increasing false
verification/disproof or violating control invariants?

## Constraints honored

- `ctf_agent` solver unchanged — aggregate fingerprint still `ead35256…dfdb88`.
- Phase 5 benchmark semantics unchanged — cases come from the frozen
  `ctf_bench.build_phase5_cases`; only `environment.memory_root` differs between arms.
- Protected trees untouched. `.agent_audit` is treated as read-only: the treatment arm
  runs against a *copy* with external knowledge layered on.
- Retrieval is advisory only. It enters solely through `AdvisoryMemory` →
  `AdvisoryBundle`, which by construction can never become a hypothesis, action, or
  evidence, and cannot verify a flag. The trust kernel is the only authority.

## Integration point

`solve()` already reads advisory memory from a directory:
`memory = _memory(environment.memory_root)` → `AdvisoryMemory(root)`, which loads
`knowledge/technique_memory.jsonl` and `trajectories/trajectories.jsonl` (plus tools and
failures). The retrieval layer therefore integrates by **projecting** ingested
`KnowledgeRecord`s into that on-disk schema. No new code path into the solver is created;
we reuse the exact advisory boundary the frozen system already trusts (and constrains).

Pipeline: `KnowledgeStore` → `KnowledgeRetriever` (rank) →
`advisory_projection.build_augmented_memory` (copy audit + append external rows) →
`environment.memory_root` → frozen `solve()`.

## Retrieval layer

`ctf_ingest.retrieval.KnowledgeRetriever` — deterministic, dependency-free ranking
(no embeddings), scoring each record by category match (weight 3), technique-keyword
overlap (weight 2), and token overlap (weight 1). Duplicates are excluded from the
searchable set. Returns ranked results with matched terms and scores.

## A/B experiment design

- **Control**: frozen solver + existing `.agent_audit` advisory memory (the Phase 5
  baseline advisory condition).
- **Treatment**: frozen solver + (`.agent_audit` copy + projected external writeup
  knowledge from the 32-record local corpus).
- Everything else identical: same frozen benchmark, kernel, planner, adapters,
  verification, budgets.

### Control reproduces the frozen baseline

`docs/knowledge_ab_results.json` (control arm): 6 cases, verified solve rate 0.833 (5/6;
the sixth is the intended `unavailable-tool` BLOCKED), false verification 0.0, budget
violations 0 — matching `docs/phase5_results.json`. This confirms the harness runs the
real baseline.

### Result (treatment vs control)

| metric | delta (treatment − control) |
|---|---|
| verified solve rate | 0.000 |
| solve rate | 0.000 |
| false verification rate | 0.000 |
| false disproof rate | 0.000 |
| duplicate action rate | 0.000 |
| average actions per solve | 0.000 |
| budget violations | 0 |

Invariants (all preserved): no increase in false verification, no increase in false
disproof, no budget violations, no solved→unsolved regression, stop correctness
maintained, terminal-state correctness maintained.

**Verdict: NEUTRAL.** External knowledge neither improved nor harmed verified solving on
this benchmark, and violated no control invariant. No flags were fabricated; no
previously unsolved case became "solved".

### Why neutral (honest mechanism)

This is an expected, truthful result, not a tuning failure:
1. The advisory bundle only influences the planner's **ranking** of proposals it already
   built from current context. It cannot introduce a capability.
2. At baseline the solver already solves all mechanism-solvable cases in ≤3 actions, so
   re-ranking cannot add a solve or reduce an already-minimal action count.
3. The one non-solved case (`unavailable-tool`) is BLOCKED because a required tool is
   unavailable — no amount of advisory knowledge can (or should) manufacture a missing
   tool. Correct control behavior is to stay BLOCKED, which it did.

In short: the benchmark has no headroom that advisory retrieval could convert, and the
system correctly refused to convert absent capability into a fabricated solve. The
valuable finding is the **guardrail result**: adding external knowledge did not degrade
verification integrity or control invariants.

## Independent retrieval quality

`docs/retrieval_quality.json`.

Labeled synthetic corpus (controlled, non-circular ground truth), k=5:
- mean precision@5: 0.486
- mean recall@5: 1.000
- mean reciprocal rank: 1.000

Recall and MRR are perfect: every relevant record is retrieved within the top 5, and the
top-ranked result is always relevant. Precision@5 is moderate because relevant sets are
small (1–2 docs), so the top-5 necessarily includes same-category non-relevant neighbors
— expected for tiny gold sets and not a ranking defect (MRR=1.0 confirms correct ordering).

Real writeups store (descriptive category-consistency@5): mean 0.75 — web/crypto/pwn
1.0, reverse 0.75, forensics 0.0. The forensics query surfaced non-forensics records: a
real, reportable weakness of keyword/category retrieval on a small heterogeneous corpus.

## Conclusion and recommendation

- Retrieval integrates cleanly at the advisory boundary with zero solver changes and
  strong ranking behavior (recall/MRR perfect on the labeled set).
- On the frozen Phase 5 benchmark, knowledge augmentation is **safe but not
  improving**: verified solving is unchanged and all control invariants hold.
- Because retrieval alone shows no verified-solve gain **on a benchmark with no headroom**,
  the correct next step is **not** fine-tuning. It is to build a benchmark with genuine
  knowledge-dependent challenges (cases the mechanism-only solver cannot solve unaided but
  a relevant writeup would unlock), then re-run this exact A/B. Only if retrieval helps
  there — without raising false verification/disproof — is fine-tuning worth investigating.

## Limitations

- The benchmark is small and designed for mechanism reasoning, giving retrieval no
  headroom to demonstrate gains; a NEUTRAL result cannot prove knowledge is useless, only
  that it did not help *here*.
- Retrieval is lexical (category/keyword/token), not semantic; the forensics miss shows
  the ceiling on a small heterogeneous corpus.
- Advisory memory affects only planner ranking in the frozen design; a larger effect would
  require a knowledge-dependent benchmark, not a solver change (which is out of scope).
- The external corpus is the 32 local writeups; a larger public corpus (e.g. a Jia Jie
  mirror via the git source) would broaden coverage but does not change the experimental
  design.
