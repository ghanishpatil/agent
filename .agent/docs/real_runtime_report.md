# Operator-Controlled Real CTF Runtime — Report

Smallest safe operator-controlled real runtime built entirely in `ctf_runtime` (frozen
`ctf_agent/**` untouched). Reuses the frozen trusted adapters rather than adding new execution
primitives.

## Runtime status: **PARTIAL** (real runtime + real-adapter path proven; autonomous real solve BLOCKED on operator LLM credentials)

## Real adapters implemented
No new execution primitives were written — the frozen adapters already enforce the required policy
and are composed by the operator env builder:
- **File** — `ctf_agent.adapters.FileAdapter`: read-only, confined to the per-session workspace,
  rejects path traversal/absolute paths, size-capped.
- **HTTP** — `ctf_agent.adapters.HttpAdapter` + `HttpPolicy`: scheme://host allow-list, refuses
  non-allowlisted targets *before* any network I/O, timeout + body cap.
- **Process** — `ctf_agent.adapters.SubprocessAdapter` + `SubprocessCommand`: ONE fixed executable
  per adapter, args-only (no `execute_anything`), timeout.
- **Verifier** — operator-supplied adapter (e.g., deterministic self-check / remote grader) wired
  as `verifier=True` with a `CandidateVerifierRoute`.

New (additive) glue in `ctf_runtime`:
- `real_environment.py` — `OperatorPolicy`, `AllowedExecutable`, `build_operator_environment()`
  (composes the frozen adapters per operator policy; deny-by-default), and `build_operator_gateway()`
  (real LLM seam + frozen `ModelRouter`, usable via `CTF_MCP_GATEWAY_FACTORY`).

## Security boundaries (all enforced, tested)
- Deny-by-default: only explicitly registered adapters exist; unknown/unregistered tool →
  `UnknownToolError` (`REJECTED_TOOL`). No `execute_pwsh`/shell/`execute_anything` anywhere.
- File confined to workspace; `../` and absolute paths refused. Resource filenames validated at the
  gateway (no traversal); challenge resources materialize only under `<workspace>/resources/...`.
- HTTP only to operator allow-listed hosts; cloud-metadata / arbitrary hosts refused pre-I/O.
- Process is one fixed executable per adapter; the LLM proposes, the policy/registry decides.
- LLM boundary: text in, typed proposals out; never receives adapter/subprocess/socket/file handles.

## Budget controls
`SolveConstraints` (per policy): wall-clock timeout, max actions/iterations/tool-executions,
network/remote/submissions/expensive/specialist calls, total cost. Budget exhaustion yields a
defined terminal (`BLOCKED`/`EXHAUSTED`/`FAILED`) — never a flag, never `DISPROVEN`.

## LLM integration
`LLMReasoningSource` (existing) wraps the operator `LLMClient` and the existing `ModelRouter`
(FAST/DEEP/FALLBACK/HIGH_END preserved; not hardcoded per category). The operator supplies a real
client via `CallableLLMClient(fn)` and points `CTF_MCP_GATEWAY_FACTORY` at a `build_operator_gateway`
call. **No model credentials are configured in this environment** (OPENAI/ANTHROPIC/GOOGLE/... all
unset), so the real model path is not exercised here.

## Verification mechanism
Uses the frozen verification hierarchy. A candidate becomes `VERIFIED_FLAG` only when an
authoritative source confirms it (verifier adapter / deterministic self-check / matching
authoritative observation). With no verifier configured, `VERIFIED_FLAG` is impossible — a
flag-shaped string is never auto-accepted. Failures (timeout/429/403/tool/network) are classified
and never disprove a hypothesis.

## Tests
- Full suite: **409 passed** (baseline 398 + 11 new). No failures.
- New `tests/runtime/test_real_runtime.py` (11): file confinement + traversal rejected; HTTP
  unauthorized/metadata refused; subprocess fixed-executable; registry rejects unregistered/arbitrary
  tool; deny-by-default env composition; failure classification (timeout/429/403/tool/network) not
  disproof; fake flag not verified (no verifier); budget exhaustion clean terminal; session
  isolation; resource-boundary traversal rejected at gateway; and a **real FileAdapter + real
  verifier end-to-end pipeline verify**.
- MCP stdio smoke: PASS. Runtime bridge + gateway suites: green.

## Frozen-core integrity
`.agent/src/ctf_agent/**`: **45/45 files byte-for-byte unchanged** (matches `phase5_freeze.md`).

## Pilot challenge readiness / what was actually exercised
- **Real-adapter pilot (`scripts/real_pilot_localfile.py`) — PASS**: a real `FileAdapter` read a
  materialized local file, real evidence was bound, and a real deterministic verifier confirmed the
  flag → `VERIFIED_FLAG` through the full frozen pipeline (journal shows `read_file` + `flag_verifier`).
  No `execute_pwsh`, no direct Python solving, no injected flag (the flag was read from the file and
  independently re-derived by the verifier). **Reasoning was a scripted stand-in.**
- This proves the real *execution + verification* path. It is **not** an autonomous real solve.

## Remaining limitations (precise)
1. **Autonomous real solve is BLOCKED on an operator LLM client.** No model API key is configured
   in this environment; `LLMReasoningSource` has no real model to reason with. The seam exists
   (`build_operator_gateway(policy, CallableLLMClient(fn))` + `CTF_MCP_GATEWAY_FACTORY`), but a real
   provider + credentials must be supplied by the operator.
2. **A real target + challenge-specific config** (authorized URL/host allow-list or resource files,
   evidence rules, and a verifier or deterministic check) must be provided per challenge; the
   runtime does not auto-discover targets or tools.
3. The IDE-level `execute_pwsh` bypass remains a documented limitation (out of scope here).

## How an operator runs a real challenge
1. Write `build_gateway()` returning `build_operator_gateway(policy, CallableLLMClient(<your model fn>))`
   with an `OperatorPolicy` authorizing the needed adapters (host allow-list / executables / verifier /
   evidence rules / budgets).
2. Set `CTF_MCP_GATEWAY_FACTORY=your_module:build_gateway`, restart the `ctf-agent` MCP server.
3. Drive via `ctf_start` → `ctf_run`/`ctf_step` → `ctf_result` (as validated over MCP).
