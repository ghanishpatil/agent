# Phase 4 Design — Specialist Intelligence Layer

## Scope boundary
Phase 4 adds a **Specialist Intelligence Layer** that advises the Phase 3 Strategic Brain. It does
not modify the Phase 2 Trust Kernel, and it makes exactly **one** small additive change to Phase 3
(`ReasoningLoop._seed_hypotheses`, see below). Specialists are advisors: they only ever produce
typed `SpecialistAnalysis` objects, which the brain converts into the same
`HypothesisSuggestion`/`ActionSuggestion` proposals the Phase 3 planner already validates. No
specialist executes a tool, mutates kernel/evidence/hypothesis state, or verifies a flag.

## Where specialists sit
```
ChallengeContext (Phase 3, live view over kernel snapshot + board)
      |
SpecialistSelector  -- picks the relevant subset (not all 5 every time)
      |
[WebSpecialist, CryptoSpecialist, ReverseSpecialist, ForensicsSpecialist, PwnSpecialist]
      |  each: analyze(SpecialistContext) -> SpecialistAnalysis   (advisory, typed, no side effects)
      |
SpecialistReasoningSource (the "Strategic Brain" mediation layer; implements Phase 3 ReasoningSource)
      |  conflict resolution + dedup + convert analyses -> validated *Suggestion objects
      |
ReasoningLoop (Phase 3, UNCHANGED except one additive _seed_hypotheses call)
      |
ActionPlanner (Phase 3, unchanged) -> validate + dedup + cheapest-discriminating-test-first
      |
AdapterRegistry (Phase 3, unchanged) -> ExecutionResult
      |
TrustKernel.process() (Phase 2, unchanged) -> classify -> evidence -> impact -> verify -> STOP
```

The `SpecialistReasoningSource` **is** how the brain consults specialists: it implements the exact
`ReasoningSource` Protocol the Phase 3 loop already accepts, so it drops in as the loop's
`reasoning_source` with no other loop wiring. Existing `ScriptedReasoningSource` remains valid and
all Phase 3 scenarios keep using it.

## Why this preserves every invariant
- **Specialists cannot execute:** a specialist's `CandidateAction` is inert data. Only
  `ReasoningLoop._execute_one` calls `AdapterRegistry.execute`, and only after the planner has
  validated and de-duplicated the corresponding `ActionSuggestion`.
- **Specialists cannot verify:** a `CandidateAction.candidate_flag` is a *proposal* of a value to
  try. The loop still forwards it through `kernel.process(candidate=...)`, and the Phase 2
  `VerificationController` independently decides acceptance from real bound evidence. A specialist
  naming a wrong flag degrades to "run as a normal probe" (Phase 3's `_evidence_is_bound_to` guard).
- **Specialists cannot mutate hypotheses:** the brain converts a `SpecialistHypothesis` into a
  `HypothesisSuggestion`, which the loop seeds via the authoritative `board.propose_hypothesis`
  (creates `OPEN` only). Terminal status only ever comes from `apply_evidence` via `kernel.process`.
- **Specialists cannot bypass dedup/anti-spray/prerequisites:** their actions become
  `ActionSuggestion`s that flow through `validate_action_suggestion` + the planner's fingerprint
  dedup + prerequisite gating, identical to any other suggestion.
- **Memory stays advisory:** specialists read `AdvisoryMemory` (Phase 3) for priors and surface
  them as `relevant_memory_refs` strings. There is no path from a memory match to kernel state.
- **Current evidence outranks specialist confidence:** specialists read live evidence from the
  `ChallengeContext` and annotate mechanism `FactState` from it; but the authoritative ranking of
  what to do next is still the planner's cheapest-discriminating-test-first over validated
  suggestions, and the authoritative truth is still the kernel's evidence, never the specialist's
  `confidence` field.

## Module layout (`.agent/src/ctf_agent/specialists/`)
```
__init__.py       exports
base.py           SpecialistContext, CandidateMechanism, SpecialistHypothesis, RecommendedTest,
                  CandidateAction, SpecialistAnalysis, Specialist (Protocol), SpecialistError,
                  validate_specialist_analysis(), analysis_to_suggestions(), evidence/flag helpers
web.py            WebSpecialist
crypto.py         CryptoSpecialist
reverse.py        ReverseSpecialist
forensics.py      ForensicsSpecialist
pwn.py            PwnSpecialist
selection.py      SpecialistSelector (relevance-based subset selection)
registry.py       SpecialistRegistry (holds specialists, exposes select+analyze)
brain.py          SpecialistReasoningSource (ReasoningSource impl; mediation + conflict resolution)
metrics.py        SpecialistRunMetrics, evaluate_specialist_run, SpecialistAggregateMetrics
```

## A. Specialist contract (`base.py`)
`analyze(context: SpecialistContext) -> SpecialistAnalysis`. Strongly typed; free text lives only
in `reasoning_summary`/`uncertainty`, never as the sole carrier of actionable data.

- `SpecialistContext(challenge: ChallengeContext, available_tools: Tuple[str,...], memory=None)` —
  the read-only "ContextSnapshot" a specialist sees. Convenience: `current_evidence()`,
  `observation_texts()`, `hypothesis_state(id)`, `flag_format`.
- `CandidateMechanism(name, description, fact_state: FactState, rationale, supporting_evidence_ids,
  conflicting_evidence_ids)` — every mechanism carries an evidence-derived `FactState`; a mechanism
  with no current evidence is `PLAUSIBLE`, never asserted true.
- `SpecialistHypothesis(hypothesis_id, statement, mechanism, technique, fact_state,
  supporting_evidence_ids, conflicting_evidence_ids)`.
- `RecommendedTest(objective, description, expected_supporting_observation,
  expected_contradicting_observation, blocked_by_failures)` — `blocked_by_failures` names the
  result classes (RATE_LIMIT/TIMEOUT/…) that would merely block, never disprove.
- `CandidateAction(hypothesis_id, objective, tool, target, input_data, relevant_parameters,
  prerequisites, expected_observation, estimated_cost, candidate_flag, reasoning)`.
- `SpecialistAnalysis(specialist, category, relevance, observations, candidate_mechanisms,
  hypotheses, supporting_evidence_refs, conflicting_evidence_refs, recommended_tests,
  candidate_actions, required_tools, prerequisites, expected_observations, confidence,
  reasoning_summary, uncertainty, applicable_techniques, relevant_memory_refs)`.

`validate_specialist_analysis(analysis, adapters=None)` enforces structure and refuses any
forbidden-phrase state assertion (reusing Phase 3's `_FORBIDDEN_PHRASES`), any candidate action
naming an empty tool/objective, etc. `analysis_to_suggestions(analysis)` returns
`(hypotheses: Tuple[HypothesisSuggestion,...], actions: Tuple[ActionSuggestion,...])` — the only
bridge from specialist output into the Phase 3 proposal world.

## B. Evidence-aware, mechanism-first reasoning
Each specialist:
1. Reads indicators from `challenge.metadata` (category/description/hints/files/urls/flag_format)
   **and** from current evidence observation bodies (`SpecialistContext.observation_texts()`).
2. Enumerates candidate mechanisms only for indicators actually present (no blanket category dump).
3. For each mechanism, emits a `SpecialistHypothesis` with a `FactState` derived from evidence:
   `PLAUSIBLE` with no evidence; leans on `HypothesisView.state` once the board reflects kernel
   evidence.
4. Recommends the cheapest discriminating test and a corresponding `CandidateAction`.
5. **Failure intelligence:** if current evidence for a mechanism's test is RATE_LIMIT / TIMEOUT /
   NETWORK_FAILURE / TOOL_FAILURE / ENVIRONMENT_FAILURE / AUTH(Z)_FAILURE, the specialist marks the
   mechanism `BLOCKED`/`UNRESOLVED` (never `DISPROVEN`) and recommends an alternative test or
   backoff. Since specialists can't set status anyway, this governs their `fact_state` annotation
   and recommendation text.
6. **Flag derivation:** if an authoritative observation body already contains a flag-format token,
   the specialist proposes a submit `CandidateAction` (candidate_flag=extracted token, reusing the
   observation's own tool+source) — evidence-derived, not foreknowledge.

## C. Selection (`selection.py`) and conflict resolution (`brain.py`)
`SpecialistSelector.select(context, available_tools)` scores each specialist's `relevance(context)`
(category match is primary; indicator keywords in description/hints/filenames are secondary, e.g.
`jwt`→crypto in addition to web) and returns only those above a threshold — so a pure web challenge
invokes Web (plus Crypto only if a crypto indicator like `jwt` appears), never all five.

`SpecialistReasoningSource` runs the selected specialists, then resolves conflicts **not** by
picking the highest-confidence specialist, but by handing every non-duplicate proposal to the
Phase 3 planner, which ranks by cheapest-discriminating-test-first over the current evidence. The
brain only de-duplicates identical hypotheses/actions and orders by (mechanism evidence state, then
specialist relevance, then lower cost) as a tie-break hint; the planner remains the authority on
what actually runs.

## D. Memory integration
Shared `AdvisoryMemory` (Phase 3), queried by each specialist with its own category + mechanism
keywords. Results surface as advisory `relevant_memory_refs` and may nudge mechanism ordering, but
never create hypotheses/evidence and never outrank current evidence (structural: the brain only
passes validated suggestions to the planner; memory matches are strings on the analysis).

## E. The one additive Phase 3 change
`ReasoningLoop` gains `_seed_hypotheses(context)`, called once per iteration before planning: it
takes `reasoning_source.suggest_hypotheses(context)`, validates each via
`validate_hypothesis_suggestion`, skips ids already on the board, and seeds the rest via
`board.propose_hypothesis` (OPEN only), journaling a new `JournalEventKind.HYPOTHESIS_PROPOSED`.
This is additive and backward-compatible: `ScriptedReasoningSource.suggest_hypotheses` returns `()`
by default, so every existing Phase 3 test and scenario is unaffected. No other loop behavior
changes.

## F. Testing
- `tests/specialists/` — contract, relevance/selection, evidence reasoning (incl. failure not
  becoming disproof, ambiguous staying unresolved, current evidence over memory), planner
  integration (proposal enters planner, dedup/prereq/cost respected), verification boundary
  (specialist cannot verify / cannot create trusted evidence / candidate still passes Phase 2
  verification / verified→STOP), conflict handling (two specialists disagree, brain resolves via
  planner/evidence).
- `tests/specialists/scenarios/` — 5 deterministic end-to-end runs (web/crypto/reverse/forensics/
  pwn) through the real `ReasoningLoop`, each with initial ambiguity, at least one wrong path, and
  at least some deliberately producing tool/environment failure, ambiguous evidence, conflicting
  hypotheses, or duplicate-action attempts.

## G. Non-goals (per phase4.md section 20)
No autonomous specialist agents, no specialist execution engines, no swarm/RL/fine-tuning, no
vector DB, no new third-party dependency, no redesign of Phase 2/3, no implementation of every CTF
category (exactly the 5 named specialists), and Phase 5 is not started.
