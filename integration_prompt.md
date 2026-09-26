You are working inside the existing CTF-agent repository.

Your task is to connect the already-implemented CTF Agent runtime to Kiro through a local MCP server, without rebuilding or modifying the frozen CTF-solving core.

0. NON-NEGOTIABLE OBJECTIVE

The final architecture must be:

Kiro IDE
   │
   │ MCP
   ▼
CTF Agent MCP Server
   │
   ▼
KiroBridge
   │
   ▼
AgentSession
   │
   ▼
LLMReasoningSource
   │
   ▼
ReasoningLoop
   │
   ▼
ActionPlanner
   │
   ▼
TrustKernel
   │
   ▼
Trusted Adapters
   │
   ▼
Authorized CTF Target

Kiro must act as the control/interface layer.

The CTF Agent must own:

challenge reasoning
hypothesis generation
action planning
tool selection
execution through trusted adapters
evidence collection
failure classification
hypothesis updates
verification
stopping
flag extraction
runtime journaling

Do not allow Kiro's LLM to directly solve the challenge outside this pipeline.

1. FIRST: AUDIT, DO NOT EDIT

Before changing anything, inspect the existing implementation.

Read at minimum:

.agent/src/ctf_agent/
.agent/src/ctf_runtime/
.agent/tests/
.agent/pyproject.toml

Especially inspect:

ctf_runtime/session.py
ctf_runtime/kiro_bridge.py
ctf_runtime/llm_client.py
ctf_runtime/reasoning_source.py
ctf_runtime/routing.py
ctf_runtime/journal.py
ctf_runtime/tool_isolation.py
ctf_runtime/smoke.py

Also inspect:

ctf_agent/llm_boundary.py
ctf_agent/kernel.py
ctf_agent/hypothesis.py
ctf_agent/evidence.py
ctf_agent/verification.py
ctf_agent/deduplication.py
ctf_agent/classifier.py

Understand the existing APIs before implementation.

Important

The existing Phase 1–5 solver is considered FROZEN.

Do not redesign it.

Do not replace it.

Do not duplicate it.

Do not "improve" its architecture.

2. FROZEN CORE PROTECTION

The following must remain untouched unless absolutely required for a compatibility fix:

.agent/src/ctf_agent/**

The current frozen-core fingerprint is:

ead35256c11e882157688410a9618de1e45c3f80a57f4bfb4be7728ebdffdb88

Before implementation, record the current fingerprint/state.

After implementation, verify that the frozen core has not changed.

If a change to ctf_agent appears necessary, STOP and explain why instead of silently modifying it.

Prefer implementing everything in:

.agent/src/ctf_runtime/

and the appropriate Kiro/MCP configuration.

3. WHAT WE ARE ACTUALLY BUILDING

We are NOT converting the CTF agent itself into an MCP-native reasoning engine.

We are creating a thin MCP gateway around the existing KiroBridge.

Current architecture:

Kiro
   X
   │
   │ no actual connection
   ▼
KiroBridge

Required architecture:

Kiro
   │
   │ MCP
   ▼
CTF Agent MCP Gateway
   │
   ▼
KiroBridge

KiroBridge already exists.

Reuse it.

Do not create a second bridge abstraction.

4. MCP TOOLS

Expose only these high-level tools:

ctf_start
ctf_step
ctf_run
ctf_state
ctf_hypotheses
ctf_evidence
ctf_progress
ctf_result

You may add a small number of read-only diagnostic tools if genuinely necessary, but keep the interface minimal.

Absolutely DO NOT expose:
execute_pwsh
shell
bash
powershell
subprocess
curl
raw_http
browser
python
arbitrary filesystem execution
arbitrary network execution
tool_call
execute_command

The MCP server must NOT become another arbitrary execution gateway.

5. TOOL RESPONSIBILITIES
ctf_start

Starts a new AgentSession.

It should accept only challenge-level information such as:

challenge_id
challenge_description
hints
resources
category
optional metadata

It must initialize the existing runtime.

It must NOT accept arbitrary executable code.

It must NOT allow Kiro to supply its own tool implementation.

It must use the server/operator-owned trusted adapter configuration.

Return:

session_id
challenge_id
status
initial_state
available_agent_capabilities
ctf_step

Advance the existing agent by exactly one reasoning/execution step.

It must call the existing:

AgentSession.step()

Do not duplicate the ReasoningLoop.

Return useful state such as:

session_id
step
hypothesis_state
pending_actions
latest_observation
latest_evidence
verification_state
progress
ctf_run

Run the existing autonomous solver until one of:

VERIFIED
BLOCKED
BUDGET_EXHAUSTED
FAILED

or the existing runtime's equivalent terminal states.

Do NOT implement a second solving loop in the MCP server.

Delegate to:

AgentSession.run()

Return the final structured result.

ctf_state

Read-only.

Return the current agent state.

ctf_hypotheses

Read-only.

Return current hypotheses and their states.

Preserve distinctions such as:

VERIFIED
SUPPORTED
PLAUSIBLE
UNRESOLVED
DISPROVEN
BLOCKED
ENVIRONMENTAL_FAILURE
TOOL_FAILURE

Do not collapse all failures into DISPROVEN.

ctf_evidence

Read-only.

Return the evidence ledger relevant to the current session.

ctf_progress

Read-only.

Return concise progress information:

current phase
current hypothesis
actions performed
actions remaining/budget
verification state
stall state
escalation state
ctf_result

Read-only final result.

It must distinguish:

verified flag
candidate flag
no flag
blocked
failed

A candidate string must NEVER automatically become a verified flag.

Verification remains owned by the existing Verification/Stopping Controller.

6. TRUST BOUNDARY

The MCP server is an untrusted interface boundary.

Everything coming from Kiro must be treated as untrusted input.

Validate:

challenge ID
challenge description
resource metadata
resource paths
strings
sizes
session IDs
tool arguments
malformed requests
unexpected fields

Never allow path traversal such as:

../../

Never allow arbitrary host/network configuration from the MCP client to override the trusted environment.

Never allow the client to register a new adapter.

Never allow the client to modify TrustKernel policy.

Never allow the client to modify verification rules.

7. TRUSTED EXECUTION

Trusted execution must remain:

ReasoningLoop
    ↓
ActionPlanner
    ↓
TrustKernel
    ↓
AdapterRegistry
    ↓
Trusted Adapter

The MCP layer must NEVER execute the action itself.

For example, if the LLM proposes:

execute_pwsh

the MCP server must not execute it.

The proposal must go through the existing validation/planning/trust pipeline.

8. KIRO BYPASS PROBLEM

We previously discovered a real runtime failure:

AGENT_BYPASSED

Kiro's LLM was able to directly use:

execute_pwsh

and other tools to solve a CTF while completely bypassing:

ReasoningLoop
ActionPlanner
TrustKernel
Evidence
Verification
Runtime Journal

This must NOT happen during an Agent-controlled CTF session.

Therefore create a clear CTF Agent Mode operating policy for Kiro.

When an active CTF Agent session exists:

Kiro must not independently solve the challenge.
Kiro must not invoke native shell/execution tools for the challenge.
Kiro must not use arbitrary MCP tools to attack the target.
Kiro must communicate with the CTF Agent through the exposed CTF MCP interface.

Important:

Do not falsely claim that a steering/instruction file technically disables Kiro's native tools.

It is a behavioral policy, not a hard security boundary.

Document this distinction explicitly.

If Kiro's current configuration supports disabling/restricting tools for a mode/session, inspect the available mechanism and use it.

Do not invent a Kiro configuration format.

9. MCP SERVER TRANSPORT

Inspect the current Kiro MCP configuration conventions in the workspace/environment.

Prefer standard local MCP communication, such as:

stdio

if supported by the current Kiro integration.

Do not assume a configuration filename or schema.

First inspect existing .kiro configuration and documentation.

If an MCP configuration already exists, integrate with it.

If none exists, create the smallest correct configuration required by the current Kiro environment.

Do not invent unsupported Kiro settings.

10. SERVER PROCESS

Create a minimal MCP server implementation around KiroBridge.

Conceptually:

MCP request
    ↓
validate
    ↓
KiroBridge
    ↓
AgentSession

The MCP server should contain almost no CTF intelligence.

It should primarily perform:

protocol handling
input validation
session lookup
KiroBridge calls
structured output serialization
error handling
audit logging

Do not move reasoning logic into the MCP server.

11. LLM BOUNDARY

Reuse the existing:

LLMReasoningSource
LLMClient
ModelRouter

Do not create another LLM reasoning abstraction.

The LLM must receive state/context, not executable handles.

The LLM must produce validated structured proposals.

The existing validators/planner must remain authoritative.

The LLM must never receive:

shell handles
subprocess objects
network sockets
Python callable objects
filesystem handles
adapter objects

Only safe textual/structured context should cross the boundary.

12. MODEL ROUTING

Preserve the existing model-routing architecture.

Do NOT hard-code:

web → model X
crypto → model Y
pwn → model Z

The current architecture deliberately uses runtime signals such as:

stall
uncertainty
difficulty
failure class
novelty
budget pressure

to determine escalation.

Preserve that.

Do not redesign the router.

For the integration test, use the existing scripted/fake LLM client first.

Then perform a real-provider integration only after the MCP transport works.

13. SPECIALIST MODE

For the first MCP integration test:

use_specialist_base=False

This isolates the real LLM reasoning path.

Once that works:

use_specialist_base=True

and verify that specialists remain advisors and cannot bypass the planner/kernel.

Do not modify specialist architecture.

14. RUNTIME JOURNAL

Every MCP-started session must retain the existing runtime journal.

The journal should allow us to reconstruct:

challenge
model
reasoning source
hypothesis
proposal
action fingerprint
planner decision
adapter
observation
evidence
impact
verification
escalation

The MCP server itself should also record enough information to prove:

MCP → KiroBridge → AgentSession

for every session.

Do not fabricate execution records.

15. SESSION ISOLATION

Multiple challenges must not accidentally share:

hypotheses
evidence
session state
runtime journal
verification state
resources
authentication context

Each ctf_start must create a unique session.

A session must not be reused for a different challenge.

Implement safe lifecycle handling:

CREATED
RUNNING
VERIFIED
BLOCKED
FAILED
CLOSED

using the existing session semantics where possible.

Do not duplicate state machines unnecessarily.

16. RESOURCE HANDLING

The agent already supports challenge resources.

Reuse the existing resource materialization mechanism.

Do not allow arbitrary client-controlled paths to escape the intended resource boundary.

For uploaded challenge files:

Kiro
 ↓
ctf_start
 ↓
validated resource
 ↓
AgentSession
 ↓
existing resource materialization

Do not create a second file ingestion subsystem.

17. TESTS

Add MCP integration tests.

At minimum:

Test 1 — Full MCP pipeline
MCP
 ↓
KiroBridge
 ↓
AgentSession
 ↓
LLM proposal
 ↓
Planner
 ↓
TrustKernel
 ↓
trusted adapter
 ↓
observation
 ↓
evidence
 ↓
verification
 ↓
verified flag

Verify the flag is returned only after actual verification.

Test 2 — Malicious LLM proposal

LLM attempts:

execute_pwsh

Expected:

REJECTED

No execution occurs.

Test 3 — Fake flag

LLM claims:

flag = CTF{fake}

without evidence.

Expected:

NOT VERIFIED
Test 4 — MCP cannot execute shell

Attempt to invoke a nonexistent/forbidden MCP operation such as:

execute_pwsh

Expected:

unknown tool / rejected

and absolutely no subprocess execution.

Test 5 — Session isolation

Start:

challenge-A
challenge-B

Verify their:

hypotheses
evidence
journal
verification

remain isolated.

Test 6 — Runtime journal

Run one complete test session.

Verify the journal records the actual:

proposal
planner
adapter
observation
evidence
verification

chain.

Test 7 — Existing regression suite

Run:

all existing tests

and verify:

Phase 2 regressions
Phase 3 tests
Phase 4 tests
Phase 5 tests
runtime tests

remain green.

18. REAL CTF SMOKE TEST

Only after the deterministic tests pass:

Start the MCP server.
Connect it to Kiro.
Start a harmless/local authorized CTF challenge.
Use:
ctf_start
ctf_state
ctf_step
ctf_progress
ctf_result
Verify the actual runtime journal.

The first real test should NOT rely on Kiro manually solving anything.

The objective is to prove:

Kiro
 → MCP
 → KiroBridge
 → AgentSession
 → LLMReasoningSource
 → ReasoningLoop
 → Planner
 → TrustKernel
 → Adapter
 → Evidence
 → Verification
19. BYPASS AUDIT

After integration, deliberately attempt to reproduce the previous bypass.

Try to make Kiro solve the same authorized/local challenge using:

execute_pwsh

or another direct execution mechanism.

Determine whether the current Kiro configuration allows it.

If it does, report:

BYPASS POSSIBLE

Do NOT falsely mark the system as fully enforced.

Then document exactly what is:

technically enforced by the agent

versus:

policy-enforced by Kiro

This distinction is critical.

20. DO NOT DO THESE THINGS

Do NOT:

rewrite the TrustKernel
rewrite ReasoningLoop
rewrite specialists
add another planner
add another evidence system
add another verification system
add another LLM boundary
add arbitrary shell access to MCP
expose raw subprocess through MCP
expose raw HTTP through MCP
give Kiro direct adapter handles
fine-tune a model
ingest external CTF corpora
modify the Phase 1–5 architecture
add fake "autonomous" behavior
fabricate execution results
claim tool isolation that is not technically enforced
modify frozen core merely to make integration easier
21. ACCEPTANCE CRITERIA

The implementation is complete only when all of the following are true:

[ ] Kiro can discover the CTF MCP server.
[ ] Kiro can start a CTF session.
[ ] Kiro can advance/run the agent.
[ ] Kiro can inspect state.
[ ] Kiro can inspect hypotheses.
[ ] Kiro can inspect evidence.
[ ] Kiro can inspect progress.
[ ] Kiro can retrieve the final result.
[ ] No shell execution primitive is exposed by the CTF MCP server.
[ ] No arbitrary network primitive is exposed by the CTF MCP server.
[ ] LLM proposals still pass through existing validation/planner.
[ ] Actions still pass through TrustKernel.
[ ] Verification remains authoritative.
[ ] Fake flags cannot become verified.
[ ] Environment/tool/rate-limit failures are not misclassified as hypothesis disproof.
[ ] Runtime journaling works.
[ ] Sessions are isolated.
[ ] Existing Phase 1–5 tests remain green.
[ ] Frozen-core fingerprint remains unchanged.
[ ] MCP integration tests pass.
[ ] A real/local authorized CTF smoke test passes.
[ ] The previous Kiro bypass is explicitly tested.
[ ] Any remaining bypass is documented honestly.
22. FINAL REPORT

At the end, report:

1. Files added
2. Files modified
3. Frozen files confirmed untouched
4. MCP tools exposed
5. MCP tools deliberately NOT exposed
6. Kiro configuration used
7. Runtime architecture
8. Security/trust boundary
9. Tests executed
10. Test results
11. Frozen-core fingerprint before/after
12. Real smoke-test result
13. Bypass test result
14. Known limitations
15. Exact command/config needed to start the MCP server

Do not claim success merely because unit tests pass.

The most important success criterion is proving that a real Kiro session actually travels through:

Kiro
→ MCP
→ KiroBridge
→ AgentSession
→ LLMReasoningSource
→ ReasoningLoop
→ Planner
→ TrustKernel
→ Trusted Adapter
→ Evidence
→ Verification

and does not silently bypass the agent.

Start with the audit. Do not modify files until you understand the existing runtime and current Kiro MCP configuration.