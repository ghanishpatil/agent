# Phase 5 Design — Autonomous Solver and Evaluation Baseline

## Scope and frozen boundaries
Phase 5 composes the existing system; it does not replace it. The Phase 2 `TrustKernel.process()` remains the only trusted state transition. Phase 3's planner/adapters/deduplication and Phase 4's advisory `Specialist` contract remain authoritative at their existing boundaries. No external corpus, model training, RL, swarm, unrestricted command execution, or second tool runtime is introduced.

Fresh pre-change baseline: 216 tests pass; compileall is clean; protected SHA-256 manifests contain 15 `.agent_audit` files, 8 `.kiro` files, and 32 `writeups` files.

## Additive module layout
```text
ctf_agent/autonomy/
  contracts.py    rich challenge/resource/environment/constraint and SolveResult types
  control.py      deny-before-execute budgets, deadline, state/prerequisite reducer
  solver.py       solve(challenge, resources, environment, constraints) composition root
  evaluation.py   labeled known/novel/adversarial/held-out evaluation and 20 metrics
  baseline.py     reproducible JSON baseline manifest generation
```
Existing-file changes are restricted to:
1. `loop.py`: optional no-op-by-default controller hooks and `TIMEOUT` loop outcome.
2. `journal.py`: additive Phase 5 event kinds.
3. `specialists/brain.py`: per-context analysis cache, invocation guard, and audit history/callbacks.
4. `ctf_agent/__init__.py`: public Phase 5 exports.

No Phase 2 module is modified.

## Public input contract
`solve(challenge, resources=(), environment=None, constraints=None) -> SolveResult` accepts:
- `ChallengeInput`: optional name/category/description/points/solves/hints/flag format/URLs/credentials/attempt limit/constraints/revision.
- `ChallengeResource`: typed FILE/SOURCE/BINARY/ARCHIVE/IMAGE/PCAP/APK/DOCUMENT content or path.
- `EnvironmentConfig`: explicitly permitted adapter-backed tools, trusted sources, verification policy, evidence rules, initial state/prerequisites, memory root, workspace/journal paths, and deterministic clocks for tests.
- `SolveConstraints`: hard total/iteration/tool/network/remote/submission/expensive/specialist/cost/wall-time budgets.

Missing input is not silently promoted to fact. `ChallengeUnderstanding` carries `InputFact`s with `KNOWN`, `UNKNOWN`, `ASSUMED`, `INFERRED`, or `VERIFIED`. This is an input-epistemic layer only; it does not alter Phase 3 `FactState` or kernel evidence.

## Public terminal contract
`SolveStatus`: `SOLVED`, `BLOCKED`, `EXHAUSTED`, `FAILED`, `INVALID_INPUT`, `TIMEOUT`.

`SolveResult` includes no flag unless the final kernel snapshot contains a `VerificationStatus.VERIFIED` candidate and global `ControlDecision.STOP`. Solved results include verification evidence ids, final verification method, action/evidence/hypothesis traces, specialist contributions, solution summary, budget usage, knowledge attribution, duration, and journal path. Non-solved results include terminal reason, remaining hypotheses, unresolved blockers, important evidence, and attempted actions; `verified_flag` is always `None`.

Mapping:
- verified kernel STOP -> `SOLVED`
- no actions/prerequisites/state conflict -> `BLOCKED`
- any deny-before-execute budget -> `EXHAUSTED`
- wall deadline -> `TIMEOUT`
- input/composition validation error -> `INVALID_INPUT`
- unexpected orchestration/adapter exception -> `FAILED`

A classified tool/network/environment/auth/rate-limit failure never directly maps the whole solve to `FAILED`; it remains evidence on its hypothesis until alternatives are exhausted.

## Autonomous composition
The facade validates and normalizes inputs, materializes supplied resource content under the permitted workspace, infers a missing category only from explicit description/resource indicators (recorded `INFERRED`), creates an explicit `AdapterRegistry` from `PermittedTool` objects, composes `AdvisoryMemory`, `SpecialistRegistry.default()`, cached `SpecialistReasoningSource`, `ActionPlanner`, `TrustKernel`, `RuntimeJournal`, `AutonomyController`, and `ReasoningLoop`, then runs without human action sequencing.

The default reasoning source is the Phase 4 specialist brain. A challenge description/resources/permitted environment are sufficient; neither the solver nor evaluation cases contain challenge-name-to-flag maps or predefined action sequences. Scenario tools/oracles may produce/verify observations but cannot select the next action.

## Loop controller and state reduction
`AutonomyController` is optional in `ReasoningLoop`, preserving every old caller. Hooks:
- `before_iteration(context)` enforces iteration/specialist/deadline budgets.
- `observe_suggestions(suggestions, state)` records proposal/retry observability.
- `before_action(proposal, state)` denies an action before execution if any projected budget would exceed its limit.
- `after_result(proposal, result, state)` records actual usage/failure class and returns `StateUpdate`.

`StateUpdate` may advance environment/auth/session/challenge revision and add/remove satisfied prerequisites only from structured `ExecutionResult.metadata`. If `state_changed=True` lacks a declared revision/state description, the controller records an unknown mutation and blocks further execution instead of blindly continuing.

## Specialist efficiency and trace
`SpecialistReasoningSource` caches one analysis batch by `ChallengeContext` object identity, so the loop's hypothesis and action requests share one specialist pass. It records selection/analysis history and emits JSON-safe events to an optional sink. An invocation guard enforces the specialist-call budget; denial is surfaced to the controller and no specialist can bypass it.

## Observability
Additive events: `SOLVE_STARTED`, `CONTEXT_UPDATED`, `SPECIALIST_SELECTED`, `SPECIALIST_INVOKED`, `SPECIALIST_PROPOSAL`, `PLANNER_DECISION`, `DEDUPLICATION_REJECTED`, `FAILURE_CLASSIFIED`, `EVIDENCE_IMPACT`, `DEAD_END_CLOSED`, `CANDIDATE_CREATED`, `VERIFICATION_COMPLETED`, `STOP_REACHED`, `BUDGET_UPDATED`, `RECOVERY_DECISION`, `SOLVE_FINISHED`.

The solver, controller, brain, and loop write through `RuntimeJournal`; no specialist writes directly. The journal can reconstruct why a specialist was selected, what was proposed, why an action ran/stopped, what evidence/impact resulted, how budgets changed, and why the terminal status was chosen.

## Budget semantics
All limits are non-negative integers (wall time positive). Counters: iterations, total actions, tool executions, network actions, remote attempts, submissions, expensive actions, specialist calls, and total cost. `before_action` checks projected usage and refuses before adapter execution; therefore budget violations must remain zero. Challenge attempt limits tighten (never loosen) the submission/remote limit.

## Evaluation
`EvaluationCase` labels `KNOWN`, `NOVEL`, `ADVERSARIAL`, or `HELD_OUT`, supplies only a challenge/resources/environment factory/constraints and independent ground truth. It never supplies actions or the correct hypothesis. `EvaluationHarness` runs `solve` and records failures openly.

Metrics (all 20 required): solve rate, verified solve rate, false verification/disproof, mean/median actions, duplicate-action rate, blind-retry rate, dead-end recovery, environment/tool-failure recovery, specialist-selection accuracy, useful specialist proposal rate, candidate verification success, stop correctness, budget violations, mean reasoning iterations, time to verified solution, resource/tool cost, and terminal-state correctness. Each result also records knowledge attribution (`DIRECT_MECHANISM_REASONING`, `MEMORY`, `SPECIALIST_KNOWLEDGE`, `CHALLENGE_ARTIFACT`, `KNOWN_TECHNIQUE`, `ANALOGY`). Ground-truth-dependent rates are never inferred without labels.

Benchmark composition:
- known regression cases represented by existing memory/mechanisms;
- novel synthetic cases with different flags/artifacts and no name shortcuts;
- adversarial misleading hints, flag-shaped decoys, failures, contradictions, and duplicate opportunities;
- held-out structurally similar but materially different mechanisms, including anti-memorization pairs.

## Baseline artifact
`.agent/docs/phase5_baseline.json` records UTC generation time, git revision/dirty state when available, Python/platform, model configuration (`deterministic specialist brain; no external LLM configured` unless explicitly changed), exact test/challenge ids and labels, tool names, budgets, memory file hashes, aggregate metrics, per-case outcomes/failures, and protected-tree integrity. This is the clean baseline for the later external-writeup project.

## Acceptance gates
- Existing 216 tests remain green.
- Explicit Phase 5 trust tests cover all 15 items in section 35.
- Autonomous scenarios begin only from input/resources/environment; no action scripts.
- Failure injection covers timeout, command/network/HTTP auth/rate failures, malformed output, unavailable tool, corrupted artifact, unknown mutation, contradiction.
- Full tests, historical 12/12, all prior/new scenarios, compileall/static checks pass.
- Phase 2 files and protected trees remain byte-identical.
- Final report includes the exact mandated status block and negative results.
