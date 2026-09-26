# Phase 3 Design — Strategic Brain + Trusted Execution

## Scope boundary
Phase 3 adds the first controlled reasoning/execution loop **on top of** the Phase 2 `TrustKernel`.
Phase 2 is not modified. Every state transition (evidence creation, hypothesis update, verification,
STOP) still passes through `TrustKernel.process()`. Phase 3 components only ever *propose* — they
build typed `Action`/`ExecutionResult`/`TestSpecification` objects and hand them to the kernel; none of
them can set `Hypothesis.status`, `Evidence`, or `FlagCandidate.verification_status` directly.

## Module layout (`.agent/src/ctf_agent/`)
```
adapters/
  base.py          ToolAdapter protocol + AdapterRegistry (explicit allow-list)
  subprocess_adapter.py   local subprocess execution -> ExecutionResult
  http_adapter.py         urllib-based HTTP calls -> ExecutionResult
  file_adapter.py         local read-only file inspection -> ExecutionResult
context.py          ChallengeContext: KNOWN/SUPPORTED/PLAUSIBLE/UNRESOLVED/BLOCKED/DISPROVEN/VERIFIED view
hypothesis_engine.py HypothesisBoard: tracks Hypothesis objects, only mutates via kernel PipelineResult
planner.py           ActionProposal, propose_actions(), rank_by_cheapest_discriminating_test()
proposals.py          Typed LLM-facing proposal objects + validate_proposal() (the LLM boundary)
journal.py            append-only JSONL under .agent/runtime/, never touches .agent_audit/
memory_retrieval.py   advisory retrieval over .agent_audit/{knowledge,tools,trajectories,failures}
loop.py               ReasoningLoop: orchestrates context -> planner -> adapter -> kernel -> verify
metrics.py            EvaluationMetrics: counters over a completed run
```

## Non-negotiable rule (re-stated as code shape)
`ReasoningLoop` never calls `Evidence(...)`, `Hypothesis(status=...)`, or sets
`FlagCandidate.verification_status`. It only calls:
- `adapter.execute(action) -> ExecutionResult` (Trusted Tool Adapter)
- `kernel.register_test(action, spec)` (before execution, to make disproof possible)
- `kernel.process(action=..., execution=..., hypothesis=..., ...)` (the only mutation point)

Every other Phase 3 module operates on **copies/read views** of kernel state
(`kernel.snapshot()`, `PipelineResult`), never on private kernel fields.

## A. Trusted Tool Adapter
`ToolAdapter` protocol: `name: str`, `execute(action: Action) -> ExecutionResult`.
Three adapters, each honest about failure structure:
- `SubprocessAdapter` — runs an explicitly allow-listed local executable/script with a timeout;
  captures exit_code/stdout/stderr/timed_out/tool_available (checked via `shutil.which` first).
- `HttpAdapter` — `urllib.request` GET/POST against an allow-listed host prefix; captures
  http_status/response_body/response_headers/network_state/timed_out; never follows redirects to
  non-allow-listed hosts.
- `FileAdapter` — reads a file under an explicitly allow-listed root directory; captures
  exit_code(0/1)/stdout(content)/tool_available(exists).
`AdapterRegistry` maps `Action.tool -> ToolAdapter` and raises if a tool is not explicitly registered
(never a bare `subprocess.run(user_string)` / arbitrary URL / arbitrary path).

## B. Context Model
`ChallengeContext` is a thin read-model built from `KernelSnapshot` plus static challenge metadata
(name/category/points/solves/description/hints/flag_format/files/urls). It classifies each hypothesis
into one of the 7 states by reading `Hypothesis.status` + evidence strength — it does not store its own
truth. `ContextFact` distinguishes `KNOWN` (a static challenge fact) from evidence-backed states.
Current evidence (from `kernel.evidence.records`, `Freshness.CURRENT`) always outranks any advisory
memory match when the two disagree about which technique is likely.

## C. Hypothesis Engine (wrapper, not a second authority)
`HypothesisBoard` is a dict of `hypothesis_id -> Hypothesis` **mirrored from** `PipelineResult.hypothesis`
after every `kernel.process()` call — it is a cache, not a parallel state machine. It also stores the
Phase-3-only advisory fields the spec asks for (`mechanism`, `technique`, `discriminating_tests`,
`priority`) in a *separate* `HypothesisMeta` dataclass keyed by the same id, so Phase 2's `Hypothesis`
dataclass is never subclassed or monkey-patched. `propose_hypothesis()` lets the planner/LLM add a new
`HypothesisMeta` + an initial `Hypothesis(status=OPEN)`; it cannot set status to DISPROVEN/SUPPORTED/VERIFIED
directly — importing `HypothesisStatus.DISPROVEN` outside of `ctf_agent.hypothesis`/`kernel` output is
rejected by a runtime assertion in `HypothesisBoard.record()`.

## D. Action Planner
`ActionProposal` (objective, tool, target, input_data, relevant_parameters, prerequisites,
hypothesis_id, expected_observation, cost_hint 1..5, reversible: bool).
`propose_actions(context) -> list[ActionProposal]` — pulls candidate actions from:
1. registered `TestSpecification` gaps (an unresolved hypothesis with no test yet run in this state)
2. advisory memory matches (technique `cheap_tests`/`discriminating_tests` fields)
`rank(proposals, context)` sorts by a simple heuristic score, NOT a utility integral:
`score = information_gain_bucket - cost_hint`, where `information_gain_bucket` is 3 if the action
discriminates >=2 open hypotheses, 2 if it tests exactly one open hypothesis, 1 otherwise; ties broken
by `cost_hint` ascending then reversibility. Before returning a proposal the planner calls
`fingerprint_action`-equivalent dedup check against `context.completed_fingerprints` and drops:
- exact duplicates in unchanged state
- proposals with unmet prerequisites
- proposals targeting an already-DISPROVEN hypothesis with no new test angle
- any proposal once `context.verification_decision is ControlDecision.STOP`

## E. LLM Reasoning Boundary
`proposals.py` defines `HypothesisSuggestion`, `ActionSuggestion`, `InterpretationNote` — plain frozen
dataclasses an LLM (or a human, or a static analyzer) can emit. `validate_proposal()` converts each
into the internal typed object (`Hypothesis`/`ActionProposal`) **only if** it passes deterministic
checks (non-empty statement/objective, tool is in `AdapterRegistry`, no forbidden verbs like "assume
verified"/"mark disproven" in free text — rejected outright). There is no code path from an
`LLMxSuggestion` to `Evidence`/`FlagCandidate.verification_status`/`HypothesisStatus`; those fields are
only ever produced by `kernel.process()`. Phase 3 ships a `NullLLM`/`ScriptedLLM` test double (returns a
fixed list of suggestions) — no real network LLM call, to keep zero third-party dependencies and
determinism; a real LLM would slot in later behind the same `Suggestion` boundary.

## F. Persistent State Journal
`RuntimeJournal(path)` under `.agent/runtime/<run_id>.jsonl`. `append(event: JournalEvent)` writes one
JSON line (sorted keys) using `os.open(..., O_APPEND | O_CREAT)` + a per-process `threading.Lock` for
atomic single-writer append (documented as single-process; multi-process locking is out of scope,
matching `FailureMemory.append`'s existing local-only pattern). It refuses (raises `ValueError`) any
path whose parts contain `.agent_audit`. Event kinds: `action_proposed`, `action_executed`,
`result_classified`, `evidence_recorded`, `hypothesis_transitioned`, `verification_attempted`,
`control_decision`, `state_changed`.

## G. Memory Retrieval
`AdvisoryMemory` loads (once, lazily) the three read-only `.agent_audit` JSONL stores it needs
(`knowledge/technique_memory.jsonl`, `tools/tool_memory.jsonl`, `trajectories/trajectories.jsonl`) plus
reuses Phase 2's `FailureMemory` for failures. `retrieve(context) -> AdvisoryBundle` does keyword/category
matching only (no embeddings) and every result carries `advisory_only=True` + `source`. Priority order
enforced structurally: `AdvisoryBundle` is only ever consulted by the planner to *rank or seed*
proposals — it is never given a path to write into `kernel.evidence` or `HypothesisBoard.record()`, so
"current evidence > memory" is a structural guarantee, not a runtime check to remember.

## H. Reasoning Loop
`ReasoningLoop.run(max_actions: int) -> LoopResult` implements the 16-step loop from the spec, calling
`kernel.process()` each iteration and stopping when: `decision is ControlDecision.STOP` (verified),
no proposals remain (`BLOCKED`), or `max_actions` exhausted (`BUDGET_EXHAUSTED`). It never resets
`HypothesisBoard`/`journal`/`context.completed_fingerprints` between iterations — state persists across
the whole run object.

## I. Stop conditions
`LoopOutcome` enum: `VERIFIED`, `BLOCKED_NO_ACTIONS`, `BUDGET_EXHAUSTED`, `BLOCKED_PREREQUISITES`.
There is deliberately **no** `IMPOSSIBLE` outcome — a tool/env/auth/network failure only ever produces
`UNRESOLVES`/`BLOCKS_TEST` on the specific hypothesis (per Phase 2), and the loop just closes that one
branch (marks it low-value in `HypothesisMeta.priority = 0`) and moves to the next proposal.

## Anti-loop / anti-spray (module: planner.py + loop.py)
The planner's dedup check (D) plus the kernel's own `ActionRegistry`/`FlagAttemptRegistry` are the two
enforcement points. The loop additionally tracks `attempts_per_hypothesis` and refuses to keep
re-proposing tests against a hypothesis whose last N results were all `UNRESOLVES`/`BLOCKS_TEST` with no
state change — it lowers that hypothesis's `HypothesisMeta.priority` (closes the branch) rather than
declaring the whole run impossible.

## J. Evaluation Metrics
`metrics.py` derives everything from a `LoopResult`'s own `pipeline_results` tuple — never from
separately-kept ad hoc counters. `evaluate_single_run(result) -> SingleRunMetrics` computes:
duplicate-action count/rate (`ControlDecision.DUPLICATE` results), unnecessary-action count/rate
(`HypothesisImpact.NO_IMPACT` results that weren't duplicates), actions-to-solution (only when
`outcome is VERIFIED`), verification latency in actions (gap between first evidence and STOP),
blocked/unresolved branch counts (read from `ChallengeContext.hypothesis_views()` +
`HypothesisBoard.meta().priority`), and `state_consistency_violations` (an architectural sanity
check: nothing produced evidence after an earlier STOP; nothing reached `VERIFIED` without decision
being `STOP`). `evaluate_runs(results, *, known_correct_flags=None,
known_wrongly_disproven_hypothesis_ids=None) -> AggregateMetrics` computes cross-run rates
(successful termination rate, average duplicate/unnecessary rate, average actions-to-solution) plus
false-verification/false-disproof rates *only* when the caller supplies external ground truth for
each run — without it, both report an honest `0.0` (no observed contradiction) rather than a guess.

## Testing strategy
Preserve all existing `.agent/tests/*.py` untouched. Add `.agent/tests/phase3/` with one file per module
plus `.agent/tests/phase3/scenarios/` for the 3 synthetic end-to-end fixtures: a local
`ThreadingHTTPServer` for the web scenario, and tiny local stdlib-only decode/analyze scripts run
through `SubprocessAdapter` for the crypto and forensics scenarios. Each scenario file exposes a
`build_*_scenario_loop()` helper so `test_scenario_metrics_aggregate.py` can run all three and feed
their `LoopResult`s into `metrics.evaluate_runs()` without duplicating scenario setup.

## Dependencies
Zero new third-party dependencies. `urllib.request`, `subprocess`, `threading`, `pathlib`, `hashlib`,
`json`, `dataclasses`, `enum` — all stdlib, matching Phase 2's constraint.
