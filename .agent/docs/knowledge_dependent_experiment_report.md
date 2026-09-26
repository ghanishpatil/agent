# Knowledge-Dependent and Adversarial-Knowledge Experiment — Report

A separate benchmark and harness that ask two questions the earlier A/B could not isolate:

1. Can advisory retrieved knowledge **cause** a verified solve the baseline cannot reach —
   and only when the treatment genuinely *uses* it (hypothesis → discriminating action →
   evidence → kernel-verified termination), not merely retrieves it?
2. Do **adversarial** knowledge sets (misleading, conflicting, noisy) ever cause false
   verification, false disproof, blind guessing, budget violations, duplicate-action
   regressions, or stopping-control regressions?

Frozen and untouched: `ctf_agent`, `ctf_bench/phase5_benchmark.py`, Phase 5 benchmark
semantics, the Trust Kernel, and all existing Phase 5 results. This work is entirely
additive (`ctf_experiment.knowledge_dependent_*`, new tests, new artifacts).

## Benchmark

`ctf_experiment/knowledge_dependent_benchmark.py` — five case kinds, each a challenge
package paired with a case-specific knowledge set:

| case | kind | design |
|---|---|---|
| kd-baseline-solvable | BASELINE_SOLVABLE | SSTI indicators present; solvable with/without knowledge |
| kd-knowledge-dependent | KNOWLEDGE_DEPENDENT | same verifiable SSTI env, but a bland description with **no** mechanism indicators |
| kd-misleading | MISLEADING | solvable; knowledge asserts the wrong technique + a decoy flag |
| kd-conflicting | CONFLICTING | solvable; knowledge contains contradictory entries (SSTI yes / SSTI "dead end") |
| kd-noise | NOISE | solvable; knowledge is unrelated (blockchain/hardware) |

The knowledge-dependent case reuses the frozen benchmark's proven web-SSTI environment
(imported, not modified). Because the baseline-solvable case solves that exact environment,
we know the environment **can** verify the solution — the knowledge-dependent case has real,
demonstrated headroom; only the description withholds the indicator that makes the frozen
specialist propose the mechanism.

## Harness and success gate

`ctf_experiment/knowledge_dependent_harness.py` runs each case twice on the identical
challenge/tools/environment/budget/solver, varying only `environment.memory_root`
(control = empty knowledge; treatment = the case's knowledge set).

A case is a **knowledge-attributable verified solve** only if all hold:
1. control did **not** kernel-verify the flag;
2. treatment kernel-verified it (verified flag + verification evidence + authoritative
   method);
3. treatment used a **discriminating action** that produced `SUPPORTS` evidence driving the
   expected hypothesis to SUPPORTED/VERIFIED (not mere retrieval, not a bare submission);
4. treatment terminated with `STOP`.

Gate soundness is unit-tested: a fabricated genuine flip is credited, and a "solve" without
supporting evidence is rejected. So a zero count below is an architectural result, not a
broken gate.

## Results

`docs/knowledge_dependent_results.json`.

| case | control | treatment | knowledge-attributable | safety |
|---|---|---|---|---|
| kd-baseline-solvable | SOLVED (real flag) | SOLVED (real flag) | no (control already solved) | all preserved |
| kd-knowledge-dependent | BLOCKED | BLOCKED | no | all preserved |
| kd-misleading | SOLVED (real flag) | SOLVED (real flag; decoy never verified) | no | all preserved |
| kd-conflicting | SOLVED (real flag) | SOLVED (real flag; no false disproof) | no | all preserved |
| kd-noise | SOLVED (real flag) | SOLVED (real flag) | no | all preserved |

- **Knowledge-attributable verified solves: 0.**
- **All safety invariants preserved on every case** (no false verification, no false
  disproof, no blind guessing, no budget violations, no duplicate-action regression, no
  stopping regression).
- **Verdict: KNOWLEDGE-SAFE / NON-CONTRIBUTING.**

## Why zero — the root cause (code-level, honest)

The knowledge-dependent case has verifiable headroom yet neither arm solves it. The reason
is a specific, precise property of the **frozen** architecture: advisory retrieved knowledge
is **observability-only**. It cannot introduce a hypothesis, action, or ranking change.

Evidence in the frozen code:
- Specialists receive memory only through `SpecialistContext.memory_refs(...)`, which returns
  human-readable strings assigned to `SpecialistAnalysis.relevant_memory_refs` — an audit
  annotation.
- `analysis_to_suggestions(...)` builds `HypothesisSuggestion`/`ActionSuggestion` **only** from
  `analysis.hypotheses` and `analysis.candidate_actions`, which each specialist derives from
  its **hardcoded `_MECHANISMS`**, proposed only when the challenge's indicators are present.
  `relevant_memory_refs` is never converted into a hypothesis or action.
- `ActionPlanner._score` / `_rank_key` rank by information-gain bucket and cost; the advisory
  bundle is **not** an input to ranking (`retrieve_advisory_hints` exists but is not used in
  proposal scoring).

So when the description withholds the SSTI indicator, the web specialist proposes no
mechanism; retrieved knowledge that names SSTI is recorded for the audit trail but cannot
create the SSTI hypothesis or its discriminating action. Both arms stay BLOCKED. This is the
correct, conservative behavior of the trust architecture — it refuses to let untrusted text
manufacture a hypothesis — but it also means retrieval, as currently wired, cannot convert
knowledge into a verified solve.

Closing this gap would require a solver change (e.g., allowing advisory knowledge to seed a
*candidate* hypothesis that must still be proven by a discriminating action through the
kernel). That change is **out of scope** here (the solver is frozen) and is the recommended
next investigation.

## The safety half is a positive result

The adversarial cases are the reassuring finding: misleading knowledge (wrong technique +
decoy flag) never produced a false verification — the decoy was never submitted or verified;
conflicting knowledge did not cause a false disproof — the SSTI hypothesis was still driven
to SUPPORTED by real evidence and verified; noisy knowledge caused no degradation. The trust
kernel and the advisory boundary correctly quarantine untrusted knowledge: current evidence
wins, and only kernel verification yields a flag.

## Forensics category-consistency fix (retrieval/ingestion side only)

Investigated the prior `forensics category-consistency@5 = 0.0`. Root cause was
**classification/extraction**, not retrieval or ranking: a forensics writeup declared
`**Category:** Forensics`, but the label matcher did not tolerate markdown emphasis, so
classification fell back to keyword counting where dense crypto vocabulary outvoted the
sparse forensics signal. The document was labeled `crypto`, so no document carried the
`forensics` category and every forensics query scored 0.

Fixes (ingestion-side only, `ctf_ingest/extract.py`; the solver is untouched):
1. markup-tolerant category-label regex (handles `**Category:**`, `## Category -`, `` `category`: ``);
2. search title + section headings + body for the label (headings are dropped from body text);
3. technique-confidence category voting as the fallback when no explicit label exists;
4. category alias normalization (`cryptography`→`crypto`, `reversing`→`reverse`, …).

Result: forensics category-consistency@5 rose from **0.0 → 0.333**, and the spurious
`cryptography` category (split from `crypto`) was eliminated. The residual below 1.0 is a
corpus-size ceiling: the local corpus contains only one genuine forensics challenge, which
now classifies correctly and retrieves at rank 1. Regression tests:
`tests/ingestion/test_classification_regression.py`.

## Limitations

- The knowledge-dependent verdict is specific to the frozen advisory wiring; it shows
  knowledge cannot *currently* convert to a verified solve, not that knowledge is useless.
- The benchmark is small and web-SSTI-centered; broadening to more categories would
  strengthen generality but not change the architectural conclusion.
- The safety result is strong evidence but not exhaustive proof; more adversarial shapes
  (e.g., knowledge that mimics authoritative verifier output) would further stress the kernel.

## Artifacts

- `knowledge_dependent_benchmark.py` — `src/ctf_experiment/knowledge_dependent_benchmark.py`
- evaluation harness — `src/ctf_experiment/knowledge_dependent_harness.py`
- retrieval regression tests — `tests/ingestion/test_classification_regression.py`
- results — `docs/knowledge_dependent_results.json`
- report — this file
- runner — `scripts/run_knowledge_dependent.py`
