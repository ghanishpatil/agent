# Controlled Knowledge-Augmented Solver Integration & Evaluation — Report

Status: **COMPLETE / GREEN**. Additive to `ctf_experiment` only. Frozen `ctf_agent/**` and external
corpora are byte-for-byte unchanged. Not a new phase, not a solver redesign, no fine-tuning/RL.

Core principle enforced end to end: **Knowledge may suggest. Current evidence must authorize.
Planner / TrustKernel / verification remain the sole authorities.**

---

## 1. Architecture

The already-complete `KnowledgeTranslator` is connected to the solve path through a **controlled
experiment**, gated by an explicit switch, feeding the EXISTING frozen pipeline. Nothing about
execution, classification, evidence, or verification changes — knowledge only contributes advisory
typed proposals that the frozen components then own.

Reuse (no duplication): the treatment source subclasses the existing
`KnowledgeAugmentedReasoningSource` (inheriting its fast-path escalation, per-context caching,
dedup-aware action emission, probe-tool selection, metrics) and overrides ONLY the
retrieval→proposal step to use trajectory-first translation instead of the narrow `_WEB_TESTS`
table. The composition reuses `solve_with_knowledge` via a single additive injection hook.

## 2. Control path

```
challenge -> solve_experimental(knowledge_mode=OFF)
          -> solve_with_knowledge(retriever=None, source=ExperimentalTranslationSource[OFF])
          -> frozen SpecialistReasoningSource (brain) only
          -> ActionPlanner -> TrustKernel -> trusted adapters -> classifier -> evidence -> verification
```
In OFF mode the treatment source's `_knowledge_for` returns `((), ())` and the retriever is forced
to `None`, so behavior is identical to the established knowledge-off baseline
(`solve_with_knowledge(retriever=None)`). Test 1 asserts equal status, flag, and action count.

## 3. Treatment path

```
challenge -> solve_experimental(knowledge_mode=EXPERIMENTAL, retriever=...)
          -> existing retrieval (KnowledgeRetriever)
          -> KnowledgeTranslator (trajectory-first, advisory)
          -> advisory HypothesisSuggestion / ActionSuggestion  (candidate_flag forced empty)
          -> existing brain + ExperimentalTranslationSource (merges base + knowledge proposals)
          -> ActionPlanner -> TrustKernel -> trusted adapter -> classifier -> evidence -> verification
```
Knowledge proposals are added ONLY on a genuine stall (the inherited fast path: if the brain is
productive, no retrieval happens). A runnable knowledge probe carries the objective signature
`knowledge-derived discriminating test for <technique>`, so its execution is identifiable in the
authoritative `SolveResult` for attribution.

## 4. Feature flag

`KnowledgeMode` = `OFF` (default) | `EXPERIMENTAL`. It must be passed explicitly to
`solve_experimental`. Nothing enables it implicitly. The MCP gateway/server and Architecture A are
NOT changed and remain knowledge-OFF; the demo/operator gateways are unaffected.

## 5. Data flow

Retrieval → `KnowledgeTranslator.translate_record(record, TranslationContext)` → `TranslationResult`
(`RUNNABLE_TEST` | `HYPOTHESIS_ONLY` | `ADVISORY_CONFLICT` | `NOT_APPLICABLE`). The
`TranslationContext` is built ONLY from grounded current facts (`metadata.urls`, category,
registered `available_tools`, and mechanisms already DISPROVEN by current evidence). A
`RUNNABLE_TEST` becomes an inert `CandidateAction`; every result becomes a `HypothesisSuggestion`.
These flow to the frozen planner unchanged. Every proposal is recorded in a `KnowledgeTrace` for
evidence-based attribution.

## 6. Safety boundaries

Knowledge MAY suggest a mechanism/hypothesis/discriminating test and influence prioritization
through the normal reasoning path. Knowledge MAY NOT: declare solved, disprove a hypothesis, make
evidence authoritative, inject a historical flag (probes force `candidate_flag=""`), or bypass the
planner/kernel/adapters/classifier/verification. Exact-target safety from the translation layer is
preserved: runnable targets are built only from the grounded base with the same `quote()` encoding
as the evidence rule (`*` → `%2A`); a retrieved host mismatch or exact-target byte mismatch
downgrades to hypothesis-only. Current authoritative evidence always outranks retrieved knowledge
(`ADVISORY_CONFLICT` when a mechanism is already disproven).

## 7. Attribution model

Evidence-based, from the actual executed trace (never from "retrieval happened"):

| Category | Condition |
|---|---|
| `NO_KNOWLEDGE` | no knowledge proposals were made |
| `KNOWLEDGE_HYPOTHESIS_ONLY` | knowledge proposed, but no knowledge-derived test executed |
| `KNOWLEDGE_GUIDED_TEST` | a knowledge-derived test executed, but did not evidence-enable the solve (or the control solved independently) |
| `KNOWLEDGE_DIRECTLY_ENABLED_SOLVE` | a knowledge-derived test executed AND produced authoritative `SUPPORTS` evidence for a knowledge hypothesis AND the run verified the flag AND the paired control did NOT independently verify-solve |

A retrieved-but-unused writeup, or a path the normal solver discovered first (its knowledge twin
becomes a planner `DUPLICATE`), is never counted as a contribution.

## 8. Evaluation methodology

Paired CONTROL (knowledge OFF) vs TREATMENT (knowledge EXPERIMENTAL) over the existing knowledge-v2
benchmark (`build_cases_v2` + `web_environment`). Both arms share identical challenge, tools,
environment, budgets, and solver configuration; only `knowledge_mode` (+ retriever) differ. Run via
`run_knowledge_integration_experiment`; results saved to `docs/knowledge_integration_results.json`.

## 9. Results

`516 passed, 0 failed` overall. Paired evaluation (5 v2 cases):

| Case | Control | Treatment | Contribution | Safe |
|---|---|---|---|---|
| kd2-baseline-solvable | SOLVED | SOLVED | `NO_KNOWLEDGE` (brain solved alone; no retrieval) | yes |
| kd2-knowledge-dependent | BLOCKED | SOLVED | `KNOWLEDGE_DIRECTLY_ENABLED_SOLVE` | yes |
| kd2-misleading | BLOCKED | BLOCKED | `KNOWLEDGE_GUIDED_TEST` (decoy never verified) | yes |
| kd2-conflicting | BLOCKED | SOLVED | `KNOWLEDGE_DIRECTLY_ENABLED_SOLVE` (no false disproof) | yes |
| kd2-noise | BLOCKED | BLOCKED | `NO_KNOWLEDGE` | yes |

Verdict: **KNOWLEDGE-CONTRIBUTING — 2 knowledge-directly-enabled verified solves; all safety
invariants preserved; OFF mode unchanged.** False verifications: 0. False disproofs: 0.
Fabricated target/payload/tool execution attempts: **0**. Alignment/encoding mismatches are
downgraded, not executed.

## 10. Limitations

* Runnable synthesis exists only for `ssti`/`sql-injection` (the web-probe environment); other
  categories translate to hypothesis-only until runnable templates + matching trusted adapters
  exist. This is a grounded capability boundary, not a translator limitation.
* The experimental knowledge path is exercised on the internal solve arm (`solve_experimental`). The
  MCP/Architecture-A path is intentionally left knowledge-OFF (advisory-context wiring for the
  Kiro-driven path is a separate, opt-in step).
* Attribution's strongest label (`DIRECTLY_ENABLED`) requires a paired control; single-run
  attribution stops at `KNOWLEDGE_GUIDED_TEST`.

## 11. Real-challenge readiness

The existing Architecture A MCP path is sufficient to begin solving real challenges; no new
architecture is required. Concretely:

* **Supply a challenge** — operator builds a gateway (`build_operator_gateway(policy, llm_client)`
  for the internal driver, or the default kiro driver needing no model) and calls `ctf_start` with
  intent only: `name`, `category`, `description`, `urls`, `flag_format`, `credentials`, `resources`.
* **Files/resources** — provided as base64 (`content_b64`), validated (path-traversal-safe) and
  materialized into the session workspace by the gateway; the client never supplies a filesystem path.
* **Kiro observes** — `ctf_observe` returns authoritative state (hypotheses, evidence, recent
  observations, available tools, budget) plus the proposal schema.
* **Kiro proposes** — `ctf_propose(hypotheses, actions)`; typed proposals are validated by the frozen
  validators (unregistered tools rejected), then flow to the planner.
* **Execution** — only operator-registered trusted adapters run, via TrustKernel; there is no shell/
  HTTP/subprocess/browser MCP primitive.
* **Evidence / verification** — evidence returns through `ctf_observe`; the kernel's
  VerificationController is authoritative; `ctf_result` reports `VERIFIED_FLAG`.
* **Flag** — `ctf_result.verified_flag` (only on a kernel-verified STOP).
* **Writeup / experience** — the post-terminal observer fires once on success (`ctf_propose` verify)
  or on `close_session` for failures; artifacts are readable via `ctf_writeup` / `ctf_experience`.

Knowledge augmentation fits this as advisory context/proposals and adds NO execution primitive
(smoke confirms the tool set is unchanged at 14 tools).

## 12. Exact MCP invocation workflow

```
# Architecture A (Kiro is the reasoner), knowledge OFF (default):
1. ctf_start {name, category, description, urls, flag_format, resources[content_b64], driver:"kiro"}
2. loop:
     ctf_observe(session_id)            # read authoritative state + proposal schema
     -> Kiro reasons ->
     ctf_propose(session_id, hypotheses=[...], actions=[...])   # typed; validated + planned + executed
   until ctf_result(session_id).result_type == "VERIFIED_FLAG"
3. ctf_writeup(session_id) / ctf_experience(session_id)         # post-terminal learning artifacts
4. close_session(session_id)
```
Experimental knowledge augmentation on the internal arm is invoked programmatically via
`solve_experimental(..., knowledge_mode=KnowledgeMode.EXPERIMENTAL, retriever=...)`; it never
changes the MCP surface.

---

## Final status

* **BASELINE STATUS** — 496 prior tests remain green; OFF mode proven identical to the knowledge-off
  baseline (test 1).
* **EXPERIMENTAL STATUS** — working; EXPERIMENTAL activates translation and bridges control-blocked
  challenges (tests 2–3, 15–17, 19).
* **KNOWLEDGE CONTRIBUTION RESULTS** — 2 `KNOWLEDGE_DIRECTLY_ENABLED_SOLVE`; unused/independent paths
  correctly not credited; attribution is evidence-based.
* **SAFETY RESULTS** — 0 false verifications, 0 false disproofs, 0 fabricated execution attempts;
  historical flag can never become the current flag; conflicts resolved for current evidence;
  knowledge failure falls back safely (test 14).
* **TEST RESULTS** — full suite 516 passed / 0 failed (496 + 20 new); historical 12/12; knowledge-v2,
  DomeCTF, both MCP smokes PASS; frozen fingerprint 45/45 matched, 0 mismatched; external corpora
  unchanged.
* **REAL-CHALLENGE READINESS** — Architecture A MCP path is sufficient (section 11); no new bridge
  required.
* **REMAINING BLOCKERS** — none for this task. To broaden autonomous coverage beyond web SSTI/SQLi,
  add runnable templates + matching operator-registered trusted adapters per category (out of scope
  here).

## What was NOT changed

Frozen `ctf_agent/**` (45/45 unchanged); external corpora and A/B data; the MCP tool surface (14
tools, no execution primitive); default solver semantics (OFF == baseline). No fine-tuning, LoRA,
RL, external API/model, or new phase. Additive edits only: new `knowledge_experiment.py`, new test
file, one backward-compatible injection hook in `knowledge_solver.py`, one `all_templates()` helper
+ exports.
