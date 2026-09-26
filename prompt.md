PHASE 2 — CTF AGENT TRUST & CONTROL FOUNDATION

You are now implementing Phase 2 of the autonomous CTF-solving agent.

WORKSPACE:

F:\mission-git-hackss\mission-git-hackss

PHASE 1 HAS ALREADY BEEN COMPLETED.

The Phase 1 audit artifacts are located at:

.agent_audit/

You MUST inspect the actual files inside .agent_audit/ before implementing anything.

============================================================
IMPORTANT: PHASE 1 IS THE DESIGN BASELINE
============================================================

The audit contains:

- architecture_recommendation.md
- schemas.md
- failures.jsonl
- trajectories.jsonl
- technique_memory.jsonl
- tool_memory.jsonl
- challenge-pattern knowledge
- category playbooks
- legacy conflict analysis
- other structured audit artifacts

Treat these artifacts as the current design baseline.

Do NOT redesign the architecture from scratch.

Do NOT blindly trust every historical claim.

Do NOT modify the original CTF corpus.

If you discover a genuine inconsistency between the audit artifacts, resolve it using the following priority:

1. Current task requirements
2. New CTF agent constitution
3. architecture_recommendation.md
4. schemas.md
5. structured historical evidence
6. older .kiro instructions

Document meaningful deviations instead of silently changing architecture.

============================================================
MISSION
============================================================

Build the TRUST / CONTROL FOUNDATION of the future CTF agent.

This phase is NOT the full autonomous solver.

We are building the machinery that prevents the future reasoning engine from:

- misclassifying failures
- falsely disproving hypotheses
- blindly retrying actions
- spraying candidate flags
- accepting plausible strings as flags
- repeating identical work
- allowing stale memory to override current evidence
- fabricating conclusions
- continuing after sufficient verification

The foundation must be deterministic wherever possible.

============================================================
DO NOT BUILD YET
============================================================

Do NOT build:

- full autonomous CTF solving
- multi-agent swarm
- RL/self-training
- model fine-tuning
- autonomous specialist routing
- massive MCP framework
- giant tool registry
- automatic challenge solving loop
- autonomous exploitation framework
- unnecessary UI
- unnecessary database infrastructure

We will build those later.

Keep Phase 2 focused.

============================================================
CORE PRINCIPLE
============================================================

The future agent MUST NOT allow raw tool output to directly change beliefs.

The mandatory conceptual pipeline is:

ACTION
  ↓
OBSERVATION
  ↓
RESULT CLASSIFICATION
  ↓
EVIDENCE
  ↓
HYPOTHESIS IMPACT
  ↓
MEMORY / STATE UPDATE
  ↓
DECISION

This separation is fundamental.

============================================================
THE MOST IMPORTANT INVARIANT
============================================================

A failed experiment does NOT automatically mean the hypothesis is false.

Example:

Hypothesis:

"SQL injection may be possible."

Action:

Send SQL injection probe.

Observation:

HTTP 429.

Correct:

RESULT_CLASS = RATE_LIMIT

HYPOTHESIS_IMPACT = UNRESOLVED

Reason:

The test was blocked by an environmental/target constraint.

Incorrect:

RESULT = SQLI_FALSE

This distinction must be enforced by the implementation.

============================================================
COMPONENTS TO IMPLEMENT
============================================================

Implement exactly these foundational components:

1. Result Classifier
2. Evidence Manager
3. Hypothesis Impact Engine
4. Failure Memory
5. Verification / Stopping Controller
6. Action Identity + Deduplication
7. Minimal State Model
8. Deterministic Test Harness

Keep them modular.

============================================================
1. RESULT CLASSIFIER
============================================================

Implement a deterministic result classifier.

It receives structured execution results.

Minimum result classes:

SUCCESS
TARGET_RESPONSE
INPUT_REJECTION
AUTH_FAILURE
AUTHZ_FAILURE
RATE_LIMIT
TIMEOUT
NETWORK_FAILURE
TOOL_FAILURE
ENVIRONMENT_FAILURE
STATE_CHANGE
AMBIGUOUS

You may add carefully justified classes if the audit demonstrates a need.

The classifier should NOT simply inspect one string.

It should consider structured fields such as:

- exit code
- stdout
- stderr
- HTTP status
- response headers
- response body
- timeout state
- process state
- network state
- tool availability
- execution metadata

Example input:

{
  "action_id": "a123",
  "tool": "http_request",
  "exit_code": 0,
  "http_status": 429,
  "stdout": "...",
  "stderr": "",
  "duration_ms": 220
}

Expected:

{
  "result_class": "RATE_LIMIT",
  "hypothesis_impact": "UNRESOLVED",
  ...
}

============================================================
CLASSIFIER DESIGN RULE
============================================================

Separate:

WHAT HAPPENED

from:

WHAT IT MEANS FOR A HYPOTHESIS.

The classifier determines the former.

The hypothesis-impact layer determines the latter.

Do NOT bury hypothesis-specific logic inside generic result classification.

============================================================
2. EVIDENCE MANAGER
============================================================

Implement structured evidence.

Every action should produce a chain:

Action
→ Observation
→ Classification
→ Evidence
→ Hypothesis impact

Evidence must contain provenance.

At minimum:

- evidence_id
- action_id
- timestamp
- source
- observation
- result_class
- status
- confidence/strength
- affected_hypotheses
- freshness
- provenance

Use the statuses defined by the audit where applicable:

VERIFIED
SUPPORTED
PLAUSIBLE
UNRESOLVED
DISPROVEN
BLOCKED
ENVIRONMENTAL_FAILURE
TOOL_FAILURE

Do not collapse these into a simple true/false model.

============================================================
3. HYPOTHESIS IMPACT ENGINE
============================================================

Implement a separate deterministic mechanism that maps classified observations to hypothesis impact.

Supported impact types:

SUPPORTS
WEAKENS
DISPROVES
UNRESOLVES
BLOCKS_TEST
NO_IMPACT

Examples:

HTTP 429
→ UNRESOLVED

HTTP 401
→ AUTH_FAILURE / BLOCKS_TEST

HTTP 403
→ AUTHZ_FAILURE or BLOCKS_TEST depending on evidence

Malformed input rejected by parser
→ INPUT_REJECTION

Successful exploit producing authoritative challenge output
→ SUPPORTS / VERIFIED depending on verification evidence

Tool executable missing
→ TOOL_FAILURE

Network unavailable
→ NETWORK_FAILURE

Do NOT automatically mark a hypothesis DISPROVEN merely because an action failed.

The system should be conservative about disproof.

============================================================
4. FAILURE MEMORY
============================================================

Implement append-only failure memory.

Use the actual historical failure records in:

.agent_audit/

especially:

failures.jsonl

Normalize them according to the audited schema.

Each record should approximately support:

failure_id
challenge
category
action
observation
result_class
initial_interpretation
correct_interpretation
root_cause
hypothesis_impact
recovery
lesson
confidence
source

Failure memory is a source of prior experience.

It is NOT an authority over current evidence.

For example:

Historical memory:
"Similar request was caused by database failure."

Current evidence:
"Database is healthy."

Current evidence wins.

============================================================
5. VERIFICATION / STOPPING CONTROLLER
============================================================

Implement the strongest anti-fabrication component.

The system must distinguish:

CANDIDATE FLAG

from:

VERIFIED FLAG

Never mark a flag verified merely because:

- it matches a regex
- it looks plausible
- decoding produced readable text
- a hash collision exists
- an LLM suggested it
- one of several format variants looks reasonable

Verification must require challenge-relevant evidence.

Possible verification sources:

- challenge verifier accepts it
- authoritative service returns it
- deterministic derivation establishes it
- exploit produces authoritative flag output
- cryptographic relationship proves it
- challenge-specific grading logic validates it

Represent:

candidate_flag
verification_evidence
verification_method
verification_status
verified_at

Statuses:

CANDIDATE
SUPPORTED
VERIFIED
REJECTED
INVALID

Once VERIFIED with minimum sufficient evidence:

STOP.

The system must not continue unnecessary exploration.

============================================================
ANTI-SPRAY
============================================================

Track:

- candidate value
- source
- supporting evidence
- verification status
- attempts
- rejection reason

Do not allow repeated flag attempts unless something materially changed:

- new evidence
- candidate changed
- challenge state changed
- verifier changed
- verification context changed

This is a control mechanism, not an LLM instruction.

============================================================
6. ACTION IDENTITY / DEDUPLICATION
============================================================

Implement action fingerprints.

Meaningfully equivalent actions should be recognized.

Fingerprint should consider relevant:

- tool
- target
- input
- objective
- environment state
- authentication/session state
- relevant parameters

Do not hash irrelevant timestamps or random execution metadata.

Track:

action_id
fingerprint
timestamp
status
result_class
state_before
state_after

Identical action + materially identical state:

→ DUPLICATE

Same action after meaningful state change:

→ ALLOWED

This is essential for preventing infinite loops.

============================================================
7. MINIMAL STATE MODEL
============================================================

Implement only the state needed for this phase.

At minimum:

ChallengeState
Hypothesis
Action
Observation
Evidence
Failure
FlagCandidate
VerificationState
EnvironmentState

Hypothesis should support:

- hypothesis_id
- statement
- status
- supporting_evidence
- contradicting_evidence
- unresolved_evidence
- last_updated

Action should support:

- action_id
- objective
- tool
- target
- input
- fingerprint
- prerequisites
- state_before
- state_after

Do not build an enormous object hierarchy.

============================================================
8. MEMORY RETRIEVAL
============================================================

For Phase 2, implement only the minimal interface required to retrieve failure experience.

Do NOT build the entire final memory system yet.

The interface should conceptually support:

retrieve_relevant_failures(context)

and return:

- matching historical failures
- confidence
- source
- lesson
- failure class
- relevant conditions

Current evidence MUST outrank memory.

Do not hard-code a numeric retrieval formula unless necessary.

============================================================
9. TEST HARNESS
============================================================

Create deterministic tests for the exact historical failure modes.

Minimum tests:

TEST 1 — RATE LIMIT

Hypothesis:
SQLi may exist.

Result:
HTTP 429.

Expected:
RATE_LIMIT
SQLi remains UNRESOLVED.

------------------------------------------------------------

TEST 2 — AUTHENTICATION

Result:
HTTP 401.

Expected:
AUTH_FAILURE
Hypothesis is NOT automatically disproven.

------------------------------------------------------------

TEST 3 — AUTHORIZATION

Result:
HTTP 403.

Expected:
AUTHZ_FAILURE / BLOCKED depending on context.

------------------------------------------------------------

TEST 4 — INPUT REJECTION

Malformed payload rejected.

Expected:
INPUT_REJECTION.

------------------------------------------------------------

TEST 5 — TOOL FAILURE

Executable unavailable.

Expected:
TOOL_FAILURE.

------------------------------------------------------------

TEST 6 — ENVIRONMENT FAILURE

Required environment unavailable.

Expected:
ENVIRONMENT_FAILURE.

------------------------------------------------------------

TEST 7 — NETWORK FAILURE

Target unreachable.

Expected:
NETWORK_FAILURE.

------------------------------------------------------------

TEST 8 — TIMEOUT

Action exceeds timeout.

Expected:
TIMEOUT.

------------------------------------------------------------

TEST 9 — SUCCESSFUL VERIFICATION

Authoritative challenge output contains flag.

Expected:

CANDIDATE
→ verification evidence
→ VERIFIED
→ STOP.

------------------------------------------------------------

TEST 10 — PLAUSIBLE BUT UNVERIFIED

Readable flag-like string produced.

Expected:

CANDIDATE or SUPPORTED

NOT VERIFIED.

------------------------------------------------------------

TEST 11 — COLLISION

A candidate exploits a weak checker but does not establish the intended answer.

Expected:

NOT VERIFIED.

------------------------------------------------------------

TEST 12 — DUPLICATE ACTION

Same action executed twice in same state.

Expected:

DUPLICATE.

------------------------------------------------------------

TEST 13 — STATE CHANGE

Same action executed after relevant environment/session state changes.

Expected:

ALLOWED.

------------------------------------------------------------

TEST 14 — MEMORY CONFLICT

Historical memory suggests a failure was a database issue.

Current evidence proves database is healthy.

Expected:

Current evidence wins.

------------------------------------------------------------

TEST 15 — FAILURE DOES NOT EQUAL DISPROOF

Generic tool failure occurs while testing a hypothesis.

Expected:

TOOL_FAILURE

Hypothesis remains:

UNRESOLVED.

============================================================
10. REGRESSION TEST AGAINST HISTORICAL FAILURES
============================================================

Use the actual 12 historical failure records from:

.agent_audit/

to construct regression cases wherever possible.

The goal is:

OLD FAILURE
→ NEW SYSTEM

and verify that the new system would classify the failure correctly.

Create a report:

historical_failure_regression.md

For each case record:

- historical situation
- old incorrect interpretation
- new classification
- new hypothesis impact
- expected recovery/control
- pass/fail

============================================================
11. INVARIANTS
============================================================

Implement tests for these non-negotiable invariants.

INVARIANT 1:

Environmental failure MUST NOT automatically disprove a hypothesis.

INVARIANT 2:

Tool failure MUST NOT automatically disprove a hypothesis.

INVARIANT 3:

A candidate flag MUST NOT become VERIFIED without verification evidence.

INVARIANT 4:

Identical actions in identical relevant state MUST NOT be silently repeated.

INVARIANT 5:

Historical memory MUST NOT override stronger current evidence.

INVARIANT 6:

Once minimum sufficient flag verification is achieved, the stopping controller MUST report STOP.

INVARIANT 7:

No component may fabricate evidence.

INVARIANT 8:

Every evidence record must have provenance.

============================================================
12. ENGINEERING
============================================================

Use the existing project language/tooling where appropriate.

Before choosing a new framework:

- inspect the existing repository
- inspect existing package/configuration
- reuse appropriate dependencies
- avoid unnecessary dependencies

Prefer:

- typed models
- deterministic functions
- small modules
- pure classification logic where possible
- explicit interfaces
- structured JSON/JSONL
- testable components

Do not couple the foundation to:

- Claude
- GPT
- Kiro
- a specific LLM provider

The eventual Strategic Brain should be replaceable.

============================================================
13. FILE ORGANIZATION
============================================================

Do not modify:

.kiro/
writeups/
existing challenge directories
historical artifacts
.agent_audit/

Create a separate implementation directory.

Prefer:

.agent/

unless the existing repository contains a stronger architectural convention.

Possible structure:

.agent/
├── state/
├── classification/
├── evidence/
├── hypothesis/
├── memory/
├── verification/
├── actions/
├── tests/
└── docs/

Adapt if the existing repository structure suggests a better organization.

============================================================
14. SAFETY / SCOPE
============================================================

All execution functionality is intended for authorized CTF environments and challenge artifacts.

Do not turn Phase 2 into a general-purpose real-world attack framework.

The executor interfaces should remain environment-scoped and auditable.

============================================================
15. IMPLEMENTATION PROCESS
============================================================

Before editing:

1. Inspect .agent_audit.
2. Inspect existing repository architecture.
3. Identify the appropriate implementation location.
4. Compare the audited schemas against the implementation plan.
5. Write a short implementation plan.

Then implement.

After implementation:

1. Run formatting/type checks if available.
2. Run all tests.
3. Run historical failure regression tests.
4. Inspect failures.
5. Fix genuine issues.
6. Re-run tests.
7. Verify no historical files were modified.

Do not stop after merely writing code.

The implementation is incomplete until the tests actually pass.

============================================================
16. DO NOT OVERBUILD
============================================================

This is extremely important.

Do NOT create:

- 50 abstractions
- 100 interfaces
- generic enterprise event buses
- distributed databases
- microservices
- unnecessary message queues
- complex plugin systems
- autonomous agents
- model routing systems

We are building a small, reliable kernel.

Correctness > abstraction.

Evidence > cleverness.

Determinism > unnecessary autonomy.

============================================================
17. FINAL REPORT
============================================================

When finished, provide:

1. Files created
2. Components implemented
3. Architecture diagram
4. Data schemas
5. Result classification rules
6. Hypothesis-impact rules
7. Failure-memory implementation
8. Verification logic
9. Anti-spray behavior
10. Action deduplication
11. State model
12. Tests
13. Historical regression results
14. Invariants verified
15. Any deviations from .agent_audit
16. Remaining limitations
17. Recommended Phase 3 architecture

Do NOT implement Phase 3.

STOP after Phase 2.

============================================================
SUCCESS CRITERIA
============================================================

Phase 2 is successful only if the system can reliably perform:

ACTION
 ↓
OBSERVATION
 ↓
CLASSIFICATION
 ↓
EVIDENCE
 ↓
HYPOTHESIS IMPACT
 ↓
STATE UPDATE
 ↓
VERIFICATION / CONTINUE / STOP

while preventing:

- false hypothesis disproof
- false flag verification
- blind flag spraying
- duplicate actions
- stale-memory override
- fabricated evidence
- uncontrolled retries

The foundation should be stable enough that a Strategic Brain can be connected to it in Phase 3 without redesigning these core controls.