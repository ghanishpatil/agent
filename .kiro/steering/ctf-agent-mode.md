---
inclusion: manual
name: ctf-agent-mode
description: Operating policy for solving CTF challenges through the governed CTF Agent MCP server instead of Kiro's own tools.
---

# CTF Agent Mode

This is a **behavioral operating policy** for Kiro when a CTF challenge is being solved through the
governed CTF Agent runtime. Activate it (via `#ctf-agent-mode`) at the start of any CTF-solving
session that should be driven by the agent.

## Honest scope note (read this first)

This file is a **policy, not a security boundary.** It does **not** technically disable Kiro's
native tools. Kiro *can* still call `execute_pwsh` and other tools; this document only instructs it
not to while an agent-driven CTF session is active. The only thing that is *technically enforced* is
what happens **inside** the agent pipeline (see "What is actually enforced" below). Treat the two
layers separately and never claim the policy layer is a hard control.

## The rule

When an active CTF Agent session exists (created via the `ctf-agent` MCP server's `ctf_start`):

1. **Do not independently solve the challenge.** Do not reason out the exploit and run it yourself.
2. **Do not use native execution tools** (`execute_pwsh`, shell, subprocess, browser, raw HTTP,
   arbitrary Python) against the challenge target.
3. **Do not use other MCP servers** (e.g. hexstrike-ai, ctf_solver_mcp) to attack the target.
4. **Drive the challenge only through the `ctf-agent` MCP tools:** `ctf_start`, `ctf_step`,
   `ctf_run`, `ctf_state`, `ctf_hypotheses`, `ctf_evidence`, `ctf_progress`, `ctf_result`.
5. **Do not treat a candidate string as a flag.** Only `ctf_result` with `result_type =
   VERIFIED_FLAG` (kernel-verified) is a solve.

Kiro acts as the control/interface layer; the agent owns planning validation, execution through
trusted adapters, evidence, verification, and stopping.

## Architecture A — the observe → propose loop (Kiro is the reasoner)

The intended flow: **Kiro's own model does the reasoning**, the CTF agent governs execution.

1. `ctf_start` (driver defaults to `kiro`) → get `session_id`.
2. `ctf_observe(session_id)` → read authoritative state: hypotheses, evidence,
   `recent_observations` (real adapter output), `available_tools`, and the `proposal_schema`.
3. **Reason** from that state. Decide the single cheapest discriminating next action.
4. `ctf_propose(session_id, hypotheses=[...], actions=[...])` — submit TYPED proposals using ONLY
   `available_tools`. The agent validates, plans, executes via trusted adapters, records evidence,
   and controls verification. You never execute anything yourself.
5. `ctf_observe` again; repeat 3–4 using the new evidence.
6. Only set `candidate_flag` when a flag string is already visible in observed evidence. It is
   verified only if the kernel accepts it (`result_type: VERIFIED_FLAG`).
7. Stop at `VERIFIED_FLAG` or a justified terminal state. Do not re-propose a
   rejected/deduplicated action without a state change. Treat failures per the returned
   classification (429/timeout/tool/network are NOT hypothesis disproof).

`driver='internal'` (ctf_step/ctf_run) still exists for the offline demo/tests.

## Why (the AGENT_BYPASSED problem)

A prior runtime audit (`RUNTIME_PATH.md`) found Kiro had solved a CTF directly with `execute_pwsh`,
bypassing the ReasoningLoop / ActionPlanner / TrustKernel / Evidence / Verification / Journal. That
produced fabricated, ungoverned, unverifiable "solving." CTF Agent Mode exists to prevent a repeat.

## What is actually enforced (technical, inside the agent)

Independent of this policy, the agent pipeline enforces:

- The LLM receives **text only** and can emit only typed proposals; it holds no execution handle.
- A proposal for an unregistered tool (e.g. `execute_pwsh`) is **rejected before the planner**; no
  adapter runs it.
- Only operator-registered **trusted adapters** execute, via `TrustKernel`
  (classify → evidence → impact → verify).
- A candidate flag with no bound evidence **cannot be verified**; verification/STOP is the kernel's.
- Rate-limit/timeout/network/tool/environment failures **cannot** auto-disprove a hypothesis.
- The MCP server exposes **no** shell/http/subprocess/file execution tool.

## What is NOT enforced (policy only)

- Kiro's own `execute_pwsh` and other IDE/MCP tools remain callable. Nothing in this file or the MCP
  server removes them. If Kiro ignores this policy and runs `execute_pwsh` on the target, the bypass
  is still technically possible. Restricting Kiro's native tools requires a Kiro-side mechanism
  (e.g. session/agent tool permissions), not this steering file.
