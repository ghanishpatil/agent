# Phase 5 Report — Full Autonomous CTF Solver and Evaluation Baseline

This report documents the integration of the Phase 1–4 components into a single
autonomous CTF-solving system, the evaluation harness used to measure it, and the
reproducible clean baseline captured before any external writeup corpus is introduced.

It is deliberately conservative. The benchmark is a small deterministic synthetic
suite. Nothing here should be read as evidence of general CTF-solving ability.

## 1. Final architecture

The mandated pipeline is preserved end to end and no component bypasses it:

```
CTF INPUT -> CONTEXT MODEL -> STRATEGIC BRAIN
   -> {HYPOTHESES, SPECIALISTS, MEMORY}
   -> ACTION PLANNER -> TRUSTED ADAPTERS -> PHASE 2 KERNEL
   -> RESULT CLASSIFIER -> EVIDENCE -> HYPOTHESIS IMPACT
   -> STRATEGIC BRAIN (loop) -> CANDIDATE -> VERIFICATION -> STOP -> FLAG
```

Phase 5 is additive. It introduces one package, `ctf_agent.autonomy`, that composes
the existing modules behind a single façade. The Phase 2 `TrustKernel.process()`
remains the only trusted state transition, Phase 3's planner/adapters/deduplication
remain authoritative, and Phase 4 specialists remain advisory.

### Additive module layout

```
ctf_agent/autonomy/
  contracts.py    challenge/resource/environment/constraint + SolveResult types
  control.py      deny-before-execute budgets, deadline, state/prerequisite reducer
  reasoning.py    RoutedReasoningSource (candidate routing over a reasoning source)
  resources.py    materialize supplied resource content under the permitted workspace
  understanding.py challenge understanding + KNOWN/UNKNOWN/ASSUMED/INFERRED/VERIFIED facts
  solver.py       solve(challenge, resources, environment, constraints) composition root
  evaluation.py   labeled KNOWN/NOVEL/ADVERSARIAL/HELD_OUT harness + 20 metrics
  baseline.py     reproducible JSON baseline manifest generation
```

Existing-file changes were limited to additive controller hooks and a `TIMEOUT`
outcome in `loop.py`, additive event kinds in `journal.py`, a per-context analysis
cache + invocation guard + audit callbacks in `specialists/brain.py`, and public
Phase 5 exports in `ctf_agent/__init__.py`. No Phase 2 module was modified.

## 2. Autonomous loop

The deterministic system, not the LLM, drives the loop. Each iteration observes the
current state, refreshes challenge understanding, retrieves advisory knowledge,
selects relevant specialists, gathers advisory hypotheses/actions, plans through the
deduplicating planner, executes one permitted action through a trusted adapter,
classifies the result, records evidence, computes hypothesis impact, updates relevant
state, and adapts. It verifies only when a candidate is bound to supported evidence,
and stops on the first kernel-verified flag. There is no uncontrolled recursive LLM
call: the reasoning source proposes, the deterministic layer disposes.

## 3. Solver interface

```
solve(challenge, resources=(), environment=None, constraints=None) -> SolveResult
```

`SolveStatus` is one of `SOLVED`, `BLOCKED`, `EXHAUSTED`, `FAILED`, `INVALID_INPUT`,
`TIMEOUT`. `verified_flag` is populated only when the final kernel snapshot contains a
`VERIFIED` candidate under a global `STOP`. Non-solved results carry a terminal reason,
remaining hypotheses, unresolved blockers, important evidence, and attempted actions;
`verified_flag` is always `None` for them (enforced in `SolveResult.__post_init__`).

## 4. Specialist orchestration

Specialists (Web, Crypto, Reverse, Forensics, Pwn) are selected from evidence, not
invoked uniformly. They analyze, propose mechanisms/hypotheses/tests/actions, and
interpret evidence. They may not execute tools, mutate evidence, verify flags, or
declare a solve. The Strategic Brain mediates all cross-specialist interaction, and a
one-batch-per-context cache means the loop's hypothesis and action requests share a
single specialist pass.

## 5. Memory usage

Retrieval is over the existing Phase 1 `.agent_audit` corpus only; it is read-only and
advisory. No external writeup corpus is ingested in Phase 5. Where memory conflicts
with current observation, current evidence wins (`EvidenceManager.resolve_conflict`).

## 6. Evidence and verification lifecycle

Every observation is classified, converted to evidence with provenance, and mapped to
a hypothesis impact. A candidate records value, origin, mechanism, evidence references,
and derivation. A flag is never trusted for looking like a flag, matching a regex,
being LLM/specialist-suggested, or appearing in history. Final verification requires an
authoritative route (here, the local grading verifier), producing
`final_verification_method = AUTHORITATIVE_VERIFIER`.

## 7. Failure recovery and state management

Failures are classified before strategy changes: tool failure, environment failure,
network failure, auth/authz failure, rate limit, malformed output, contradiction, and
so on. A classified failure never becomes a hypothesis disproof. Structured
`ExecutionResult.metadata` advances environment/auth/session/challenge revision and
prerequisites; an undeclared mutation blocks further execution rather than continuing
blindly. Attempt limits tighten (never loosen) the submission/remote budget.

## 8. Stopping behavior

On the first independently verified flag the solver emits a global `STOP` and returns;
no further exploration, confirmation, or environment mutation occurs. `stop_correctness`
verifies STOP appears exactly once and only as the terminal action of a solved run.

## 9. Evaluation methodology

`EvaluationHarness` runs labeled cases and supplies only a challenge, resources, an
environment factory, and constraints plus independent ground truth. It never supplies
an action sequence or the correct hypothesis; scenario tools/oracles may produce or
verify observations but cannot select the next action. Failures are recorded openly.

### Benchmark composition (6 cases)

| case_id | kind | mechanism | expected |
|---|---|---|---|
| known-xor | KNOWN | single-byte XOR, dead-end recovery from base64 | SOLVED |
| novel-ssti | NOVEL | server-side template injection | SOLVED |
| adversarial-decoy | ADVERSARIAL | SQL hint + flag-shaped decoy, true SSTI | SOLVED |
| heldout-classical | HELD_OUT | Caesar shift (not XOR), tool-failure recovery | SOLVED |
| environment-recovery | ADVERSARIAL | SQL path env-failure, recover to SSTI | SOLVED |
| unavailable-tool | ADVERSARIAL | required tool unavailable | BLOCKED |

The KNOWN/HELD_OUT pair is an anti-memorization test: XOR versus a structurally similar
but mechanistically different Caesar shift. The solver reasons from mechanism and
evidence rather than replaying the KNOWN answer.

## 10. Metrics and results

Measured by `scripts/generate_phase5_baseline.py` and recorded in
`docs/phase5_baseline.json`.

| # | metric | value |
|---|---|---|
| 1 | solve rate | 0.833 (5/6) |
| 2 | verified solve rate | 0.833 |
| 3 | false-verification rate | 0.000 |
| 4 | false-disproof rate | 0.000 |
| 5 | average actions per solve | 2.80 |
| 6 | median actions per solve | 3 |
| 7 | duplicate-action rate | 0.360 |
| 8 | blind-retry rate | 0.000 |
| 9 | dead-end recovery rate | 1.000 |
| 10 | environmental-failure recovery rate | 1.000 |
| 11 | tool-failure recovery rate | 1.000 |
| 12 | specialist selection accuracy | 1.000 |
| 13 | useful specialist proposal rate | 1.000 |
| 14 | candidate verification success | 1.000 |
| 15 | stop correctness | 1.000 |
| 16 | budget violations | 0 |
| 17 | average reasoning iterations | 2.83 |
| 18 | average time to verified solution | 377.8 ms |
| 19 | average resource/tool cost | 2.67 |
| 20 | terminal-state correctness | 1.000 |

The single non-solve (`unavailable-tool`) is an intended `BLOCKED` outcome and is
reported, not hidden. Solve rate is below 1.0 precisely because the blocked case is
counted.

## 11. Knowledge vs reasoning

Each case records knowledge attribution. On this synthetic suite every solve is driven
by direct mechanism reasoning and specialist analysis over challenge artifacts, with
memory/known-technique tags available but not decisive. This separation exists so the
post-Phase-5 external-corpus project can measure whether added writeups improve
reasoning or merely add recognition.

## 12. Baseline configuration

`docs/phase5_baseline.json` records UTC generation time, git state (recorded as
`unavailable` in this environment), Python 3.10.7 / Windows platform, the exact case
ids and labels, tool names, model configuration (deterministic specialist brain; no
external LLM configured), `.agent_audit` memory file hashes, all 20 aggregate metrics,
per-case outcomes, and SHA-256 integrity for the protected trees
(`.agent_audit` 15 files, `.kiro` 8 files, `writeups` 32 files). It is regenerated by
`python scripts/generate_phase5_baseline.py`.

## 13. Limitations and known weaknesses

- The benchmark is small (6 cases) and fully synthetic/deterministic. Metrics reflect
  architectural behavior, not real-world CTF difficulty.
- Adapters exercised are in-process test doubles plus a Python subprocess decoder; no
  real remote target, real binary exploitation, or real network I/O is measured.
- The reasoning source is the deterministic specialist brain; no external LLM is wired,
  so language-understanding limits are not exercised.
- Duplicate-action rate (0.36) reflects that the deduplicator legitimately rejects
  repeat proposals during exploration; it is a control signal here, not a defect, but
  it is not yet tuned against a large action space.

## 14. Unresolved bugs

- None known at this revision. During this audit a missing `EvidenceRule` import in
  `autonomy/solver.py` was fixed; the full suite and baseline are green afterward.

## 15. Architectural deviations

- Input-epistemic facts (`KNOWN/UNKNOWN/ASSUMED/INFERRED/VERIFIED`) live in a Phase 5
  understanding layer and deliberately do not alter Phase 3 `FactState` or kernel
  evidence. This is an intentional additive layer, not a change to trusted state.
- No other deviations from the frozen Phase 2/3/4 boundaries.

## 16. Post-Phase-5 recommendation

Proceed to **External CTF Writeup Ingestion and Knowledge Expansion** as a separate
project, evaluated against this baseline. Ingestion must remain advisory (retrieval
only), must not weaken any Phase 2 trust boundary, and must be measured by re-running
this harness so the baseline-vs-augmented comparison isolates the knowledge variable.

---

PHASE 5 STATUS:
COMPLETE

TESTS:
264 passed

HISTORICAL REGRESSIONS:
12/12 pass

AUTONOMOUS SCENARIOS:
pass (solver decides all actions from challenge + resources + environment; no scripted action sequences)

HELD-OUT EVALUATION:
pass (heldout-classical Caesar solved by mechanism reasoning, distinct from the KNOWN XOR case)

SOLVE RATE:
0.833 (5/6; the sixth case is an intended BLOCKED outcome)

VERIFIED SOLVE RATE:
0.833

FALSE VERIFICATION:
0.000

FALSE DISPROOF:
0.000

DUPLICATE ACTION RATE:
0.360

AVERAGE ACTIONS:
2.80 (median 3)

STOP CORRECTNESS:
1.000

KNOWN LIMITATIONS:
- small synthetic deterministic benchmark (6 cases)
- in-process/subprocess adapters only; no real remote/binary/network execution
- deterministic specialist brain; no external LLM wired
- duplicate-action rate untuned against a large action space

UNRESOLVED BUGS:
- none known at this revision

ARCHITECTURAL DEVIATIONS:
- Phase 5 input-epistemic understanding layer is additive and does not alter Phase 3 FactState or kernel evidence
- no Phase 2/3/4 trust-boundary weakening

BASELINE STATE:
docs/phase5_baseline.json — 264 tests; 12/12 historical; tools {decode_tool, flag_verifier, http_probe}; model "deterministic specialist brain; no external LLM configured"; protected trees intact (.agent_audit 15, .kiro 8, writeups 32); no external writeups ingested; no fine-tuning

POST-PHASE-5 RECOMMENDATION:
External CTF Writeup Ingestion and Knowledge Expansion
