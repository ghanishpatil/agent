# RUNTIME_INTEGRATION

How Kiro (and any operator) uses the runtime bridge to solve a real challenge through the frozen
`ctf_agent`, instead of solving it directly with IDE tools.

## The rule
Once an `AgentSession` is active, Kiro drives it through the bridge and must NOT solve the challenge
with its own tools (`execute_pwsh`, MCP CTF tools, raw subprocess/HTTP/browser). Kiro's role becomes:
supply challenge intent, advance the agent, observe state, read the verified flag.

## Trust separation (who supplies what)
- **Operator** supplies the trusted `EnvironmentConfig`: `permitted_tools` (each a real
  `ToolAdapter`), `evidence_rules`, and the `verifier_route`. This is where real capability
  (network/subprocess) is granted — as trusted adapters, never as raw handles.
- **Kiro** supplies only *challenge intent*: name/category/description/hints/urls/credentials and
  file resources. Kiro cannot inject an execution tool, because it never provides the adapter
  registry.
- **Deployment** supplies a concrete `LLMClient` (wrap a model API with `CallableLLMClient`), or a
  `ScriptedLLMClient` for tests.

## Minimal usage (KiroBridge)
```python
from ctf_runtime import KiroBridge, ModelRouter, CallableLLMClient
from ctf_agent.autonomy.contracts import EnvironmentConfig, SolveConstraints

env = EnvironmentConfig(permitted_tools=(... trusted adapters ...),
                        evidence_rules=(...), verifier_route=...)   # operator-provided
client = CallableLLMClient(lambda model, prompt: call_my_model(model, prompt))  # deployment

bridge = KiroBridge(environment=env, llm_client=client,
                    constraints=SolveConstraints(), router=ModelRouter(),
                    session_journal_path=Path("runtime/session.jsonl"))

bridge.start_challenge(name="Example", category="web",
                       description="...", urls=("https://target/app",),
                       flag_format="CTF{...}")

# advance one reasoning step at a time (Kiro observes; it never executes)
report = bridge.next_step()          # StepReport: model, adapter, decision, impact, verified
state  = bridge.get_state()          # hypotheses + evidence + progress
# ...or run to terminal:
summary = bridge.run()               # {status, verified_flag, terminal_reason, ...}
flag = bridge.get_flag()             # verified flag or None
```
`KiroBridge` exposes **no execution primitive** — there is intentionally no `run_shell`/`http`/`tool`
method. The only way to make anything happen is `next_step()` / `run()`, which drive the frozen loop.

## Direct session API (AgentSession)
```python
from ctf_runtime import AgentSession
session = AgentSession(challenge, llm_client=client, environment=env,
                       constraints=constraints, router=ModelRouter()).start()
session.step(); session.run()
session.get_state(); session.get_pending_actions(); session.get_evidence()
session.get_hypotheses(); session.is_verified(); session.get_flag(); session.get_result()
```

## Observability
Two journals are produced per run:
1. The **frozen loop journal** (`RuntimeJournal`, written by `ReasoningLoop`) — solve/hypothesis/
   planner/action/classification/evidence/impact/verification/stop events.
2. The **runtime session journal** (`RuntimeSessionJournal`, `session_journal_path`) — per executed
   step, all required fields: `timestamp, challenge_id, model, reasoning_source, hypothesis_id,
   hypothesis_state, proposal_id, action_fingerprint, planner_decision, execution_adapter,
   observation_class, evidence_id, impact, verification_state, escalation_reason`.

Together they prove a real solve traversed the architecture (see the trace in
`RUNTIME_ARCHITECTURE.md`).

## Controlled real-challenge smoke test (Step 9)
`ctf_runtime.smoke.prepare_real_session(spec, environment=..., llm_client=...)` assembles and
composes a real `AgentSession` but **does not run it** (`AUTORUN_DISABLED = True`). It refuses to
prepare a session with no trusted tools. The first real target is chosen by a human, who then calls
`.step()` / `.run()` explicitly. `RealChallengeSpec` accepts description, category, hints, target,
flag_format, resources, and credentials.

## What is NOT included (out of scope / PLANNED)
- A concrete model-API client (only the `CallableLLMClient` seam is provided).
- Trusted adapters for specific real-world tools (operator responsibility).
- Any change to Phase 5 / `ctf_agent` (explicitly forbidden and verified unchanged).
- No new agent architecture, planner, knowledge subsystem, or fine-tuning.
