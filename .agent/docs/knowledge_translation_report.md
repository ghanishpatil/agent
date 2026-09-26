# Generalized Knowledge Translation Layer — Implementation Report

Status: **COMPLETE / GREEN**. Additive to `ctf_experiment` only. Frozen `ctf_agent/**` and all
external corpora are byte-for-byte unchanged. This is a single focused capability — not a new
phase, not fine-tuning, not a solver redesign.

Core principle enforced throughout: **Knowledge may suggest. Evidence must authorize.
Planner / kernel / verification remain authoritative.**

---

## 1. Files added

| File | Purpose |
|------|---------|
| `.agent/src/ctf_experiment/knowledge_translation.py` | The generalized, deterministic, advisory-only translation layer. |
| `.agent/tests/experiment/test_knowledge_translation.py` | 37 tests covering the full checklist + experience translation. |
| `.agent/docs/knowledge_translation_report.md` | This report. |

## 2. Files modified

| File | Change |
|------|--------|
| `.agent/src/ctf_experiment/__init__.py` | Export-only: added the translation public API to `__all__`. No behavior change. |

Nothing else was modified. In particular `knowledge_reasoning.py` (and its `_WEB_TESTS`) is
untouched, byte-for-byte.

## 3. Architecture

The translator lives in `ctf_experiment` (the knowledge-augmentation package that already imports
`ctf_ingest` + `ctf_agent` but is never imported by `ctf_agent`). It converts retrieved knowledge
into the SAME typed proposals the frozen Strategic Brain / reasoning source already emit
(`ctf_agent.proposals.HypothesisSuggestion` and `ActionSuggestion`), so its output flows through
the existing pipeline with no new seam:

```
Retrieved knowledge (KnowledgeRecord)   Agent experience (ExperienceRecord)
                 \                              /
                  \                            /
                   v                          v
              KnowledgeTranslator  (deterministic, advisory-only)
                   |
   TranslationResult(status, mechanism, HypothesisSuggestion,
                     discriminating_test, ActionSuggestion?, provenance, ...)
                   |
        (advisory) Strategic Brain / reasoning source
                   |
             frozen ActionPlanner  ->  TrustKernel  ->  trusted adapters
                   |
                Evidence  ->  Verification  ->  STOP
```

The translator **returns data only**. It has no adapters, no kernel reference, no network, no
subprocess, no clock, no model. Its `ActionSuggestion` output is accepted by the frozen
`validate_action_suggestion`/`validate_hypothesis_suggestion` unchanged (test 32), which is how it
stays planner/kernel-compatible without modifying the solver.

It is **not** wired into `solve_with_knowledge` by default — doing so would alter the verified
459-test baseline. It is a tested, importable capability that produces frozen-compatible proposals.

## 4. Translation data model

* `TranslationResult` — `status`, `mechanism`, `technique_id`, `hypothesis: HypothesisSuggestion?`,
  `discriminating_test` (prose, always present when a mechanism is found), `runnable_action:
  ActionSuggestion?` (present iff `RUNNABLE_TEST`), `provenance`, `applicability`, `support`,
  `evidence_requirements`, `missing_requirements`, `reason`.
* `TranslationStatus` — `RUNNABLE_TEST` | `HYPOTHESIS_ONLY` | `ADVISORY_CONFLICT` | `NOT_APPLICABLE`.
* `Applicability` — `PLAUSIBLE` | `UNRESOLVED` | `DISPROVEN_ELSEWHERE`.
* `KnowledgeOrigin` — `EXTERNAL_WRITEUP` | `AGENT_SUCCESS_EXPERIENCE` | `AGENT_FAILURE_EXPERIENCE`.
* `TranslationProvenance` — origin + `source_id`, `technique_id`, external locators
  (`source_uri`, `document_path`) OR agent locators (`run_id`, `session_id`, `driver`,
  `source_kind`), plus the trajectory step orders that produced the mechanism/hypothesis/test.
* `TranslationContext` — the grounded "evidence must authorize" side: `target_urls`,
  `available_tools`, `verifier_tool`, `known_parameters`, `exact_targets`, `disproven_mechanisms`.
* `MechanismTemplate` / `RunnableSpec` / `TemplateRegistry` — the generalized, data-driven template
  mechanism (replaces a hardcoded technique switch).
* `TrajectoryExtract` / `TranslationSupport` — trajectory reading + audit metadata.

`TranslationResult` carries no timestamp, so identical inputs serialize identically (determinism).

## 5. How trajectory-first translation works

`extract_trajectory()` reads one text (+ order) per reasoning stage directly from the ingested
`ReasoningTrajectory` steps (`CANDIDATE_MECHANISM`, `HYPOTHESIS`, `DISCRIMINATING_TEST`,
`OBSERVATION`, `INTERPRETATION`, `NEXT_ACTION`). For each stage the **lowest-order** step wins;
later differing steps of the same kind are recorded as `conflicts` and never merged; duplicates are
ignored. Translation prefers the trajectory's own prose for human-facing mechanism/hypothesis/test
text and falls back to the matched template. Because knowledge is read as a reasoning sequence
(not `technique -> payload`), a writeup with no reusable payload still yields a mechanism +
hypothesis + a described discriminating test (`HYPOTHESIS_ONLY`).

## 6. How runnable-vs-hypothesis-only is decided

A result is `RUNNABLE_TEST` only when ALL hold:
1. A `MechanismTemplate` matches (by structured `technique_id`, alias, or a whole-token match of the
   trajectory mechanism text) **and** the template has a vetted `RunnableSpec`.
2. Every grounded slot the spec requires is present in `TranslationContext`: a `target_url`, a
   non-verifier `probe_tool`, and (if `param_must_be_grounded`) the parameter appears in
   `known_parameters`.
3. Target/evidence alignment passes (section 7).

Otherwise the result is `HYPOTHESIS_ONLY` (mechanism + hypothesis + described test, `runnable_action
= None`), with `missing_requirements` and a `reason`. A template with no `RunnableSpec` (e.g. JWT,
crypto, RE, forensics, pwn, misc seeds) is always `HYPOTHESIS_ONLY`. If the current evidence already
disproves the mechanism the result is `ADVISORY_CONFLICT`; if no mechanism can be extracted it is
`NOT_APPLICABLE`.

## 7. How target/evidence alignment is enforced

* Runnable targets are built **only** from the grounded `TranslationContext.target_urls[0]`; a
  retrieved target is never used as the base.
* If the retrieved knowledge names an explicit host that differs from the current grounded host, the
  result downgrades to `HYPOTHESIS_ONLY` ("alignment failed").
* Exact-encoding guard: when `exact_targets` are supplied, the synthesized target must **byte-equal**
  one of them. This catches the historical `*` vs `%2A` mismatch — synthesis uses the same
  `urllib.parse.quote` as the existing bridge (so `{{7*7}}` → `%7B%7B7%2A7%7D%7D`); a raw-`*`
  authoritative target does not byte-match and yields `HYPOTHESIS_ONLY`. The translator never
  "fixes" encoding by guessing.

## 8. How provenance is preserved

Every `TranslationResult` carries a `TranslationProvenance` whose `origin` is one of three distinct
`KnowledgeOrigin` values, plus source-specific locators and the trajectory step orders that produced
each element. External locators (`source_uri`, `document_path`) and agent locators (`run_id`,
`session_id`, `driver`, `source_kind`) are separate fields and are never cross-populated (tests
25–27 assert this).

## 9. How external knowledge differs from agent experience

* **External writeup** → `KnowledgeOrigin.EXTERNAL_WRITEUP`; may become `RUNNABLE_TEST` when grounded.
* **Agent success experience** → `AGENT_SUCCESS_EXPERIENCE`; may become `RUNNABLE_TEST` when grounded;
  `applicability = PLAUSIBLE`.
* **Agent failure experience** → `AGENT_FAILURE_EXPERIENCE`; **always `HYPOTHESIS_ONLY`** (a prior
  attempt did not establish the mechanism here). Applicability is `UNRESOLVED` by default — including
  the rate-limit/timeout/network case — and only becomes `DISPROVEN_ELSEWHERE` when the experience
  carries an **authoritative DISPROVEN** hypothesis for that mechanism, and even then it is advisory
  ("reduced applicability in a different context"), never a current disproof. The three origins never
  collapse into one anonymous source.

## 10. Existing SSTI/SQLi compatibility

The `ssti` and `sql-injection` seeded templates reproduce the exact `_WEB_TESTS` behavior. Their
`RunnableSpec` uses the same param/payload/expected-observation constants, and target synthesis is
`f"{base_url}?{param}={quote(payload)}"` — byte-identical to `knowledge_reasoning.py`. A dedicated
test (`test_web_tests_target_construction_is_equivalent`) iterates `_WEB_TESTS` and asserts the
translator produces the same target, expected observation, and hypothesis id for each. `_WEB_TESTS`
itself is left untouched.

## 11. Cross-category tests

`crypto` (Mersenne-Twister PRNG), `reverse` (dynamic analysis), `forensics` (audio steganography),
`pwn` (format string), `misc` (python jail escape) all translate to `HYPOTHESIS_ONLY` with a
mechanism + hypothesis + described discriminating test and no invented payload — demonstrating the
architecture is generalized and not fundamentally web-only. A prose-only crypto trajectory (no
structured technique) is also matched via trajectory text.

## 12. Safety tests

Missing target → hypothesis-only; missing grounded parameter → hypothesis-only; no runnable
synthesis (missing payload) → hypothesis-only; missing probe tool → hypothesis-only; retrieved-host
mismatch → hypothesis-only; URL-encoding (`*` vs `%2A`) mismatch → hypothesis-only; invented expected
observation rejected (runnable action carries only the template constant); invented tool rejected
(tool comes only from grounded `available_tools`). Authority tests confirm the translator never sets
a candidate flag, never exposes a `status`/state transition on hypotheses, never executes, and its
outputs pass the frozen proposal validators while an unregistered tool is still rejected by them.

## 13. Full test results

`python -m pytest` → **496 passed, 0 failed** (459 prior baseline + 37 new translation tests).
The new file alone: 37 passed.

## 14. Historical regression results

`tests/test_historical_regression.py` → PASS (12/12 historical failure regressions; environmental/
tool/auth/network/timeout outcomes never become automatic disproof — the same invariant the
translator applies to failure experiences).

## 15. Knowledge v2 results

`tests/experiment/test_knowledge_dependent.py` + `test_knowledge_integration.py` → PASS (knowledge
attribution + safety invariants intact; the existing `KnowledgeAugmentedReasoningSource` path is
unchanged).

## 16. DomeCTF results

`tests/experiment/test_domectf_eval.py` → PASS. The DomeCTF evaluation artifacts under
`.agent/knowledge/domectf_eval_v1/**` were not regenerated or modified.

## 17. Frozen ctf_agent fingerprint result

`ooc/fpcheck.py` → **manifest files: 45, matched (raw bytes): 45, mismatched: 0, missing: []**.

## 18. External corpus integrity result

Untouched. The translator performs **zero file I/O** (no reads or writes of corpora; it operates on
in-memory `KnowledgeRecord`/`ExperienceRecord` objects passed by the caller). The in-suite
`test_jiaje_ingestion.py` and DomeCTF tests (which assert corpus integrity) pass, and no
`agent_experience_v1` or corpus files were created/modified by this work.

## 19. Limitations discovered

* Only `ssti` and `sql-injection` currently have a vetted `RunnableSpec`, because the only
  executable evaluation environment is the web probe. All other seeded techniques are deliberately
  `HYPOTHESIS_ONLY` — this is a grounded capability boundary, not a translator limitation, and new
  runnable templates can be registered as executable environments appear.
* Host/URL detection for alignment is deterministic and conservative (explicit `http(s)://` tokens);
  knowledge that references a target only in prose without a URL contributes advisory hypotheses
  only, which is the intended safe default.
* The translator is not wired into the live solver composition by default (to preserve the verified
  baseline); integration is a separate, explicitly-approved step.

## 20. Explicit statement of what was NOT changed

* `.agent/src/ctf_agent/**` — frozen, unchanged (45/45 fingerprints matched).
* `knowledge_reasoning.py` / `_WEB_TESTS` — unchanged; equivalence proven by test, not by edit.
* `knowledge_solver.py`, the A/B harnesses, and DomeCTF eval logic/artifacts — unchanged.
* External CTF corpora and A/B evaluation data — unchanged.
* No fine-tuning, no LoRA, no RL, no weight updates, no model/API calls, no new Phase, no solver
  redesign. TrustKernel, verification/evidence/hypothesis-transition semantics, and ActionPlanner
  authority are all untouched and remain the sole authorities.
