# Phase 4 Report — Specialist Intelligence Layer

Status: **complete for the scope defined in `phase4.md`.** Per section 25, Phase 5 was not started
and no full autonomous solver was built. This report is honest about what works, what is
scenario-configured, and what is not yet demonstrated.

## 1. Specialists implemented

Exactly the five named in the spec, no more:

| Specialist | Category | File | Mechanisms it reasons about |
|---|---|---|---|
| Web | `web` | `specialists/web.py` | SQLi, SSTI, command injection, SSRF, LFI/traversal; notes JWT as a cross-domain crypto hand-off |
| Crypto | `crypto` | `specialists/crypto.py` | base64/encoding, single-byte XOR, RSA weakness, classical cipher, JWT signature/alg-confusion |
| Reverse | `reverse` (corpus `rev`) | `specialists/reverse.py` | embedded strings/constants, reversible encoding transform, hidden comparison/keycheck |
| Forensics | `forensics` | `specialists/forensics.py` | appended trailer/carved payload, EXIF/metadata, plaintext strings, LSB stego |
| Pwn | `pwn` | `specialists/pwn.py` | stack overflow, format string, heap corruption (UAF/double-free) |

Cloud/mobile/IoT/OSINT/stego-as-its-own-specialist were deliberately **not** built (stego indicators
route to the forensics specialist).

## 2. Specialist contract

`Specialist` is a `Protocol` with `name`, `category`, `relevance(SpecialistContext) -> float`, and
`analyze(SpecialistContext) -> SpecialistAnalysis`. `SpecialistContext` is a read-only wrapper over
the Phase 3 `ChallengeContext` plus `available_tools` and an optional advisory memory. Output is the
strongly-typed `SpecialistAnalysis` (specialist, category, relevance, observations,
`candidate_mechanisms`, `hypotheses`, supporting/conflicting evidence refs, `recommended_tests`,
`candidate_actions`, required tools, prerequisites, expected observations, confidence,
`reasoning_summary`, `uncertainty`, `applicable_techniques`, `relevant_memory_refs`). Free text
exists only in `reasoning_summary`/`uncertainty`; every actionable item is a typed dataclass
(`CandidateMechanism`, `SpecialistHypothesis`, `RecommendedTest`, `CandidateAction`).
`validate_specialist_analysis` enforces structure and rejects: forbidden state-assertion phrases
(reusing Phase 3's `_FORBIDDEN_PHRASES`), hypotheses proposed in terminal state (DISPROVEN/VERIFIED),
empty required fields, out-of-range relevance/confidence, and invalid `FactState` values.

## 3. Specialist selection

`SpecialistSelector` selects a specialist if it is the challenge's exact category match, or its
relevance clears a deliberately high cross-domain bar (0.45). Relevance is `0.6` for category match
plus up to `0.4` for indicator-keyword hits. The high cross-domain bar prevents generic keyword
overlap (e.g. a crypto challenge saying "xor"/"key", which are also reverse-ish words) from dragging
in an off-domain specialist; only a strong, specific signal (JWT for crypto; an ELF binary for
reverse/pwn) crosses it. Verified by `test_selection.py` (web→web; web+JWT→web+crypto; pure
crypto→crypto only, not reverse/pwn/forensics; rev→reverse via category mapping).

## 4. Specialist-to-brain interface

`SpecialistReasoningSource` (`specialists/brain.py`) is the Strategic Brain's consulting layer. It
implements the **exact Phase 3 `ReasoningSource` Protocol**, so it drops into `ReasoningLoop` as the
`reasoning_source` with no other wiring. Each cycle it selects specialists, runs their `analyze`,
validates each analysis (dropping any that violate structure/authority), converts survivors via
`analysis_to_suggestions` into Phase 3 `HypothesisSuggestion`/`ActionSuggestion` objects,
de-duplicates, and orders them (submit-first, then evidence-state, relevance, cost) as a tie-break
hint. It exposes `last_selection`/`last_analyses` for tests and metrics. It never executes, mutates
kernel state, or verifies.

## 5. Knowledge sources

Specialists reason from: challenge metadata (name/category/description/hints/files/urls/flag_format),
**current evidence observation bodies** (so reasoning is evidence-driven, not description-only), and
the Phase 1 corpus via the Phase 3 `AdvisoryMemory` (`.agent_audit/knowledge`, `/tools`,
`/trajectories`, `/failures`). Corpus knowledge is surfaced as advisory `relevant_memory_refs`
strings (technique/tool/trajectory/failure ids), used as priors for explanation/ordering — never as
truth. Historical knowledge generalizes (mechanism→indicator→discriminating test→interpretation),
and no challenge-specific flag is copied from the corpus.

## 6. Memory integration

Shared, not per-specialist: one `AdvisoryMemory` queried by each specialist with its own category +
mechanism keywords. Priority (current evidence > current observations > challenge-specific verified
experience > general techniques > historical priors > plausible knowledge) is **structural**:
`AdvisoryMemory` has no method that can write kernel evidence or call `board.record`, so memory can
never outrank current evidence. Verified by `test_evidence_reasoning.py`
(`test_historical_memory_does_not_override_absence_of_current_evidence`: memory contributes refs but
every mechanism stays PLAUSIBLE with no current evidence).

## 7. Evidence handling & 8. Failure handling

Each mechanism carries a `FactState` read live from the board (`current_hypothesis_state`), not an
invented one. A mechanism with no current evidence is `PLAUSIBLE`. Crucially, the failure result
classes (RATE_LIMIT / TIMEOUT / NETWORK_FAILURE / TOOL_FAILURE / ENVIRONMENT_FAILURE / AUTH(Z) /
INPUT_REJECTION — `NON_DISPROVING_RESULT_CLASSES`) are annotated as `BLOCKED`/`UNRESOLVED` and never
as disproof; the specialist explicitly says the *test* was blocked. Once the kernel actually
DISPROVES a mechanism (via a registered discriminating test + authoritative contradiction), the
specialist stops re-proposing it (anti-spray). Verified end-to-end by
`test_scenario_failure_modes.py` (a crashing tool never disproves any hypothesis; ambiguous output
stays UNRESOLVED) and at unit level by `test_evidence_reasoning.py`.

## 9. Cross-domain handling & 10. Conflict resolution

Specialists never talk to each other; the brain mediates. A web+JWT challenge selects both web and
crypto, each proposing competing hypotheses. The brain does **not** pick the highest-confidence
specialist — it emits all non-duplicate proposals and lets the Phase 3 planner rank by
cheapest-discriminating-test-first over current evidence, so **current evidence outranks specialist
confidence**. Verified by `test_conflict.py`.

## 11. Planner integration

Specialist actions become ordinary `ActionSuggestion`s that flow through the unchanged Phase 3
planner: `validate_action_suggestion` (registered tool, non-empty fields, no forbidden phrases),
fingerprint dedup, prerequisite gating, cheapest-discriminating-test-first ranking. Verified by
`test_planner_integration.py`: a valid specialist action becomes a proposal; an unregistered-tool
action is rejected; a duplicate in the same state is blocked; an unmet-prerequisite action is
blocked (`blocked_only_by_prerequisites`).

## 12. Security boundaries

Specialists cannot execute (only `ReasoningLoop._execute_one` calls `AdapterRegistry.execute`),
cannot verify (a `CandidateAction.candidate_flag` is only a value-to-try; the Phase 2
`VerificationController` decides), and cannot mutate hypotheses/evidence (seeding goes through the
authoritative `board.propose_hypothesis`, OPEN only). Architecturally verified by
`test_verification_boundary.py`: no specialist module references `TrustKernel`/`EvidenceManager`/
`VerificationController`/`kernel.process` in source; analysis objects have no `verify`/`commit`/
`record_evidence`/`mark_verified` method; a `candidate_flag` submission is a plain `ActionSuggestion`
with no verification field.

## 13. The one additive Phase 3 change

`ReasoningLoop._seed_hypotheses(context)` (called once per iteration before planning) validates
`reasoning_source.suggest_hypotheses(context)` and seeds new ids via the authoritative
`board.propose_hypothesis`, journaling a new `JournalEventKind.HYPOTHESIS_PROPOSED`. It is
backward-compatible: `ScriptedReasoningSource.suggest_hypotheses` returns `()`, so all pre-existing
Phase 3 tests/scenarios are unaffected (re-verified: Phase 3's 95 tests still pass unchanged). No
Phase 2 file was modified.

## 14. Tests

**216 tests pass** (0 failures): 74 Phase 2 + 95 Phase 3 (both unchanged) + **47 Phase 4**.
Phase 4 breakdown:
- Unit (37): `test_contract.py` (11), `test_selection.py` (8), `test_evidence_reasoning.py` (7),
  `test_planner_integration.py` (4), `test_conflict.py` (4), `test_verification_boundary.py` (3).
- Scenario/metrics (10): 5 domain end-to-end (1 each) + `test_scenario_failure_modes.py` (3) +
  `test_specialist_metrics.py` (2).

## 15. Synthetic CTF scenarios

Five deterministic, local/synthetic end-to-end scenarios, each driven by a real `SpecialistReasoning
Source` through the real `ReasoningLoop` → planner → adapter → Phase 2 kernel, each with initial
ambiguity and a plausible wrong path that is disproven by real evidence before the right mechanism
wins and the observed flag is submitted and kernel-verified:

- **Web** (`test_scenario_web_specialist.py`): local HTTP server; command-injection probed first
  (wrong, DISPROVEN), SQLi SUPPORTED, flag submitted, VERIFIED.
- **Crypto** (`test_scenario_crypto_specialist.py`): base64 DISPROVEN, XOR SUPPORTED, VERIFIED.
- **Reverse** (`test_scenario_reverse_specialist.py`): keycheck DISPROVEN (opaque), static strings
  SUPPORTED, VERIFIED.
- **Forensics** (`test_scenario_forensics_specialist.py`): EXIF DISPROVEN, appended trailer
  SUPPORTED, VERIFIED.
- **Pwn** (`test_scenario_pwn_specialist.py`): format-string DISPROVEN, stack overflow SUPPORTED via
  a controlled harness (never direct target execution), VERIFIED.

Plus `test_scenario_failure_modes.py`: tool-failure-never-disproof, duplicate-actions-blocked, and
ambiguous-evidence-stays-unresolved, all end-to-end.

## 16. Evaluation metrics and results

`specialists/metrics.py` computes section-18 metrics from run data (hypothesis-id prefixes attribute
work to specialists): verified, actions-to-solution, useful-hypothesis rate, disproven count,
duplicate/unnecessary action rates, discriminating-tests-run, recovered-from-wrong-path,
unnecessary-specialist-invocations, and false-disproof/false-verification (which require external
ground truth). Aggregated across the 5 domain scenarios (`test_specialist_metrics.py`):

| Metric | Result |
|---|---|
| Successful termination rate | 100% (5/5) |
| False verification rate | 0.0 |
| False disproof rate | 0.0 |
| Recovered-from-wrong-path rate | ≥ 0.8 (4–5 of 5 exercised a disproven wrong path) |
| Average actions-to-solution | small, bounded (3 per solved scenario) |

## 17. Final validation (phase4.md section 23)

1–6. All tests + Phase 3 scenarios + specialist scenarios pass (216 total). ✅
3. Historical regressions: **12/12** (run standalone outside pytest). ✅
7. `python -m compileall src tests`: exit 0. ✅
8. Static audit = compileall + JSONL parse (same definition Phase 2/3 used; no separate AST tool
   exists). ✅
9. Phase 2 Trust Kernel unchanged (no Phase 2 file modified; only `journal.py` enum + `loop.py`
   `_seed_hypotheses` among pre-existing files). ✅
10. Phase 3 core behavior valid (95/95 unchanged). ✅
11–14. Specialists cannot bypass kernel / verify / mutate evidence / execute — verified by
   `test_verification_boundary.py` + planner-integration tests. ✅
15. `.agent_audit/` (15 files), `.kiro/` (8), `writeups/` (32) byte-for-byte unchanged by SHA-256
   before/after; `.agent/runtime/` never created; no writes outside `.agent/` except `.pytest_cache`.
   ✅

## 18. Limitations and known gaps (honest)

1. **Specialists are deterministic rule-based analyzers, not an LLM.** They match indicators to a
   fixed mechanism table and build probes; they do not do open-ended reasoning. This is intentional
   (zero-dependency, deterministic tests) but means "specialist expertise" here is curated heuristics
   plus evidence-awareness, not emergent understanding.
2. **Scenario success is partly scenario-configured.** Each scenario registers the exact tools the
   specialist proposes and a `TestSpecification` that maps the tool's output markers to
   supports/contradicts. The specialist genuinely drives selection, mechanism choice, wrong-path
   recovery, flag extraction, and submission — but the tool's semantics and the authoritative
   discriminating test are provided by the scenario, not discovered. A real target would require a
   real tool and a real oracle.
3. **Wrong-path ordering relies on objective-string tie-breaking.** When two mechanisms have equal
   planner score, the brain's stable ordering (ultimately alphabetical by objective) decides which is
   tried first. The scenarios are arranged so the "wrong" mechanism sorts first; this is deterministic
   but is a weaker guarantee than a genuine cost/information-gain model would give.
4. **Flag derivation assumes the flag appears verbatim in authoritative tool output.**
   `extract_flag_candidates` scans observation bodies for a flag-format token. Challenges where the
   flag must be assembled/derived across steps are not handled by the current submit logic.
5. **Memory is consulted but its influence is shallow.** Specialists surface `relevant_memory_refs`
   and could use them to order mechanisms, but current ordering is dominated by evidence state and
   the planner; no scenario demonstrates memory *changing* a decision.
6. **`unsupported-action rate` and `specialist relevance accuracy` from section 18 are only partially
   realized.** Unsupported actions are rejected by the planner (not separately counted post-hoc), and
   relevance accuracy needs a labeled expected-relevant set that only the selection unit tests supply.
7. **No adversarial/false-verification scenario exists.** All false-rate metrics are structurally 0
   because no scenario constructs a plausible-but-wrong flag that the kernel might wrongly accept —
   the Phase 2 verification boundary makes that hard to construct, but it also means the 0.0
   false-verification rate is "no counterexample found", not "proven impossible".

## 19. Deviations from this specification

1. **Specialists reflect the board's DISPROVEN state by skipping a mechanism rather than reporting a
   DISPROVEN hypothesis.** `validate_specialist_analysis` rejects terminal-state hypotheses (to stop a
   specialist asserting disproof); to avoid a false conflict when the *kernel* already disproved a
   branch, specialists simply stop proposing that mechanism and note it in observations. This was a
   real bug found during scenario bring-up, fixed cleanly.
2. **`build_submit_actions` resolves a `(tool, target)` collision** (two mechanisms probing the same
   file with the same tool, differing only by mode) by attaching the submit to the SUPPORTED
   hypothesis's probe and never to a DISPROVEN branch — a real correctness fix, not in the original
   design.
3. **The generic tool builder falls back to the specialist's canonical tool name** (which the planner
   then rejects if unregistered) rather than hijacking an unrelated available tool — a real isolation
   fix found when the reverse specialist grabbed the crypto scenario's `decode_tool`.
4. **Cross-domain selection threshold raised to 0.45** (+ category-match-always, + a crypto JWT
   relevance bump) to stop generic keyword overlap from over-selecting specialists.
5. No new third-party dependency; stdlib only. No Phase 2/3 redesign. No autonomous specialist
   agents, execution engines, swarm, RL, fine-tuning, vector DB, or UI (section 20 respected).

## 20. Exact recommendation for Phase 5

If Phase 5 proceeds, in priority order:
1. **Replace one specialist's rule table with a real LLM behind the same `Specialist` contract**,
   keeping `validate_specialist_analysis` + the planner/kernel boundary unchanged — this is the
   designed extension point and would test whether the boundary holds against non-deterministic
   output.
2. **Add a scenario with a real analysis tool and a real oracle** (e.g. an actual local `sqlite`
   endpoint, or `strings`/`binwalk` on a real file) so mechanism semantics and the discriminating
   test are *discovered*, not scenario-provided — directly addressing limitations #2 and #4.
3. **Construct an adversarial false-verification scenario** (a plausible-but-wrong candidate) to turn
   the 0.0 false-verification metric from "no counterexample" into a tested guarantee.
4. **Give the planner a real information-gain/cost model** so wrong-path ordering no longer depends on
   objective-string tie-breaking (limitation #3).
5. Only after 1–4 should additional specialist categories or any move toward a full autonomous solver
   be considered — and always as advisors behind the unchanged Trust Kernel.

## 21. Final stop

Phase 4 implementation, integration, testing (216 pass), regression validation (12/12), static
validation (compileall clean), evaluation, and documentation are complete. **Phase 5 has not been
started. No full autonomous solver was built.** Stopping here.
