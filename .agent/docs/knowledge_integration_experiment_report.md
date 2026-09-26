# Knowledge → Hypothesis Integration (v2) — Experiment Report

This phase implements the **minimum additive** Knowledge → Hypothesis integration with
performance-first behavior, then re-runs the knowledge-dependent + adversarial benchmark as a
**new experiment version** (v2). It does not overwrite the earlier v1 KNOWLEDGE-SAFE /
NON-CONTRIBUTING result.

## What was and was not changed

Frozen and untouched: `ctf_agent` (TrustKernel, EvidenceManager, VerificationController,
planner, specialists, loop), `ctf_bench/phase5_benchmark.py`, Phase 5 semantics, and the
existing Phase 5 results. Verified via fingerprints (below).

The integration is entirely additive and reuses the frozen system's sanctioned extension
point — the Phase 3 `ReasoningSource` Protocol that `ReasoningLoop` already consumes and that
`_seed_hypotheses` already routes through `board.propose_hypothesis`. No new architectural
subsystem was introduced.

New modules (all in `ctf_experiment/`, none imported by `ctf_agent`):
- `knowledge_reasoning.py` — `KnowledgeAugmentedReasoningSource`: wraps the frozen specialist
  brain, implements `suggest_hypotheses`/`suggest_actions`/`interpret`, and — only on escalation
  — emits **typed candidate hypotheses** (plus the standard discriminating test for a retrieved
  technique). It cannot execute, create evidence, verify, bypass the planner, or stop.
- `knowledge_solver.py` — `solve_with_knowledge`: the frozen `solve()` happy-path composition,
  reusing the frozen helpers verbatim, with exactly one substitution: the reasoning source is
  wrapped by the augmented source before the existing `RoutedReasoningSource`.
- `knowledge_dependent_benchmark_v2.py`, `knowledge_dependent_harness_v2.py` — v2 benchmark and
  A/B harness.

Fidelity is tested: `solve_with_knowledge(retriever=None)` reproduces frozen `solve()`
(status + verified flag) on a baseline case.

## The pipeline is unchanged

A knowledge-derived hypothesis flows through the exact same path as any specialist hypothesis:

```
candidate (typed HypothesisSuggestion) -> validate_hypothesis_suggestion -> board.propose_hypothesis
  -> planner (dedup + rank + validation) -> trusted adapter execution -> classifier
  -> EvidenceManager (provenance preserved) -> hypothesis impact -> VerificationController -> STOP
```

Knowledge only proposes. The kernel still classifies, records evidence, decides impact, and is
the sole verifier. A knowledge-derived candidate flag is submitted only via the existing
`RoutedReasoningSource` eligibility gate (hypothesis must be kernel-SUPPORTED and the candidate
must already be bound in trusted evidence), so knowledge can never verify a flag by itself.

## Performance-first escalation policy (simple deterministic budgets)

1. Fast path: each iteration, if the frozen brain already yields an actionable step (or a
   knowledge branch is already in progress), do nothing extra — no retrieval.
2. Escalate only when the branch stalls (no actionable proposal) and the retrieval budget
   remains (`max_retrievals=2`).
3. On escalation: one targeted retrieval; generate at most `max_candidates=2` typed candidate
   hypotheses, each with its standard cheapest discriminating test.
4. If retrieval yields nothing usable, count it and stop retrieving (exhausted).
5. Once the kernel verifies a flag, the loop stops immediately (unchanged).

No utility/optimization framework — just counters and thresholds.

## Results (v2)

`docs/knowledge_dependent_results_v2.json`, `docs/knowledge_integration_performance.json`.

Verdict: **KNOWLEDGE-CONTRIBUTING — 2 knowledge-attributable verified solves; all safety
invariants preserved; easy cases stayed on the fast path.**

| case | kind | control | treatment | retrievals | knowledge hyps | attributable |
|---|---|---|---|---|---|---|
| kd2-baseline-solvable | BASELINE_SOLVABLE | SOLVED | SOLVED | 0 | 0 | no (control already solved) |
| kd2-knowledge-dependent | KNOWLEDGE_DEPENDENT | BLOCKED | SOLVED | 1 | 1 | **yes** |
| kd2-conflicting | CONFLICTING | BLOCKED | SOLVED | 1 | 1 | **yes** |
| kd2-misleading | MISLEADING | BLOCKED | BLOCKED (decoy never verified) | 1 | 1 | no |
| kd2-noise | NOISE | BLOCKED | BLOCKED (0 actions) | 1 | 0 | no |

The five required demonstrations:
1. **Retrieval causes a new verified solve** — `kd2-knowledge-dependent`: control BLOCKED,
   treatment SOLVED (`CTF{kd2_dependent}`). The knowledge-derived `web-ssti` hypothesis was
   proven by a discriminating action (EVAL=49 → SUPPORTS) and verified by the kernel, then STOP.
   `kd2-conflicting` is a second such solve.
2. **Misleading knowledge rejected through evidence** — `kd2-misleading`: the retrieved (wrong)
   SQL-injection hypothesis was tested; the response contradicted it, and the decoy flag
   `CTF{sqli_decoy_should_never_verify}` was never verified (the verifier route refused it
   because the hypothesis was not kernel-SUPPORTED). No false verification.
3. **Irrelevant knowledge → no unnecessary exploration** — `kd2-noise`: one bounded retrieval
   found nothing usable (blockchain/hardware records), produced 0 hypotheses and executed 0
   actions, and the run stopped BLOCKED. No wasted probing.
4. **Conflicting knowledge resolved by current evidence** — `kd2-conflicting`: knowledge
   contained both "it is SSTI" and "SSTI is a dead end"; current evidence (EVAL=49) drove
   `web-ssti` to SUPPORTED and the solve succeeded. No false disproof.
5. **Easy case stays fast** — `kd2-baseline-solvable`: indicators present, the frozen brain
   solved it with **0 retrievals** and no knowledge hypotheses.

### Metrics (aggregate)

| metric | value |
|---|---|
| knowledge-attributable verified solves | 2 |
| mean time to first action | ~11.5 ms |
| mean time to verified flag | ~25.8 ms |
| mean actions per solve | 1.6 |
| total retrieval calls | 4 |
| knowledge-derived hypotheses | 3 |
| unnecessary retrievals | 1 (noise) |
| duplicate actions (executed) | 0 (1 proposal deduped in misleading) |
| budget violations | 0 |
| false verifications | 0 |
| false disproofs | 0 |
| stopping-correct cases | 5 / 5 |
| fast-path cases (0 retrieval) | 1 |

(Times are wall-clock from journal timestamps and will vary slightly per run; the deterministic
counts — actions, retrievals, hypotheses, duplicates — are stable.)

## Safety and trust boundaries

- No false verification on any case; the misleading decoy never verified.
- No false disproof; conflicting knowledge did not disprove the correct mechanism.
- No blind guessing: a candidate is submitted only from evidence bound to a SUPPORTED hypothesis
  (existing `RoutedReasoningSource` + kernel `FlagAttemptRegistry` rules).
- No budget violations; no executed duplicate actions (dedup is structural).
- Stopping correctness preserved: solved runs end with exactly one STOP; non-solved runs have none.
- Provenance and the evidence hierarchy are preserved — knowledge records enter only as typed
  candidate hypotheses; evidence still originates from trusted adapter executions.

## Relationship to v1

v1 (`docs/knowledge_dependent_results.json`) measured the frozen `solve()` where advisory memory
is observability-only, and correctly found 0 knowledge-attributable solves. v2 keeps that result
intact and adds the minimal integration at the reasoning boundary, which converts retrieval into
verified solves on genuinely knowledge-dependent cases while preserving every safety invariant.

## Limitations

- The technique→discriminating-test mapping is a tiny deterministic table (web SSTI/SQLi) — enough
  to demonstrate the mechanism end-to-end; broader coverage is future work.
- The benchmark is small and web-centric; the conclusion is that the integration path is sound and
  safe, not that coverage is complete.
- The augmented composition duplicates the frozen `solve()` wiring (reusing frozen helpers) because
  `solve()` exposes no reasoning-source injection hook; if a future `solve(reasoning_source=...)`
  seam is added, this composition collapses to a one-line override.

## Artifacts

- implementation: `src/ctf_experiment/knowledge_reasoning.py`, `knowledge_solver.py`,
  `knowledge_dependent_benchmark_v2.py`, `knowledge_dependent_harness_v2.py`
- tests: `tests/experiment/test_knowledge_integration.py`
- performance results: `docs/knowledge_integration_performance.json`
- knowledge-dependent A/B results: `docs/knowledge_dependent_results_v2.json`
- runner: `scripts/run_knowledge_integration.py`
