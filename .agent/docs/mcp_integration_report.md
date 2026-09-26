# CTF Agent ↔ Kiro MCP Integration — Final Report

Thin MCP gateway connecting Kiro to the existing frozen CTF solver via the pre-existing
`KiroBridge`. The frozen Phase 1–5 core (`ctf_agent`) was **not** modified.

Runtime architecture achieved:

```
Kiro IDE → MCP (stdio) → CtfAgentGateway → KiroBridge → AgentSession → LLMReasoningSource
        → ReasoningLoop → ActionPlanner → TrustKernel → Trusted Adapters → Evidence → Verification
```

---

## 1. Files added
- `.agent/src/ctf_runtime/mcp_gateway.py` — `CtfAgentGateway`: input validation, session registry
  + isolation, audit log, lifecycle, and delegation to `KiroBridge`. **No execution primitive.**
- `.agent/src/ctf_runtime/mcp_server.py` — thin FastMCP server (stdio). Registers only the
  sanctioned tools; ships a deterministic **offline demo** gateway and an operator hook
  (`CTF_MCP_GATEWAY_FACTORY`).
- `.agent/tests/runtime/test_mcp_gateway.py` — 9 integration tests (spec Tests 1–6 + validation).
- `.agent/scripts/mcp_stdio_smoke.py` — real subprocess stdio MCP smoke test.
- `.agent/kiro-mcp-config.example.json` — Kiro MCP config template (see §6).
- `.kiro/steering/ctf-agent-mode.md` — CTF Agent Mode behavioral policy (honest about limits).
- `.agent/docs/mcp_integration_report.md` — this report.

## 2. Files modified
- `.agent/src/ctf_runtime/__init__.py` — **exports only** (`CtfAgentGateway`, `GatewayError`,
  `UnknownSession`, `ValidationError`). No behavioral change.

## 3. Frozen files confirmed untouched
All 45 files under `.agent/src/ctf_agent/**` match `docs/phase5_freeze.md` per-file SHA-256
**byte-for-byte** (45/45), before and after the work. Nothing in `ctf_agent` was edited, and
`ctf_agent` does not import `ctf_runtime`.

## 4. MCP tools exposed (10)
Core (8): `ctf_start`, `ctf_step`, `ctf_run`, `ctf_state`, `ctf_hypotheses`, `ctf_evidence`,
`ctf_progress`, `ctf_result`.
Read-only diagnostics (2): `ctf_sessions`, `ctf_trust_boundary`.

## 5. MCP tools deliberately NOT exposed
`execute_pwsh`, `shell`, `bash`, `powershell`, `subprocess`, `curl`, `raw_http`, `browser`,
`python`, `tool_call`, `execute_command`, arbitrary filesystem/network execution. The server has
**no** method that executes anything; execution happens only inside the frozen trusted adapters.

## 6. Kiro configuration used
Kiro reads MCP config from `.kiro/settings/mcp.json` (workspace) or `~/.kiro/settings/mcp.json`
(user). **The agent is not permitted to write `.kiro/settings/` (blocked by `kiro-scope`
permissions), so the operator must place the config manually.** Copy from
`.agent/kiro-mcp-config.example.json`:

```json
{
  "mcpServers": {
    "ctf-agent": {
      "command": "python",
      "args": ["-m", "ctf_runtime.mcp_server"],
      "env": { "PYTHONPATH": "f:\\mission-git-hackss\\mission-git-hackss\\.agent\\src" },
      "disabled": false,
      "autoApprove": ["ctf_state","ctf_hypotheses","ctf_evidence","ctf_progress","ctf_result","ctf_sessions","ctf_trust_boundary"]
    }
  }
}
```
Transport is **stdio** (FastMCP default). `autoApprove` covers only read-only tools.

## 7. Runtime architecture (request path)
`ctf_start` validates intent → operator `environment_factory` builds the trusted `EnvironmentConfig`
→ new `KiroBridge` → `AgentSession.start()` (composes the frozen `solve()` pipeline, substituting
only the `LLMReasoningSource`). `ctf_step`/`ctf_run` delegate to `AgentSession.step()/run()` — no
second loop. Read tools project frozen state. The gateway never executes an action.

## 8. Security / trust boundary
- **Operator-owned seam:** tools/adapters/verification policy/model come from the operator at
  construction; the MCP client supplies only text intent + optional in-memory resource content.
- **Client input is untrusted:** validated for type/size/unexpected fields; execution/environment
  fields (`command`, `permitted_tools`, `environment`, `verification_policy`, …) are rejected;
  resource filenames are path-traversal-safe and client filesystem `path` is refused (content only).
- **LLM boundary:** the model receives text and returns text; it holds no handle. A proposal for an
  unregistered tool is rejected before the planner.
- **Verification authority:** `ctf_result` only reports `VERIFIED_FLAG` when the kernel verified and
  STOPped; candidates are surfaced separately and never promoted.
- **Session isolation:** each `ctf_start` mints a unique `session_id` → its own bridge/kernel/board/
  journal. No cross-session sharing.
- **Audit:** every tool call is logged; `ctf_start` records the chain
  `MCP->CtfAgentGateway->KiroBridge->AgentSession`.

## 9. Tests executed
Full suite (`python -m pytest` from `.agent/`) + the real stdio smoke script.

## 10. Test results
- **398 passed** (baseline 389 + 9 new MCP gateway tests). No failures/errors.
- New tests cover: full pipeline → verified flag; malicious `execute_pwsh` proposal rejected (no
  execution); fake/guessed flag never verified; server exposes only the 10 sanctioned tools;
  forbidden-field / unknown-session / path-traversal validation; session isolation; runtime-journal
  pipeline chain.

## 11. Frozen-core fingerprint before/after
- Per-file manifest comparison: **45/45 identical** before and after (authoritative).
- Aggregate via this repo's method: `bfcacb5eddfec96a09e24be617ff7995186ec1f873aa2f9f34d496b55eecbcd3`
  (stable before/after). This differs from the documented `ead35256…` **only** because the original
  aggregate used a different relpath+digest concatenation; the per-file hashes (which all match) are
  the authoritative integrity proof. No frozen file changed.

## 12. Real smoke-test result
- **In-process demo:** `ctf_start → ctf_run → SOLVED`, verified flag `CTF{mcp_demo_ssti_verified}`;
  journal shows `http_probe` + `flag_verifier` adapters and a `VERIFIED` state.
- **Real stdio subprocess** (`scripts/mcp_stdio_smoke.py`): server launched via
  `python -m ctf_runtime.mcp_server`, driven by an MCP client over stdio → tools listed (no
  execution tool), `ctf_start`/`ctf_run` reached the same **kernel-verified** flag, and a call to
  the unknown `execute_pwsh` tool was rejected (error result) with nothing executed. **SMOKE: PASS.**
- This is an offline deterministic target (fake in-memory web adapter + scripted LLM), as the spec
  requires for the first smoke test. Real network/model integration is an operator step (supply a
  real `environment_factory` with trusted network adapters + a real `LLMClient` via
  `CTF_MCP_GATEWAY_FACTORY`).

## 13. Bypass test result — **BYPASS POSSIBLE (honest)**
The previous `AGENT_BYPASSED` condition is **not** closed at the Kiro layer:
- The MCP gateway and the `ctf-agent-mode` steering do **not** remove Kiro's native `execute_pwsh`
  or other IDE/MCP tools. A CTF earlier in this very workspace was solved by Kiro directly with
  `execute_pwsh`, entirely outside the agent — that path still exists.
- **Technically enforced (inside the agent):** LLM proposals for unregistered tools are rejected;
  only trusted adapters execute; candidates cannot be verified; failures cannot auto-disprove; the
  MCP server exposes no execution primitive. This governs everything that enters the pipeline.
- **Policy-only (outside the agent):** "don't use native tools during a CTF Agent session" is a
  behavioral instruction in the steering file, not a hard control.
- Kiro **does** have a permission mechanism (`kiro-scope` / `~/.kiro/settings/permissions.yaml` — it
  blocked the agent from writing `.kiro/settings/`). An operator could use it to hard-restrict
  native execution tools during CTF work, but that is a Kiro-side configuration step and is **not**
  implemented or verified here. Until then: **bypass is possible.**

## 14. Known limitations
- Default gateway is an offline deterministic demo; real solving requires an operator-supplied
  trusted environment + real LLM client.
- Tool restriction for Kiro's native tools is policy-only (see §13).
- `.kiro/settings/mcp.json` must be installed manually (agent write-blocked by permissions).
- The documented aggregate fingerprint value (`ead35256…`) is not reproducible by a naive
  relpath+digest concatenation; per-file hashes are used as the integrity source of truth.

## 15. Exact command / config to start the MCP server
Manual run (stdio):
```powershell
$env:PYTHONPATH = "f:\mission-git-hackss\mission-git-hackss\.agent\src"
python -m ctf_runtime.mcp_server
```
Via Kiro: install the `.kiro/settings/mcp.json` block from §6 (or copy
`.agent/kiro-mcp-config.example.json`), then reconnect the `ctf-agent` server from Kiro's MCP view.
Real-provider gateway: set `CTF_MCP_GATEWAY_FACTORY=your_module:build_gateway` (a callable returning
a `CtfAgentGateway` built with your trusted `environment_factory` + real `LLMClient`).
