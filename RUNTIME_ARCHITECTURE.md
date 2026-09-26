# RUNTIME_ARCHITECTURE

The production runtime bridge that makes the frozen `ctf_agent` the actual authority for real CTF
solving. It is **additive**: a new package `.agent/src/ctf_runtime/` composes the frozen `solve()`
pipeline and substitutes only the reasoning source. Nothing in `ctf_agent` (Phase 5) is modified.

## Where it lives
```
.agent/src/ctf_runtime/
  __init__.py            exports
  llm_client.py          LLMClient contract (text-in/text-out) + ScriptedLLMClient/CallableLLMClient
  routing.py             ModelRouter (FAST/DEEP/FALLBACK/HIGH_END) — ReasoningSource layer only
  reasoning_source.py    LLMReasoningSource — the real ReasoningSource protocol implementation
  journal.py             RuntimeSessionJournal — required observability fields per step
  session.py             AgentSession — runtime entrypoint (start/step/run/get_*)
  kiro_bridge.py         KiroBridge — the facade Kiro uses instead of solving directly
  tool_isolation.py      classification of every direct execution surface
  smoke.py               controlled real-challenge interface (prepares, never auto-runs)
.agent/tests/runtime/test_runtime_bridge.py   integration + negative + routing tests
```
(The package is under `src/` so it is importable and does not collide with the solver's runtime
journal directory `.agent/runtime/`, which is `_default_runtime_root()`.)

## The mandated path (unchanged, now actually driven by an external model)
```
LLM (text only)
  -> LLMReasoningSource: parse JSON -> proposals.validate_* -> typed *Suggestion
  -> RoutedReasoningSource (frozen: candidate submissions routed to the trusted verifier)
  -> ReasoningLoop._seed_hypotheses -> HypothesisBoard.propose_hypothesis (OPEN only)
  -> ReasoningLoop._select_next -> ActionPlanner.propose_with_diagnostics
       (validation + prerequisites + action fingerprint / deduplication)
  -> ReasoningLoop._execute_one -> AdapterRegistry.execute (trusted ToolAdapter)
  -> TrustKernel.process:
       Result Classifier -> Evidence Manager (+provenance) -> Hypothesis Impact
       -> State update -> VerificationController -> STOP
```
Every component after `LLMReasoningSource` is the **frozen** `ctf_agent` implementation. The LLM only
adds typed proposals at the one sanctioned extension point (`ReasoningSource`).

## Component labels

| Component | Status |
|---|---|
| `ctf_agent/*` (kernel, planner, loop, adapters, classifier, evidence, verification, specialists) | **FROZEN** (aggregate `ead35256…`, unchanged) |
| `ctf_bench/phase5_benchmark.py` + phase5 artifacts | **FROZEN** (unchanged) |
| `ctf_runtime/reasoning_source.py` `LLMReasoningSource` | **IMPLEMENTED** (new; real ReasoningSource) |
| `ctf_runtime/session.py` `AgentSession` | **IMPLEMENTED** (new; mirrors `solve()` via `_solver` helpers) |
| `ctf_runtime/routing.py` `ModelRouter` | **IMPLEMENTED** (new) |
| `ctf_runtime/kiro_bridge.py` `KiroBridge` | **IMPLEMENTED** (new) |
| `ctf_runtime/journal.py` `RuntimeSessionJournal` | **IMPLEMENTED** (new) |
| `ctf_runtime/tool_isolation.py` | **IMPLEMENTED** (classification data only) |
| `ctf_runtime/smoke.py` `prepare_real_session` | **IMPLEMENTED** (prepares only; `AUTORUN_DISABLED=True`) |
| A concrete production `LLMClient` (real model API) | **PLANNED** (seam provided via `CallableLLMClient`; not shipped) |
| Trusted adapters for real network/subprocess CTF tools | **PLANNED** (operator supplies via `EnvironmentConfig.permitted_tools`) |

## AgentSession composition (reuse, not duplication)
`AgentSession.start()` builds exactly the objects `ctf_agent.autonomy.solver.solve()` builds, calling
the frozen helper functions verbatim (`_solver._adapter_registry`, `_apply_attempt_limit`,
`_verification_policy`, `_test_specs`, `_initial_state`, `_memory`, `_project_result`,
`_run_id`, `_duration_ms`). The only substitution:

```
brain          = SpecialistReasoningSource(SpecialistRegistry.default(), ...)   # frozen deterministic
llm_source     = LLMReasoningSource(client, adapters=registry, router=..., base=brain)
reasoning_src  = RoutedReasoningSource(llm_source, env.verifier_route)          # frozen wrapper
loop           = ReasoningLoop(..., reasoning_source=reasoning_src, ...)        # frozen loop
```

## Stepping model
One `AgentSession` holds one `ReasoningLoop`; the loop persists board/kernel/fingerprints/
prerequisites on itself. `step()` calls `loop.run(state, max_actions=1)`; `run()` repeats `step()`
until verified, blocked (no new action produced), or budget. Terminal is detected from
`is_verified()` and from whether a new `PipelineResult` was produced — never from the 1-action run's
`outcome` (a single-action run reports `BUDGET_EXHAUSTED` even mid-solve). Multi-action state
threading within one `run()` call is handled entirely by the frozen loop.

## One real execution trace (deterministic SSTI web environment)
```
STATUS=SOLVED  flag=CTF{rt_ssti_real}  method=AUTHORITATIVE_VERIFIER

step 1: model=sonnet-5  hypothesis=web-ssti[SUPPORTED]  proposal=a1
        fingerprint=17bf2d97…  planner=CONTINUE  adapter=http_probe
        observation=TARGET_RESPONSE  evidence=ev-5490f350  impact=SUPPORTS  verification=null
        escalation="default fast path (low uncertainty, no stall, no blocking failure)"
step 2: model=sonnet-5  hypothesis=web-ssti[SUPPORTED]  proposal=a2
        fingerprint=6ea27990…  planner=STOP  adapter=flag_verifier
        observation=SUCCESS  evidence=ev-9fd749bd  impact=NO_IMPACT  verification=VERIFIED
```
This is the complete causal chain: LLM → typed proposal → planner → trusted adapter → observation →
classifier → evidence → impact → verification → STOP.
