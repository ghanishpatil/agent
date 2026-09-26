PHASE 5 — FULL AUTONOMOUS CTF SOLVER + EVALUATION

Workspace:
F:\mission-git-hackss\mission-git-hackss

MODEL:
GPT-5.6 Sol — High

============================================================
MISSION
============================================================

This is the FINAL PHASE of the original 5-phase architecture.

Phase 1 — Corpus & Knowledge Audit: COMPLETE
Phase 2 — Trust & Control Foundation: COMPLETE
Phase 3 — Strategic Brain + Execution: COMPLETE
Phase 4 — Specialist Intelligence: COMPLETE
Phase 5 — Full Autonomous Solver + Evaluation: THIS PHASE

Your job is NOT to redesign the previous architecture.

Your job is to integrate the completed components into a genuinely autonomous CTF-solving system and rigorously evaluate whether it can solve unseen challenges without human intervention.

The final system must:

INPUT
→ understand challenge
→ construct hypotheses
→ select specialists
→ retrieve relevant knowledge
→ plan actions
→ execute through trusted tools
→ classify results
→ update evidence
→ update hypotheses
→ adapt strategy
→ recover from failures
→ avoid duplicate work
→ identify dead ends
→ generate candidate
→ independently verify candidate
→ stop
→ return flag

The Strategic Brain remains the coordinator.

The Phase 2 Trust Kernel remains the authority.

============================================================
0. ABSOLUTE ARCHITECTURAL RULE
============================================================

The architecture is:

                    CTF INPUT
                        │
                        ▼
                CONTEXT MODEL
                        │
                        ▼
                 STRATEGIC BRAIN
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
     HYPOTHESES     SPECIALISTS    MEMORY
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  ACTION PLANNER
                        │
                        ▼
                TRUSTED ADAPTERS
                        │
                        ▼
                 PHASE 2 KERNEL
                        │
                        ▼
                 RESULT CLASSIFIER
                        │
                        ▼
                     EVIDENCE
                        │
                        ▼
                HYPOTHESIS IMPACT
                        │
                        ▼
                 STRATEGIC BRAIN
                        │
                       ↺
                        │
                        ▼
                    CANDIDATE
                        │
                        ▼
                  VERIFICATION
                        │
                        ▼
                      STOP
                        │
                        ▼
                     FLAG

No component may bypass this architecture.

============================================================
1. READ EVERYTHING FIRST
============================================================

Before changing anything, inspect the actual implementation.

Read:

.agent/README.md

.agent/docs/

especially:

- Phase 2 documentation
- Phase 3 documentation
- Phase 4 documentation
- implementation plans
- design documents
- deviations
- regression documentation
- phase reports

Inspect:

.agent/src/ctf_agent/

including:

- models
- classifier
- impact engine
- hypothesis system
- evidence manager
- failure memory
- verification
- deduplication
- kernel
- reasoning loop
- context model
- planner
- trusted adapters
- LLM boundary
- journal
- memory retrieval
- specialists
- specialist registry
- specialist selection
- specialist reasoning source

Inspect ALL tests.

Do not rely on summaries alone.

Understand the real implementation before modifying it.

============================================================
2. FREEZE PHASE 2 AND PHASE 3
============================================================

Phase 2 and Phase 3 are architectural foundations.

Do NOT rewrite them merely to make Phase 5 easier.

Do NOT replace the Trust Kernel.

Do NOT weaken verification.

Do NOT remove evidence provenance.

Do NOT remove action deduplication.

Do NOT remove anti-spray behavior.

Do NOT allow LLM output to directly mutate trusted state.

Do NOT replace deterministic controls with prompts.

If an integration problem exists:

FIRST:
find the smallest additive integration point.

SECOND:
document it.

THIRD:
add regression coverage.

Only modify existing code if genuinely necessary.

============================================================
3. FREEZE PHASE 4 SPECIALIST BOUNDARY
============================================================

Specialists remain advisors.

They may:

- analyze
- propose mechanisms
- propose hypotheses
- propose tests
- propose actions
- interpret evidence
- retrieve knowledge

They may NOT:

- execute tools
- mutate trusted evidence
- mutate kernel state
- verify flags
- bypass planner
- bypass deduplication
- bypass verification
- declare challenge solved

The flow remains:

SPECIALIST
→ PROPOSAL
→ STRATEGIC BRAIN
→ PLANNER
→ TRUSTED EXECUTOR
→ KERNEL

============================================================
4. BUILD THE REAL AUTONOMOUS REASONING LOOP
============================================================

Phase 3 and Phase 4 already provide most components.

Phase 5 must make the complete system operate as one autonomous solver.

The loop should conceptually be:

while not terminal:

    observe current state

    understand current challenge

    retrieve relevant knowledge

    determine relevant specialists

    ask specialists for analysis

    maintain hypotheses

    identify uncertainty

    generate candidate actions

    eliminate:

        duplicate actions
        impossible actions
        missing-prerequisite actions
        low-value actions
        unsupported actions
        already-resolved branches

    select the best next action

    execute through trusted adapter

    classify result

    convert result into evidence

    determine hypothesis impact

    update state

    detect:

        progress
        contradiction
        failure
        environmental blockage
        tool failure
        dead end
        repeated loop
        new attack surface
        candidate

    adapt strategy

    verify when appropriate

    stop when verified

Do not implement this as uncontrolled recursive LLM calls.

The deterministic system controls the loop.

============================================================
5. LLM ROLE
============================================================

The LLM is the reasoning/planning component.

It is NOT the trust authority.

The LLM may:

- understand descriptions
- reason about mechanisms
- propose hypotheses
- propose experiments
- interpret observations
- select among permitted strategies
- suggest specialist usage
- identify missing information
- propose next actions

The LLM may NOT:

- directly execute arbitrary commands
- directly mutate evidence
- directly verify a flag
- declare a flag correct
- bypass planner constraints
- bypass action deduplication
- override current evidence
- convert an untrusted observation into trusted evidence

All LLM output must cross typed/deterministic boundaries.

============================================================
6. CHALLENGE INPUT CONTRACT
============================================================

The solver must support a challenge package containing, where available:

- challenge name
- category
- description
- points
- solves
- hints
- flag format
- URLs
- downloadable files
- source code
- binaries
- archives
- images
- PCAPs
- APKs
- documents
- credentials supplied by the challenge
- environment information
- attempt limits
- known constraints

The solver must NOT assume all fields exist.

Missing information is part of the problem.

The Context Model should explicitly track:

KNOWN
UNKNOWN
ASSUMED
INFERRED
VERIFIED

Do not silently convert assumptions into facts.

============================================================
7. CONTEXT UNDERSTANDING
============================================================

Before significant exploitation, establish a challenge model.

Determine:

- likely category/categories
- available artifacts
- remote/local targets
- authentication requirements
- tools available
- obvious constraints
- attempt limits
- potential attack surfaces
- hints and their implications
- known/unknown information

Avoid premature commitment.

Example:

Do NOT:

"Category = web → SQL injection."

Instead:

"Web challenge.
Observed parameter X.
Response behavior Y.
Potential mechanisms A/B/C.
Need discriminating test."

============================================================
8. HYPOTHESIS MANAGEMENT
============================================================

Maintain explicit hypotheses.

Each hypothesis must track:

- mechanism
- status
- supporting evidence
- conflicting evidence
- unresolved questions
- proposed tests
- prerequisites
- confidence/priority
- origin
- last tested state

Use the established state vocabulary where applicable:

VERIFIED
SUPPORTED
PLAUSIBLE
UNRESOLVED
DISPROVEN
BLOCKED
ENVIRONMENTAL FAILURE
TOOL FAILURE

Do NOT collapse these states.

Especially:

FAILED EXPERIMENT ≠ DISPROVEN HYPOTHESIS

Example:

SQLi test → HTTP 429

Correct:

experiment = RATE_LIMIT
hypothesis = UNRESOLVED/BLOCKED

Incorrect:

hypothesis = DISPROVEN

============================================================
9. MAXIMUM INFORMATION PER ACTION
============================================================

Every action should have an objective.

Prefer:

CHEAPEST DISCRIMINATING TEST

over:

MOST POWERFUL TOOL

over:

RANDOM EXPLORATION

For competing hypotheses:

H1: SQL injection
H2: template injection
H3: literal reflection

select a test that distinguishes them.

Do not ask the LLM to perform elaborate mathematical utility calculations for every action.

Use practical heuristics based on:

- expected information gain
- cost
- prerequisites
- risk
- novelty
- branch elimination
- evidence quality

============================================================
10. ACTION DEDUPLICATION
============================================================

The solver must not repeat equivalent actions.

Deduplication must consider:

- objective
- tool
- target
- input
- relevant parameters
- prerequisites
- environment revision
- authentication/session state
- challenge revision
- relevant state identity

An action may be repeated ONLY if something materially changed.

Examples:

VALID:

same request after authentication changed

VALID:

same exploit after target version changed

VALID:

same test after a prerequisite was satisfied

INVALID:

same payload
same target
same state
same objective
→ repeat

Do not allow LLM enthusiasm to override deduplication.

============================================================
11. DEAD-END DETECTION
============================================================

Detect branches that have become low-value or disproven.

A dead-end should be closed when:

- hypothesis is DISPROVEN
- prerequisite cannot be satisfied
- repeated evidence contradicts the mechanism
- branch has no useful remaining discriminating tests
- cost exceeds reasonable value
- mechanism is incompatible with verified challenge behavior

Do NOT claim:

"Impossible."

Instead record:

"Current evidence makes this branch non-productive."

Allow reopening only when materially new evidence appears.

============================================================
12. FAILURE DIAGNOSIS
============================================================

Classify failures before changing strategy.

Distinguish:

TECHNIQUE FAILURE
INPUT FAILURE
TARGET REJECTION
AUTH FAILURE
RATE LIMIT
NETWORK FAILURE
ENVIRONMENT FAILURE
TOOL FAILURE
STATE CONFLICT
UNSUPPORTED ASSUMPTION
ACTUAL HYPOTHESIS CONTRADICTION

Example:

HTTP 429
→ RATE LIMIT

NOT:

SQLi disproven

Example:

binary tool crashes
→ TOOL FAILURE

NOT:

binary has no vulnerability

Example:

remote service unreachable
→ NETWORK/ENVIRONMENT FAILURE

NOT:

mechanism disproven

============================================================
13. STATE-AWARE PLANNING
============================================================

The agent must understand that the environment changes.

Track relevant state such as:

- authentication
- cookies
- tokens
- files created
- processes
- ports
- server state
- challenge state
- installed/available tools
- environment revision
- exploit state
- previous mutations

An action valid before authentication may be invalid afterward.

An action previously blocked may become valid after satisfying a prerequisite.

Do not treat every action as stateless.

============================================================
14. PRECONDITIONS AND RECOVERY
============================================================

Before executing an action, verify prerequisites.

Examples:

- required file exists
- tool exists
- target reachable
- session available
- credentials available
- correct architecture
- required package available
- correct working directory

After destructive or uncertain experiments:

- detect state mutation
- restore known-good state where possible
- record state revision

Never blindly continue after an unknown environment mutation.

============================================================
15. SPECIALIST ORCHESTRATION
============================================================

Use Phase 4 specialists.

Initial specialists:

- Web
- Crypto
- Reverse
- Forensics
- Pwn

Select specialists based on evidence.

Do NOT invoke every specialist on every challenge.

Allow multiple specialists for cross-domain challenges.

Example:

Web
→ JWT identified

Crypto
→ token/signature mechanism analysis

Web
→ application-level consequence

Strategic Brain mediates all cross-specialist interaction.

============================================================
16. KNOWLEDGE RETRIEVAL
============================================================

Use the EXISTING corpus/memory created in previous phases.

This phase must NOT ingest the large external Jia Jie corpus yet.

Do NOT introduce external writeup ingestion in Phase 5.

We need a clean baseline first.

Memory is advisory.

Current evidence outranks historical memory.

If memory conflicts with current observations:

CURRENT EVIDENCE WINS.

============================================================
17. FLAG CANDIDATE GENERATION
============================================================

The solver must have a legitimate path from reasoning to candidate.

A candidate must include:

- candidate value
- origin
- hypothesis/mechanism
- evidence references
- derivation or extraction method
- target/challenge identity
- candidate state

A candidate is NOT trusted merely because:

- it looks like a flag
- it matches regex
- it contains FLAG{}
- an LLM suggested it
- a specialist suggested it
- a historical writeup contained it
- an emulator produced it
- it was found in a random string

============================================================
18. HARD VERIFICATION
============================================================

Every final flag must pass the existing Phase 2 verification architecture.

Valid verification may include:

- authoritative challenge response
- grading endpoint
- deterministic derivation
- cryptographic proof
- challenge-specific self-check
- authoritative local verifier
- verified grading logic

Weak evidence is insufficient.

Examples of insufficient verification:

- regex match
- plausible flag format
- readable text
- LLM confidence
- specialist confidence
- historical flag
- collision
- guess
- output that merely "looks right"

The solver must NEVER return a final flag without trusted verification.

============================================================
19. STOP CONDITION
============================================================

Once a flag is independently verified:

STOP.

Do NOT:

- continue exploring
- seek additional confirmation unnecessarily
- run unrelated tools
- modify the environment
- generate more candidates

Minimal sufficient verification is the goal.

The system should have an explicit terminal state.

============================================================
20. NO BLIND GUESSING
============================================================

The solver must never:

- brute-force flag strings
- spray payloads without evidence
- try endless encoding variants
- enumerate huge search spaces without a mechanism
- submit arbitrary candidates
- repeatedly retry identical failures

If no useful action exists:

the solver should enter a controlled:

BLOCKED / NEEDS_INFORMATION / EXHAUSTED

state rather than hallucinating a solution.

============================================================
21. ATTEMPT BUDGETS
============================================================

Respect challenge attempt limits.

Track:

- remote attempts
- submissions
- expensive actions
- network actions
- tool executions
- total actions
- specialist calls
- reasoning iterations

Do not spend remote attempts on low-confidence guesses.

The planner should prefer local proof before remote submission where possible.

============================================================
22. PARALLEL INVESTIGATION
============================================================

Support parallel analysis only when genuinely independent.

Example:

WEB:
inspect source

FORENSICS:
inspect uploaded archive

CRYPTO:
analyze token

These may proceed independently.

Do NOT parallelize dependent actions.

Example:

Do not launch five exploit attempts simultaneously when the result of one determines the next.

Parallelism must not break state consistency or deduplication.

============================================================
23. COST-AWARE EXPLORATION
============================================================

Actions have different costs.

Consider:

- execution time
- compute
- network
- remote attempts
- destructive risk
- setup cost
- human-equivalent effort

Prefer cheap discriminating tests.

Do not over-investigate after sufficient evidence exists.

============================================================
24. AUTONOMY REQUIREMENT
============================================================

The final system must operate from a challenge package without a human manually directing each step.

Human input should be limited to providing:

- challenge
- files/resources
- credentials explicitly supplied for the challenge
- permitted environment configuration

After initialization, the agent should determine its own:

- specialist selection
- hypotheses
- actions
- tool usage
- experiment order
- recovery
- verification
- stopping

No human should need to say:

"Now try SQLi."

or:

"Run strings."

or:

"Use GDB."

============================================================
25. TOOL ORCHESTRATION
============================================================

Use the Phase 3 trusted adapters.

Do not create a second execution architecture.

Tool selection should be based on:

- objective
- artifact type
- hypothesis
- prerequisites
- expected observation
- cost

The LLM may propose a tool.

The deterministic layer decides whether it is permitted.

============================================================
26. REALISTIC END-TO-END SOLVER
============================================================

Create a top-level solver interface.

Conceptually:

solve(challenge_package) -> SolveResult

SolveResult should distinguish:

SOLVED
BLOCKED
EXHAUSTED
FAILED
INVALID_INPUT
TIMEOUT

For SOLVED:

include:

- verified flag
- verification evidence
- solution path summary
- actions taken
- key hypotheses
- specialist contributions
- final verification method

For non-solved outcomes:

include:

- terminal reason
- remaining hypotheses
- unresolved blockers
- important evidence
- actions attempted
- why continued exploration was stopped

Do not fabricate a flag for non-SOLVED states.

============================================================
27. OBSERVABILITY
============================================================

Every important decision must be journaled.

Record:

- context updates
- hypothesis creation
- hypothesis transitions
- specialist invocation
- specialist proposal
- planner decision
- action execution
- result classification
- evidence creation
- evidence impact
- failure classification
- deduplication rejection
- dead-end closure
- candidate creation
- verification
- STOP

The journal should allow reconstruction of:

WHY DID THE AGENT DO THIS?

============================================================
28. EVALUATION — MOST IMPORTANT PART
============================================================

Do not declare Phase 5 successful merely because the solver works on synthetic examples.

Build a proper evaluation harness.

Evaluation must include:

A. Known scenarios

Challenges already represented in the existing corpus.

Purpose:
regression.

B. Novel synthetic scenarios

Challenges not used to construct the exact solver path.

Purpose:
generalization.

C. Adversarial scenarios

Intentionally include:

- misleading hints
- plausible wrong mechanism
- tool failure
- environment failure
- rate limiting
- duplicate opportunities
- misleading flag-looking strings
- contradictory evidence
- dead-end branches
- state mutation
- cross-domain challenge

D. Held-out challenges

Where feasible, use challenge instances not used to construct scenario-specific rules.

This is essential.

============================================================
29. EVALUATION METRICS
============================================================

Measure at minimum:

1. Solve rate
2. Verified solve rate
3. False-verification rate
4. False-disproof rate
5. Average actions per solve
6. Median actions per solve
7. Duplicate-action rate
8. Blind-retry rate
9. Dead-end recovery rate
10. Environmental-failure recovery rate
11. Tool-failure recovery rate
12. Specialist selection accuracy
13. Useful specialist proposal rate
14. Candidate verification success
15. Stop correctness
16. Budget violations
17. Average reasoning iterations
18. Time to verified solution
19. Resource/tool cost
20. Terminal-state correctness

Do NOT hide failed attempts.

Report them.

============================================================
30. EVALUATION MUST SEPARATE KNOWLEDGE FROM REASONING
============================================================

Record whether a solution came from:

- direct mechanism reasoning
- existing memory
- specialist knowledge
- challenge-specific artifact
- known technique
- analogy to previous challenge

This will be important for the next phase of the project.

We need to know whether the architecture can reason or merely recognize.

============================================================
31. ANTI-MEMORIZATION TEST
============================================================

If a challenge is already represented in memory:

test exact reproduction separately.

Then test structurally similar but different challenges.

The second test is more important.

Example:

Known:
JWT → algorithm confusion

Held-out:
JWT → key confusion / signing implementation flaw

The agent should not simply replay the old answer.

It should reason from mechanism and evidence.

============================================================
32. BASELINE
============================================================

Create a reproducible Phase 5 baseline.

Record:

- exact code revision/state
- test set
- challenge set
- configuration
- available tools
- memory contents
- model configuration
- budgets
- results
- failures

This baseline is critical because AFTER Phase 5 we will introduce the large external CTF writeup corpus.

We need to compare:

BASELINE AGENT

vs

AGENT + EXTERNAL WRITEUP KNOWLEDGE

without changing everything simultaneously.

============================================================
33. EXTERNAL WRITEUP CORPUS — DO NOT INGEST YET
============================================================

IMPORTANT:

DO NOT scrape or ingest:

- Jia Jie writeups
- CTFtime writeups
- CTF Pal
- external GitHub CTF repositories
- other external writeup collections

during Phase 5.

Do NOT fine-tune the model.

Do NOT add external training data.

This phase must establish the clean baseline.

The external corpus will be a separate post-Phase-5 project.

============================================================
34. REGRESSION REQUIREMENT
============================================================

Before declaring completion:

ALL existing tests must pass.

Required:

- all Phase 2 tests
- all Phase 3 tests
- all Phase 4 tests
- 12/12 historical regressions
- all existing synthetic scenarios
- all Phase 5 tests
- all Phase 5 evaluation scenarios

No regression may be hidden or ignored.

============================================================
35. TRUST BOUNDARY TESTS
============================================================

Add explicit tests proving:

1. LLM cannot directly execute tools.
2. Specialist cannot execute tools.
3. LLM cannot directly mutate evidence.
4. Specialist cannot mutate evidence.
5. LLM cannot verify a flag.
6. Specialist cannot verify a flag.
7. Untrusted candidate cannot become verified.
8. Regex cannot verify a candidate.
9. Historical memory cannot override current evidence.
10. Tool failure cannot become hypothesis disproof.
11. Environment failure cannot become hypothesis disproof.
12. Duplicate actions remain blocked.
13. Post-stop actions remain blocked.
14. Attempt budgets cannot be exceeded.
15. Invalid planner proposals are rejected.

============================================================
36. FAILURE INJECTION
============================================================

Deliberately inject:

- tool timeout
- command failure
- network failure
- HTTP 429
- HTTP 401
- HTTP 403
- malformed tool output
- unavailable tool
- corrupted artifact
- unexpected state mutation
- contradictory evidence

Verify that the solver diagnoses and recovers correctly.

Do not merely catch exceptions.

The system must understand what the failure means.

============================================================
37. AUTONOMY LOOP TEST
============================================================

At least several tests must start with:

ONLY:

challenge description
+
resources
+
permitted environment

and then allow the solver to operate without manually specified action sequences.

The test harness must NOT secretly tell the solver:

"next call tool X."

The solver must decide.

This distinction is essential.

============================================================
38. NO SCENARIO CHEATING
============================================================

Avoid scenario-specific shortcuts such as:

if challenge_name == "X":
    return flag

Avoid:

hardcoded flag mappings

Avoid:

predefined action sequences masquerading as autonomy

Avoid:

test harnesses that secretly select the correct hypothesis.

Scenario-specific oracles may verify outcomes, but they must NOT drive the solver's decision process.

============================================================
39. FINAL SYSTEM INTERFACE
============================================================

The final user-facing abstraction should be conceptually:

solve(
    challenge,
    resources,
    environment,
    constraints
)

and return:

SolveResult

The user should NOT need to understand:

- hypotheses
- specialists
- planner
- kernel
- adapters
- evidence ledger

Those are internal.

============================================================
40. PERFORMANCE
============================================================

Do not sacrifice correctness for speed.

But prevent obvious waste:

- repeated observations
- redundant specialist calls
- duplicate actions
- unnecessary full scans
- repeated failed payloads
- unnecessary verification after STOP
- excessive context growth

Use compact state summaries where possible.

Preserve evidence provenance.

============================================================
41. NO MULTI-AGENT SWARM
============================================================

Do NOT turn this into an uncontrolled swarm.

The architecture remains:

ONE STRATEGIC BRAIN
+
SPECIALIST ADVISORS
+
DETERMINISTIC CONTROL LAYER

Specialists do not become independent autonomous agents.

============================================================
42. NO RL / SELF-TRAINING YET
============================================================

Do NOT implement:

- reinforcement learning
- self-modifying policies
- automatic model fine-tuning
- recursive self-training
- uncontrolled experience replay
- model weight updates

These are future research directions.

Phase 5 is about proving the architecture.

============================================================
43. SECURITY BOUNDARY
============================================================

All execution is for authorized CTF environments, local challenge infrastructure, or explicitly supplied challenge targets.

Do not introduce unrestricted real-world exploitation infrastructure.

Maintain sandbox boundaries.

============================================================
44. DOCUMENTATION
============================================================

Create:

.agent/docs/phase5_report.md

Document:

- final architecture
- autonomous loop
- integration points
- solver interface
- specialist orchestration
- memory usage
- action planning
- evidence lifecycle
- verification lifecycle
- failure recovery
- state management
- stopping behavior
- evaluation methodology
- benchmark composition
- metrics
- results
- failures
- limitations
- known weaknesses
- deviations
- baseline configuration
- recommendations for post-Phase-5 external corpus ingestion

Be honest.

Do not claim general CTF-solving ability from a small synthetic benchmark.

============================================================
45. FINAL VALIDATION
============================================================

Run:

1. Full test suite
2. Historical regressions
3. Phase 2 tests
4. Phase 3 tests
5. Phase 4 tests
6. Phase 5 tests
7. End-to-end autonomous scenarios
8. Adversarial scenarios
9. Failure injection
10. Held-out evaluation where available
11. compileall
12. static checks
13. trust-boundary audit
14. duplicate-action audit
15. post-stop audit

Verify:

- no modifications to .agent_audit/
- no modifications to .kiro/
- no modifications to writeups/
- no modifications to historical challenge artifacts unless explicitly required for a controlled evaluation artifact
- no external writeup ingestion
- no fine-tuning
- no Phase 2 trust-boundary weakening

============================================================
46. FINAL REPORT FORMAT
============================================================

At the end of phase5_report.md include:

PHASE 5 STATUS:
COMPLETE / INCOMPLETE

TESTS:
<exact count>

HISTORICAL REGRESSIONS:
<exact result>

AUTONOMOUS SCENARIOS:
<exact result>

HELD-OUT EVALUATION:
<exact result>

SOLVE RATE:
<measurement>

VERIFIED SOLVE RATE:
<measurement>

FALSE VERIFICATION:
<measurement>

FALSE DISPROOF:
<measurement>

DUPLICATE ACTION RATE:
<measurement>

AVERAGE ACTIONS:
<measurement>

STOP CORRECTNESS:
<measurement>

KNOWN LIMITATIONS:
<list>

UNRESOLVED BUGS:
<list>

ARCHITECTURAL DEVIATIONS:
<list>

BASELINE STATE:
<description>

POST-PHASE-5 RECOMMENDATION:
External CTF Writeup Ingestion and Knowledge Expansion

Do not hide negative results.

============================================================
47. CRITICAL SUCCESS CRITERIA
============================================================

Phase 5 is NOT successful because:

- many tests pass
- many classes exist
- many specialists exist
- the code is large
- the agent generates convincing reasoning
- the agent finds plausible flags

Phase 5 is successful only if the system demonstrates:

1. Autonomous decision making
2. Evidence-driven reasoning
3. Correct failure interpretation
4. Adaptive strategy
5. Specialist orchestration
6. Action deduplication
7. Dead-end detection
8. State-aware planning
9. Controlled tool execution
10. Hard verification
11. Correct stopping
12. No fabricated flags
13. No trust-boundary bypass
14. Measurable performance on held-out/unseen scenarios

============================================================
48. STOP CONDITION FOR THIS PHASE
============================================================

When Phase 5 is complete:

STOP.

Do NOT:

- ingest external writeups
- scrape Jia Jie
- scrape CTFtime
- scrape CTF Pal
- fine-tune an LLM
- build RL
- start Phase 6
- redesign the architecture

Instead, produce the Phase 5 report and the reproducible baseline.

The NEXT project after this phase will be:

EXTERNAL CTF WRITEUP INGESTION + KNOWLEDGE EXPANSION

That project will be evaluated against the Phase 5 baseline.

============================================================
FINAL PRINCIPLE
============================================================

The objective is NOT to build an LLM that knows many CTF solutions.

The objective is to build an agent that can:

UNDERSTAND
→ HYPOTHESIZE
→ TEST
→ OBSERVE
→ INTERPRET
→ ADAPT
→ VERIFY
→ STOP

under uncertainty,

while never allowing an untrusted model output, specialist suggestion,
failed experiment, or historical memory to become trusted truth without
the deterministic control architecture validating it.

Build the smallest system that genuinely demonstrates this.

Do not overbuild.

Do not fake autonomy.

Do not fake evaluation.

Do not fabricate success.