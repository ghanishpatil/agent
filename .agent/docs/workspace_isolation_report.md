# CTF Agent — Workspace Isolation & Bypass-Hardening Audit

Audit-only task. **No file was changed to enforce anything** (see rationale). This documents what
Kiro actually supports (verified against official docs + direct inspection), what is workspace-local
vs global, and why a hard `execute_pwsh` block was deliberately NOT applied.

Workspace root audited: `f:\mission-git-hackss\mission-git-hackss` (Kiro workspace-root hash
`e2b93414e6860ac5`).

---

## 1. Kiro configuration mechanisms discovered (verified)

| Mechanism | Location | Scope | Verified how |
|---|---|---|---|
| MCP servers | `.kiro/settings/mcp.json` (workspace) vs `~/.kiro/settings/mcp.json` (global) | workspace file = this workspace only; merge precedence Agent > Workspace > Global | docs + inspection |
| Steering | `.kiro/steering/*.md` (workspace) vs `~/.kiro/steering/` (global) | workspace-local; `inclusion: manual` loads only when referenced | docs + inspection |
| Permissions | `~/.kiro/workspace-roots/<hash>/permissions.yaml` (per-workspace, per-user) and `~/.kiro/settings/permissions.yaml` (global) | workspace-roots file = that one project only; **deny-overrides**, most restrictive wins | docs + inspection |
| Hooks | `.kiro/hooks/` (workspace) and `~/.kiro/hooks/` (global) | workspace hooks are project-scoped; `preToolUse` can block a tool (exit 2) | docs |
| Agent tool controls | custom-agent `tools`/`excludedTools`/`allowedTools` + per-agent `permissions` | per-agent | docs |

## 2. Which mechanisms are workspace-local
- `.kiro/settings/mcp.json`, `.kiro/steering/*.md`, `.kiro/hooks/*`, and
  `~/.kiro/workspace-roots/<hash>/permissions.yaml` are all scoped to **this workspace only**.

## 3. Which mechanisms are global
- `~/.kiro/settings/mcp.json`, `~/.kiro/settings/permissions.yaml`, `~/.kiro/steering/`,
  `~/.kiro/hooks/` apply to **all** workspaces.

## 4. What I changed
- **Nothing** (this task). Audit + verification only. No enforcement file written.

## 5. What I deliberately did NOT change (and why)
- Did **not** add a `shell` deny to `~/.kiro/workspace-roots/e2b93414e6860ac5/permissions.yaml`.
  Reasons: (a) that path is write-protected for the agent by `kiro-scope` (by design, only the IDE
  "This workspace" approval UI writes it); (b) a blanket `shell` deny would also break normal
  development *in this same workspace* (pytest/python/git are the same dual-use tool), violating the
  top-priority rule "do not break normal Kiro / preserve normal development."
- Did **not** touch any global file (`~/.kiro/settings/*`, `~/.kiro/steering/`, `~/.kiro/hooks/`).
- Did **not** modify frozen `.agent/src/ctf_agent/**`, the MCP gateway/server, or the solver.

## 6. Is `execute_pwsh` available globally?
Yes. It is a native Kiro tool governed by the `shell` capability and remains available everywhere.
The global `~/.kiro/settings/permissions.yaml` currently *allows* a set of shell patterns (npm,
python, git, docker, node, Get-Content, etc.) and contains **no** CTF/deny rules.

## 7. Can `execute_pwsh` be restricted only in this workspace?
**Technically yes.** A rule `{capability: shell, effect: deny, match: ["*"]}` in
`~/.kiro/workspace-roots/e2b93414e6860ac5/permissions.yaml` would hard-block shell in *only* this
workspace (deny-overrides), leaving all other projects untouched. **But it is not applied here**
because (a) the agent cannot write that path, and (b) it would also block legitimate development in
this workspace. This is an operator decision, not an automatic one — see §14 for exact steps if the
tradeoff is accepted.

## 8. Is the CTF MCP workspace-local?
Yes — when installed in `.kiro/settings/mcp.json` (workspace). It is currently **not registered
anywhere** (workspace `.kiro/settings/` does not exist; global `~/.kiro/settings/mcp.json` is empty
`{}`), so it does not leak into any other project. Install per `.agent/kiro-mcp-config.example.json`.

## 9. Is CTF steering workspace-local?
Yes. `.kiro/steering/ctf-agent-mode.md` is in this workspace and uses `inclusion: manual`.
Verified: `~/.kiro/steering/` is empty and no `ctf-agent-mode` exists anywhere under `~/.kiro/`.

## 10. Is any other Kiro project affected?
**No.** Zero global CTF footprint: empty global `mcp.json`, empty global `steering/`, no global
`hooks/`, and no CTF/deny entries in global `permissions.yaml`. The other 13 workspace-roots are not
touched.

## 11. Tests performed and results
- Full suite (`python -m pytest` from `.agent/`): **398 passed** (unchanged).
- Frozen-core per-file SHA-256 vs `docs/phase5_freeze.md`: **45/45 identical**.
- Config inspection (read-only) of global + workspace Kiro settings/steering/hooks/permissions.

## 12. Frozen-core integrity result
`.agent/src/ctf_agent/**` = **byte-for-byte unchanged** (45/45).

## 13. Final classification — **PARTIAL WORKSPACE ISOLATION**
- CTF MCP, steering, runtime, tests, and state are workspace-local with **zero global footprint** —
  other projects are provably unaffected. (This half is effectively HARD.)
- The `execute_pwsh` bypass **remains technically possible** in this workspace, because the only
  hard control (workspace `shell` deny) also breaks normal development here and cannot be
  self-applied by the agent. Kiro exposes **no intent-scoped** ("only when solving a CTF")
  permission that could block CTF misuse while allowing dev use of the same tool.
- Not classified HARD-ENFORCED: that would require a workspace `shell` deny that is not applied.

## 14. Remaining limitations & operator options
- **Inherent dual-use gap:** `execute_pwsh` cannot be "blocked for CTF solving but allowed for dev"
  — the permission layer sees one tool, not intent. Any hard block is all-or-nothing per workspace.
- **Operator option A (hard, breaks dev in this workspace):** in Kiro, when prompted for a shell
  command in this workspace, choose Deny for "This workspace", or add to
  `~/.kiro/workspace-roots/e2b93414e6860ac5/permissions.yaml`:
  ```yaml
  rules:
    - capability: shell
      effect: deny
      match: ["*"]
  ```
  This hard-blocks shell in this workspace only. Accept that pytest/python/git in the terminal here
  stop working until removed.
- **Operator option B (soft, workspace-local):** a `preToolUse` hook in `.kiro/hooks/` matching
  `execute_pwsh` that returns an "ask" decision — a confirmation speed-bump, not a hard block. It
  does not stop a determined bypass and does not fire when Kiro solves *without* starting a session,
  so it is not a real fix for the core bypass.
- **Behavioral layer (in place):** `.kiro/steering/ctf-agent-mode.md` instructs Kiro to route CTF
  work through the MCP tools and not use native execution — policy only, honestly labeled.
- **Agent-side (already enforced):** everything that enters the agent pipeline is governed (LLM
  can't execute, unregistered tools rejected, only trusted adapters run, candidates can't verify).
  This does not and cannot govern actions Kiro takes entirely outside the agent.
