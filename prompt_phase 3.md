PHASE 3 — STRATEGIC BRAIN + TRUSTED EXECUTION

Workspace:
F:\mission-git-hackss\mission-git-hackss

MODEL:
You are implementing Phase 3 using Sonnet 5.

IMPORTANT:
Phase 2 is COMPLETE and is the authoritative Trust & Control Foundation.

Do NOT redesign, weaken, bypass, or replace Phase 2.

==================================================
1. READ BEFORE IMPLEMENTING
==================================================

First inspect:

.agent/docs/design.md
.agent/docs/implementation_plan.md
.agent/docs/deviations.md
.agent/docs/historical_failure_regression.md

Then inspect the Phase 2 implementation:

.agent/src/ctf_agent/models.py
.agent/src/ctf_agent/kernel.py
.agent/src/ctf_agent/classifier.py
.agent/src/ctf_agent/impact.py
.agent/src/ctf_agent/hypothesis.py
.agent/src/ctf_agent/evidence.py
.agent/src/ctf_agent/failure_memory.py
.agent/src/ctf_agent/verification.py
.agent/src/ctf_agent/deduplication.py

Also inspect:

.agent/tests/

Phase 2 verification baseline:

- 74/74 tests passed
- 12/12 historical failure regressions passed
- Python compileall passed
- static audit passed
- .agent_audit/ was preserved
- Phase 3 was not previously implemented

Treat the existing Phase 2 implementation as the source of truth.

==================================================
2. PHASE 3 OBJECTIVE
==================================================

Build the first real autonomous reasoning and execution layer ON TOP OF the Phase 2 Trust Kernel.

The goal is NOT yet a complete general-purpose CTF solver.

The goal is to create the controlled machinery that can:

UNDERSTAND
→ FORM HYPOTHESES
→ SELECT THE NEXT USEFUL ACTION
→ EXECUTE IT
→ CLASSIFY THE RESULT
→ RECORD EVIDENCE
→ UPDATE HYPOTHESES
→ PLAN AGAIN
→ VERIFY
→ STOP

The architecture must remain:

Strategic Brain
      ↓
    Action
      ↓
Trusted Tool Adapter
      ↓
ExecutionResult
      ↓
Phase 2 Trust Kernel
      ↓
Classification
      ↓
Evidence
      ↓
Hypothesis Impact
      ↓
Continue / Stop

==================================================
3. NON-NEGOTIABLE ARCHITECTURAL RULE
==================================================

Phase 2 remains the authority.

No Phase 3 component may bypass:

- result classification
- evidence provenance
- hypothesis impact rules
- action deduplication
- candidate anti-spray controls
- verification
- STOP enforcement

The LLM is NOT the authority.

The planner is NOT the authority.

Memory is NOT the authority.

Specialists are NOT the authority.

Only the deterministic Trust Kernel may commit state transitions.

Core invariant:

ACTION
→ OBSERVATION
→ CLASSIFICATION
→ EVIDENCE
→ HYPOTHESIS IMPACT
→ STATE UPDATE
→ DECISION

Never:

RAW TOOL OUTPUT
→ BELIEF

Never:

LLM OUTPUT
→ VERIFIED FLAG

==================================================
4. COMPONENTS TO BUILD
==================================================

Implement these Phase 3 components.

-----------------------------------------------
A. TRUSTED TOOL ADAPTER
-----------------------------------------------

Create a narrow interface such as:

TrustedToolAdapter.execute(Action) -> ExecutionResult

The adapter must:

- execute only explicitly allowed tools
- validate tool identity
- validate action structure
- capture stdout
- capture stderr
- capture exit code
- capture HTTP status where applicable
- capture timeout
- capture network errors
- capture environment errors
- capture relevant state before/after execution
- preserve raw output
- return structured ExecutionResult
- never invent success
- never declare a flag verified
- never directly mutate hypotheses
- never directly create trusted evidence
- never bypass the Trust Kernel

Start small.

Prefer deterministic adapters for:

1. Python/local subprocess execution
2. HTTP requests
3. local file inspection

Do NOT build a giant plugin/MCP framework.

Do NOT connect unrestricted arbitrary internet exploitation.

Execution must remain inside explicitly configured CTF/authorized environments.

-----------------------------------------------
B. CONTEXT MODEL
-----------------------------------------------

Create a structured ChallengeContext / ContextModel.

It should represent:

- challenge name
- category
- points
- solves
- description
- hints
- flag format
- files
- URLs
- available tools
- environment state
- relevant constraints
- discovered observations
- evidence
- hypotheses
- completed actions
- blocked prerequisites
- candidate flags
- verification state

Do NOT flatten all of this into one giant prompt string.

The model must distinguish states such as:

KNOWN
SUPPORTED
PLAUSIBLE
UNRESOLVED
BLOCKED
DISPROVEN
VERIFIED

Current evidence must outrank historical memory.

-----------------------------------------------
C. HYPOTHESIS ENGINE
-----------------------------------------------

Implement structured hypotheses containing at minimum:

- hypothesis ID
- statement
- mechanism
- category/technique if known
- supporting evidence IDs
- weakening evidence IDs
- blocking conditions
- required prerequisites
- possible discriminating tests
- current state
- priority/confidence where useful

Important:

The LLM may propose a hypothesis.

The LLM may NOT arbitrarily mark it:

DISPROVEN
or
VERIFIED.

Only valid Phase 2-compatible evidence may cause those transitions.

Remember:

TOOL FAILURE ≠ HYPOTHESIS DISPROVEN

ENVIRONMENT FAILURE ≠ HYPOTHESIS DISPROVEN

TIMEOUT ≠ HYPOTHESIS DISPROVEN

RATE LIMIT ≠ HYPOTHESIS DISPROVEN

AUTH FAILURE ≠ HYPOTHESIS DISPROVEN

These normally mean the test was blocked or unresolved.

-----------------------------------------------
D. ACTION PLANNER
-----------------------------------------------

Build an evidence-aware action planner.

For every proposed action consider:

- objective
- target
- input
- relevant parameters
- prerequisites
- expected observation
- hypotheses being tested
- hypotheses being discriminated
- relevant environment/state
- approximate cost
- whether an equivalent action already exists

Primary planning principle:

CHEAPEST DISCRIMINATING TEST FIRST.

The planner should prefer actions that:

- answer an important uncertainty
- distinguish competing hypotheses
- are cheap
- are reversible
- have clear expected observations
- require minimal setup
- produce high-value evidence

Do NOT make the planner perform elaborate mathematical utility calculations for every action.

Simple deterministic heuristics are preferred.

The planner must reject:

- duplicate actions
- actions with no meaningful objective
- actions with unmet prerequisites
- blind payload spraying
- repeated equivalent tests
- actions after verified STOP

-----------------------------------------------
E. LLM REASONING BOUNDARY
-----------------------------------------------

If/when an LLM is integrated, enforce a strict boundary.

LLM MAY:

- understand challenge descriptions
- summarize context
- identify possible mechanisms
- propose hypotheses
- propose actions
- interpret classified observations
- suggest next actions
- prioritize unresolved hypotheses
- summarize reasoning

LLM MAY NOT:

- directly mutate TrustKernel state
- directly create trusted evidence
- declare a candidate verified
- bypass verification
- bypass action deduplication
- bypass anti-spray
- bypass prerequisites
- fabricate observations
- fabricate tool results
- treat tool/environment failure as disproof
- overwrite current evidence using memory
- execute arbitrary commands outside the trusted adapter boundary

All LLM outputs must be converted into typed proposals.

Every proposal must pass deterministic validation before execution/state mutation.

-----------------------------------------------
F. PERSISTENT STATE JOURNAL
-----------------------------------------------

Create an append-only runtime journal under:

.agent/runtime/

It should record:

- actions
- observations
- classifications
- evidence
- hypothesis transitions
- verification attempts
- control decisions
- relevant state changes

Use structured JSONL or another simple append-only format.

Implement safe/atomic append behavior.

If file locking is necessary, implement it.

The journal must not modify:

.agent_audit/

Historical Phase 1 data remains read-only.

-----------------------------------------------
G. MEMORY RETRIEVAL
-----------------------------------------------

Implement minimal retrieval over the Phase 1 corpus.

Useful sources include:

.agent_audit/

and the relevant Phase 1 datasets:

- techniques
- failures
- trajectories
- tool knowledge
- challenge patterns

Memory should be ADVISORY.

Memory may suggest:

- likely techniques
- similar challenges
- historical failure patterns
- useful tools
- possible mechanisms

Memory must NEVER directly determine current truth.

Priority must remain:

CURRENT VERIFIED EVIDENCE
>
CURRENT OBSERVATIONS
>
CHALLENGE-SPECIFIC VERIFIED EXPERIENCE
>
GENERAL VERIFIED TECHNIQUES
>
HISTORICAL PRIORS
>
PLAUSIBLE KNOWLEDGE

Do NOT introduce vector databases/embeddings unless there is a concrete demonstrated need.

A simple retrieval mechanism is preferred for Phase 3.

-----------------------------------------------
H. REASONING LOOP
-----------------------------------------------

Implement the first controlled orchestration loop.

Conceptually:

1. LOAD CHALLENGE
2. BUILD CONTEXT
3. UNDERSTAND
4. FORM INITIAL HYPOTHESES
5. RANK UNRESOLVED HYPOTHESES
6. SELECT CHEAPEST DISCRIMINATING TEST
7. VALIDATE ACTION
8. CHECK DEDUPLICATION
9. EXECUTE THROUGH TRUSTED ADAPTER
10. CLASSIFY RESULT
11. RECORD EVIDENCE
12. UPDATE HYPOTHESES
13. CHECK VERIFICATION
14. IF VERIFIED → STOP
15. OTHERWISE PLAN NEXT ACTION
16. REPEAT

The loop must preserve state across iterations.

It must NOT blindly restart reasoning after every action.

It must know:

- what has already been tested
- what was learned
- what remains unresolved
- which actions are blocked
- which hypotheses are weakened/disproven
- which tools are available
- what environment state changed

-----------------------------------------------
I. STOP CONDITIONS
-----------------------------------------------

The system MUST stop when:

- a candidate is properly verified

It must safely stop or enter a blocked state when:

- no useful action remains
- prerequisites are unavailable
- environment is blocked
- action budget is exhausted
- challenge state is irrecoverably blocked

IMPORTANT:

Do NOT claim:

"challenge impossible"

merely because:

- a tool failed
- network failed
- authentication failed
- environment is unavailable
- one hypothesis failed
- one technique failed

Those should be diagnosed correctly.

-----------------------------------------------
5. ANTI-LOOP / ANTI-SPRAY
-----------------------------------------------

The agent must never repeatedly perform:

same action
+
same state
+
same objective

unless something materially changed.

Use Phase 2 action fingerprints.

The agent should detect:

- repeated payload variants with no new information
- repeated failed tools
- cycling between the same hypotheses
- repeatedly testing already-disproven mechanisms
- repeatedly attempting blocked actions
- repeatedly generating the same candidate flag

When a branch becomes low-value or blocked:

CLOSE THE BRANCH

Do not claim the entire challenge is impossible.

-----------------------------------------------
6. STATE-AWARE PLANNING
-----------------------------------------------

Relevant state must affect planning.

Examples:

- authentication/session state
- environment revision
- available tools
- challenge revision
- files extracted
- services started/stopped
- credentials obtained
- previous state-changing actions

A state-changing action may make a previously duplicated action valid again.

Do not use timestamps/random IDs as meaningful state changes.

Respect the Phase 2 fingerprinting model.

-----------------------------------------------
7. TESTING
-----------------------------------------------

Preserve every existing Phase 2 test.

Add Phase 3 tests for:

### Tool adapter

- successful execution
- nonzero exit
- timeout
- network failure
- HTTP 429
- HTTP 401
- HTTP 403
- malformed input
- missing tool
- missing environment

### Planner

- chooses a discriminating test
- prefers cheap test when appropriate
- rejects duplicate
- rejects missing prerequisite
- rejects blind repetition
- respects relevant state
- respects STOP

### Hypothesis engine

- creates hypothesis
- supports hypothesis with evidence
- weakens hypothesis
- blocks test
- does not disprove from environment failure
- does not disprove from tool failure
- does not accept arbitrary LLM state mutation

### Memory

- retrieves relevant historical knowledge
- historical memory remains advisory
- current evidence overrides historical memory
- historical files remain unchanged

### Verification

- candidate cannot self-verify
- fabricated evidence rejected
- failed tool result cannot verify
- plausible flag cannot verify
- verified candidate produces STOP

### Loop

- action → observation → classification → evidence → impact → state update
- multiple iterations preserve state
- duplicate actions are blocked
- blocked branches do not poison unrelated hypotheses
- verified flag terminates execution

-----------------------------------------------
8. SYNTHETIC END-TO-END TESTS
-----------------------------------------------

Create at least THREE deterministic local/synthetic CTF scenarios.

Scenario A:
WEB

Example structure:
- controlled local HTTP service
- discoverable vulnerability
- evidence-based exploitation
- deterministic flag verification

Scenario B:
CRYPTO or REVERSE

Use a local deterministic challenge where:
- an initial hypothesis is wrong or incomplete
- an experiment provides discriminating evidence
- the agent must adapt

Scenario C:
FORENSICS or STEGO

Use a deterministic artifact where:
- multiple possible mechanisms exist
- the agent must select useful analysis
- final flag verification is authoritative

These must be local/synthetic.

Do NOT attack real third-party systems.

The purpose is to validate the architecture, not demonstrate offensive capability against real targets.

-----------------------------------------------
9. EVALUATION METRICS
-----------------------------------------------

Measure at minimum:

- successful termination rate
- false verification rate
- false disproof rate
- duplicate action rate
- unnecessary action rate
- actions to solution
- verification latency
- blocked-branch handling
- state consistency

Do NOT optimize for:

"number of tools used"

Optimize for:

CORRECTNESS
+
EVIDENCE QUALITY
+
INFORMATION GAIN
+
LOW DUPLICATION
+
LOW FALSE DISPROOF
+
ZERO FALSE VERIFICATION

-----------------------------------------------
10. DO NOT OVERBUILD
-----------------------------------------------

Do NOT implement:

- multi-agent swarm
- RL
- model fine-tuning
- autonomous self-training
- dozens of specialists
- giant plugin architecture
- unrestricted MCP framework
- vector database
- distributed execution
- Kubernetes
- cloud deployment
- full production UI
- full autonomous CTF platform

Do not blindly ingest all ~1310 Python files.

Do not rebuild Phase 1.

Do not rebuild Phase 2.

Keep the implementation modular and understandable.

-----------------------------------------------
11. FILE BOUNDARY
-----------------------------------------------

Prefer:

.agent/
    src/ctf_agent/
    tests/
    runtime/
    docs/

Do NOT modify:

.agent_audit/
.kiro/
existing writeups/
historical challenge artifacts

unless a test fixture absolutely requires a new file under .agent/.

-----------------------------------------------
12. CODE QUALITY
-----------------------------------------------

Prefer:

- small modules
- typed interfaces
- deterministic behavior
- explicit state transitions
- clear provenance
- testable components
- minimal dependencies
- no hidden global state
- no magical abstractions

Do not add dependencies just for convenience.

Keep Phase 2's zero-third-party-dependency property unless a Phase 3 dependency is genuinely necessary.

If adding one, document why.

-----------------------------------------------
13. FINAL VALIDATION
-----------------------------------------------

Before declaring Phase 3 complete:

1. Run ALL existing Phase 2 tests.
2. Run ALL Phase 3 tests.
3. Run historical regressions.
4. Run Python compileall.
5. Run static audit.
6. Verify .agent_audit/ was not modified.
7. Verify existing challenge/writeup files were not modified.
8. Verify no post-STOP actions generate new evidence.
9. Verify LLM proposals cannot bypass deterministic controls.
10. Verify tool adapters cannot directly mutate hypotheses/evidence.
11. Verify duplicate actions remain blocked.
12. Verify environment/tool failures do not become automatic disproof.

-----------------------------------------------
14. PHASE 3 REPORT
-----------------------------------------------

Create:

.agent/docs/phase3_report.md

Include:

- files created
- architecture
- components implemented
- Trust Kernel integration
- tool execution boundary
- LLM boundary
- context model
- hypothesis model
- planner behavior
- state journal
- memory retrieval
- reasoning loop
- anti-loop behavior
- tests
- synthetic CTF scenarios
- evaluation metrics
- results
- limitations
- known gaps
- deviations from this specification
- exact recommendation for Phase 4

Be honest about anything incomplete.

Do not claim autonomous solving capability unless the synthetic end-to-end tests actually demonstrate it.

-----------------------------------------------
15. FINAL STOP
-----------------------------------------------

Phase 3 ends after:

- implementation
- tests
- regression validation
- static validation
- report

Do NOT automatically start Phase 4.

Do NOT add specialist agents yet.

STOP after Phase 3.