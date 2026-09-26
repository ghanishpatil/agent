# Architecture A — Kiro-Driven Reasoning Inversion — Report

Kiro's own model is the reasoner; the frozen CTF agent is the authoritative execution/evidence/
verification layer. No external LLM, no API key, no MCP sampling, no direct Kiro execution. Frozen
`ctf_agent/**` untouched.

```
Kiro model → ctf_observe → (Kiro reasons) → ctf_propose → validate → ActionPlanner → TrustKernel
           → trusted adapter → observation → classifier → evidence → hypothesis impact
           → verification / STOP → ctf_observe → (repeat)
```

## Implementation (all additive, `ctf_runtime` only)
- `kiro_driven.py` — `QueuedReasoningSource` (a frozen-`ReasoningSource` whose proposals are what
  Kiro loads) + `KiroDrivenController` (`observe()` / `propose()` + passthrough reads). No LLM runs
  inside the runtime on this path.
- `session.py` — additive `inner_reasoning_source` hook (injected source is wrapped by the frozen
  `RoutedReasoningSource`), `adapter_registry` + `metadata` accessors, and a `recent_observations()`
  projection so `observe()` can expose real adapter output. `llm_client` is now optional. Backward
  compatible (internal path unchanged).
- `mcp_gateway.py` — `ctf_observe` / `ctf_propose`; per-session `driver` (`internal` | `kiro`);
  internal-only tools reject kiro sessions and vice-versa; existing isolation/audit/budget reused.
- `mcp_server.py` — new MCP tools `ctf_observe` + `ctf_propose`; `ctf_start` gains a `driver` param
  (**MCP default `kiro`**; gateway programmatic default stays `internal` so existing tests are
  unaffected).

## MCP tools (now 12)
Existing 10 + **`ctf_observe`** (read authoritative state + proposal schema) and **`ctf_propose`**
(submit typed hypotheses/actions → frozen pipeline). Still **no** shell/exec/http/file execution
primitive.

## Security — how Kiro proposals are constrained
- Kiro only proposes typed data; it never executes. `validate_action_suggestion` rejects
  unregistered tools (e.g. `execute_pwsh`, `curl`) **before** the planner; malformed/empty
  proposals are rejected with reasons.
- The planner de-duplicates; the kernel classifies, binds evidence, and owns verification/STOP.
- A `candidate_flag` is verified only by the frozen VerificationController (kernel STOP); proposing
  it is never sufficient.
- Failures (429/timeout/403/tool/network) are classified and never disprove a hypothesis.
- Budgets, session isolation, and the audit journal are the frozen mechanisms.

## Tests
- Full suite: **417 passed** (was 409; +8 Architecture A tests). No failures.
- `test_kiro_driven.py`: full observe→propose→execute→observe→propose→`VERIFIED_FLAG`; `execute_pwsh`
  rejected; unknown/malformed rejected; fake flag not verified; duplicate action deduplicated;
  session isolation; driver guards (kiro session rejects ctf_run/ctf_step; internal rejects
  observe/propose).
- Real transport: `scripts/mcp_kiro_smoke.py` drives the observe/propose loop over **stdio** →
  `VERIFIED_FLAG` (deterministic reasoner stand-in). Internal-path `scripts/mcp_stdio_smoke.py` still
  PASS.

## Frozen-core integrity
`.agent/src/ctf_agent/**` — **45/45 byte-for-byte unchanged**.

## Real Kiro test — PENDING SERVER RECONNECT
The connected `ctf-agent` MCP server is still the pre-change process (its tool list lacks
`ctf_observe`/`ctf_propose`). To run the live test where **the actual Kiro model** reasons:
1. Reconnect/restart the `ctf-agent` MCP server (it will expose 12 tools incl. observe/propose).
2. Kiro: `ctf_start` (driver defaults to `kiro`) → `ctf_observe` → reason → `ctf_propose` →
   `ctf_observe` → `ctf_propose` (submit observed flag) → expect `VERIFIED_FLAG`.
The server provides state and executes proposals; the reasoning is NOT hardcoded — Kiro decides.

## Remaining limitations
- The demo/pilot targets are the offline deterministic SSTI/file environments; a real challenge
  needs an operator environment (authorized target, evidence rules, verifier).
- The internal `LLMReasoningSource` path is retained (per instruction) for comparison; it still
  needs an operator `LLMClient` to reason on real challenges.
- The IDE-level `execute_pwsh` bypass remains a documented, out-of-scope limitation.
