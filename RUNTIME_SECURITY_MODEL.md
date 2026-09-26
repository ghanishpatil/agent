# RUNTIME_SECURITY_MODEL

The single hard invariant of the runtime bridge:

> The external LLM / Kiro MUST NEVER directly execute a CTF action. The model may ONLY produce
> typed reasoning proposals. The frozen `ctf_agent` retains all execution, verification, and state
> authority.

## The model's total capability
An `LLMClient` (`ctf_runtime/llm_client.py`) is handed **only text** — a model id and a prompt — and
returns **only text**. It is never given a tool handle, an adapter, a subprocess, an HTTP/browser
client, the kernel, the planner, or the adapter registry. The model can therefore only *emit words*.

## Every gate an emitted proposal must pass before anything executes
Turning words into an executed action requires passing, in order:

1. **JSON parse** (`LLMReasoningSource._safe_json`) — malformed output yields no proposals.
2. **Typed conversion** into the existing `HypothesisSuggestion` / `ActionSuggestion` /
   `InterpretationNote` dataclasses (no parallel schema).
3. **`proposals.validate_*`** (frozen):
   - `validate_action_suggestion(suggestion, adapters)` rejects any `tool` that is **not a
     registered trusted adapter** — so `execute_pwsh`, `shell`, `bash`, raw HTTP, an MCP tool, etc.
     are rejected here, before the planner.
   - `_reject_forbidden_phrases` rejects prose attempting a state transition
     ("mark verified", "assume verified", "declare disproven", …).
4. **Hypothesis validation + OPEN-only seeding** — a proposed hypothesis can only become an `OPEN`
   `Hypothesis`; the model cannot set a status.
5. **Candidate routing** (`RoutedReasoningSource._eligible_candidate`, frozen) — a `candidate_flag`
   is only routed to the verifier if its source hypothesis is kernel-`SUPPORTED` **and** the exact
   candidate string already appears in bound evidence. A guessed/placeholder flag is dropped.
6. **Planner** (`ActionPlanner`) — validation, prerequisites, and **action fingerprint /
   deduplication** (`fingerprint_action` + `completed_fingerprints`).
7. **Budget** (`AutonomyController`) — action/iteration/submission/cost limits.
8. **Trusted adapter** (`AdapterRegistry.execute`) — the only execution path; the subprocess adapter
   runs a **fixed allow-listed executable** with args only.
9. **TrustKernel.process** — result classification → evidence → impact → verification. Only an
   authoritative discriminating contradiction may `DISPROVE`; only a verification gate may verify.

## Forbidden paths (none exist in the runtime bridge)
- LLM → `execute_pwsh` — **blocked** (unregistered tool rejected at step 3).
- LLM → raw subprocess / raw HTTP / browser — **blocked** (not registered adapters).
- LLM → direct MCP CTF tool (`hexstrike-ai`, `ctf_solver_mcp`) — **not wired**; classified
  `DIRECT_UNGOVERNED` in `tool_isolation.py`.
- LLM → verification — **impossible**; the model never calls the verifier; candidate acceptance is
  the kernel's `VerificationController` decision from bound evidence.
- LLM → state mutation via prose — **blocked** (`_reject_forbidden_phrases`).

## Tool isolation (Step 4 classification; nothing deleted)
`ctf_runtime/tool_isolation.py` records each surface:
- `Kiro execute_pwsh`, `hexstrike-ai MCP`, `ctf_solver_mcp`, `raw subprocess/network/browser` →
  **DIRECT_UNGOVERNED** — must not be used to solve while an `AgentSession` is active.
- `hexstrike-ai/ctf_toolkit.py` → **WRAPPABLE** — only via a trusted adapter if genuinely needed.
- `ctf_agent` trusted adapters (`AdapterRegistry`) → **TRUSTED_ADAPTER** — the only sanctioned path.

## Anti-guessing / failure-classification guarantees (preserved from Phase 2)
- A proposal does not execute because it "sounds plausible"; it must pass validation, hypothesis
  validity, evidence-where-required, non-duplication, prerequisites, budget, and planner acceptance.
- A failed action still flows through the Result Classifier. `429 / timeout / auth / tool /
  network / environment` failures classify as failures and **cannot disprove** a hypothesis (frozen
  `impact.py`); they only UNRESOLVE/BLOCK the touched hypothesis.
- A fabricated or placeholder flag cannot be verified (demonstrated in tests: a `CTF{...}`
  placeholder and a made-up `CTF{totally_made_up_guess}` are both dropped, never verified).

## Model routing is a cost lever, not a trust lever
`ModelRouter` chooses which model produces the *next proposals* (FAST `sonnet-5` → DEEP `opus-5` →
HIGH_END `gpt-5.6-sol-high`; FALLBACK `gpt-5.6-luna-think` on model error). Escalation is
evidence-driven (uncertainty/stall/failure-class/difficulty/budget), never category→model
hard-coding. Escalation changes *who proposes*; it never changes the pipeline, the state, or the
verification authority, and agent state persists across an escalation (same session, same kernel).
