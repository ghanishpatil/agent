PHASE 4 — SPECIALIST INTELLIGENCE LAYER

Workspace:
F:\mission-git-hackss\mission-git-hackss

MODEL:
Use Opus 5 for this phase.

============================================================
PHASE STATUS
============================================================

Phase 1 — Corpus & Knowledge Audit: COMPLETE
Phase 2 — Trust & Control Foundation: COMPLETE
Phase 3 — Strategic Brain + Trusted Execution: COMPLETE

Do NOT redesign Phase 1, Phase 2, or Phase 3.

Phase 2 and Phase 3 are the current architectural source of truth.

Phase 3 validation baseline:

- 169/169 tests passed
- 74 Phase 2 tests
- 95 Phase 3 tests
- 12/12 historical regressions passed
- compileall clean
- .agent_audit/ unchanged
- .kiro/ unchanged
- writeups/ unchanged
- 3 synthetic end-to-end scenarios pass through the real ReasoningLoop
- Phase 2 Trust Kernel remains the authority

============================================================
1. READ THE EXISTING SYSTEM FIRST
============================================================

Before changing anything, inspect:

.agent/docs/
.agent/src/ctf_agent/
.agent/tests/
.agent/runtime/

Read the Phase 3 report if present:

.agent/docs/phase3_report.md

Also inspect the Phase 1 corpus intelligence:

.agent_audit/

Especially:

- architecture_recommendation.md
- schemas.md
- trajectories.jsonl
- failures.jsonl
- technique_memory.jsonl
- tool_memory.jsonl
- legacy_conflicts.md

Inspect the existing Phase 3:

- Context Model
- Hypothesis Engine
- Action Planner
- Trusted Tool Adapters
- ReasoningLoop
- Memory Retrieval
- Runtime Journal
- LLM boundary
- Trust Kernel integration

Do not assume the previous architecture is exactly as expected.
Verify the actual implementation before extending it.

============================================================
2. PHASE 4 OBJECTIVE
============================================================

Build the Specialist Intelligence Layer.

The purpose is to give the Strategic Brain deep CTF-domain expertise without allowing specialists to bypass the deterministic architecture.

Target architecture:

                    STRATEGIC BRAIN
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
          WEB          CRYPTO         PWN
       SPECIALIST     SPECIALIST    SPECIALIST
             │            │            │
             ├────────────┼────────────┤
             │            │            │
             ▼            ▼            ▼
           REVERSE     FORENSICS     STEGO
         SPECIALIST    SPECIALIST   SPECIALIST
             │            │            │
             └────────────┼────────────┘
                          │
                  Specialist Output
                          │
                          ▼
                  STRATEGIC BRAIN
                          │
                          ▼
                    ACTION PLANNER
                          │
                          ▼
                  TRUSTED ADAPTER
                          │
                          ▼
                   PHASE 2 KERNEL
                          │
                          ▼
              EVIDENCE / STATE / STOP

SPECIALISTS ARE ADVISORS.

THE STRATEGIC BRAIN REMAINS THE AUTHORITY.

============================================================
3. INITIAL SPECIALIST SET
============================================================

Build these five specialists first:

1. WEB
2. CRYPTO
3. REVERSE ENGINEERING
4. FORENSICS
5. PWN

Do NOT build every possible category yet.

Do NOT build cloud/mobile/IoT/OSINT/etc. unless the existing corpus clearly requires a narrowly scoped shared capability.

The objective is quality and architecture validation, not maximum category count.

Future specialists can be added after Phase 4 evaluation.

============================================================
4. SPECIALIST CONTRACT
============================================================

Every specialist must expose a common interface.

For example:

Specialist.analyze(ContextSnapshot) -> SpecialistAnalysis

The exact implementation is up to you, but the contract must be strongly typed.

SpecialistAnalysis should contain structured information such as:

- specialist
- observations
- candidate mechanisms
- hypotheses
- supporting evidence references
- conflicting evidence references
- recommended discriminating tests
- candidate actions
- required tools
- prerequisites
- expected observations
- estimated action cost
- confidence/priority
- reasoning summary
- uncertainty
- applicable techniques
- relevant memory references

Do NOT return only free-form text.

Free-form reasoning may exist as an explanatory field, but all actionable information must have typed structure.

============================================================
5. SPECIALISTS MUST NOT CONTROL THE SYSTEM
============================================================

Specialists MAY:

- analyze challenge context
- identify possible mechanisms
- propose hypotheses
- propose discriminating experiments
- suggest tools
- suggest candidate actions
- interpret existing evidence
- identify contradictions
- identify prerequisites
- recommend a direction
- retrieve relevant historical knowledge

Specialists MUST NOT:

- execute tools directly
- directly mutate TrustKernel state
- directly mutate evidence
- directly mark a hypothesis VERIFIED
- directly mark a hypothesis DISPROVEN
- verify a flag
- bypass ActionPlanner
- bypass ActionDeduplication
- bypass anti-spray controls
- bypass prerequisites
- bypass verification
- declare the challenge solved
- override current evidence
- override the Strategic Brain
- treat memory as current truth

The flow must always remain:

SPECIALIST
→ PROPOSAL
→ STRATEGIC BRAIN
→ ACTION PLANNER
→ TRUSTED ADAPTER
→ PHASE 2 KERNEL

Never:

SPECIALIST
→ EXECUTE

Never:

SPECIALIST
→ VERIFIED FLAG

============================================================
6. EVIDENCE-AWARE SPECIALISTS
============================================================

This is one of the most important requirements.

Specialists must reason from evidence rather than merely pattern-match challenge descriptions.

Bad behavior:

"This looks like SQL injection. Try SQL injection payloads."

Good behavior:

"The observed parameter behavior is consistent with SQL injection, but this is currently only PLAUSIBLE. The cheapest discriminating test is to determine whether a controlled syntax perturbation changes the response. A timeout, 429, or tool failure must not be interpreted as disproof."

Every specialist recommendation should distinguish:

KNOWN
SUPPORTED
PLAUSIBLE
UNRESOLVED
BLOCKED
DISPROVEN

Do not allow specialist confidence to substitute for evidence.

============================================================
7. MECHANISM-FIRST REASONING
============================================================

Specialists should reason from mechanisms.

They should ask:

- What mechanism could produce this behavior?
- What observation would distinguish competing mechanisms?
- What prerequisite must exist?
- What is the cheapest test?
- What result would support the hypothesis?
- What result would actually disprove it?
- What failures would merely block the test?
- What evidence is still missing?

Avoid:

- payload spraying
- random tool selection
- generic wordlists without justification
- brute force without a mechanism
- repeating equivalent tests
- guessing flags
- assuming a common vulnerability merely because of category

============================================================
8. SPECIALIST-SPECIFIC REQUIREMENTS
============================================================

------------------------------------------------------------
WEB SPECIALIST
------------------------------------------------------------

Reason about mechanisms including, where supported by evidence:

- SQL injection
- NoSQL injection
- command injection
- SSTI
- XSS
- SSRF
- LFI/RFI
- path traversal
- authentication flaws
- authorization flaws
- IDOR
- JWT issues
- session handling
- CSRF
- request smuggling
- deserialization
- mass assignment
- prototype pollution
- file upload
- business logic flaws
- API vulnerabilities

Do NOT hardcode a vulnerability list as the only knowledge source.

The specialist must infer mechanisms from:

- requests
- responses
- headers
- parameters
- source code
- JavaScript
- routes
- cookies
- tokens
- application behavior
- challenge hints
- historical patterns

It should prioritize cheap discriminating tests.

------------------------------------------------------------
CRYPTO SPECIALIST
------------------------------------------------------------

Reason about:

- classical ciphers
- XOR
- substitution/transposition
- encoding vs encryption
- RSA
- ECC
- Diffie-Hellman
- discrete logarithm structures
- weak randomness
- nonce reuse
- IV reuse
- padding
- MAC/signature flaws
- hash constructions
- length extension where applicable
- key recovery
- known plaintext
- chosen plaintext/ciphertext structures
- algebraic weaknesses
- implementation mistakes
- protocol misuse

Use mechanism-first mathematical reasoning.

Do not randomly brute-force cryptographic parameters without evidence.

Prefer:

structure
→ identify weakness
→ derive attack
→ test
→ verify.

------------------------------------------------------------
REVERSE ENGINEERING SPECIALIST
------------------------------------------------------------

Reason about:

- executable structure
- strings
- imports
- control flow
- functions
- constants
- transformations
- encoding/decoding
- anti-analysis behavior
- comparisons
- input validation
- key derivation
- custom algorithms
- VM/bytecode behavior
- packed/obfuscated code
- dynamic behavior

Use the cheapest useful static analysis before expensive dynamic analysis where appropriate.

Identify what observation would distinguish:

- encoding
- encryption
- hashing
- transformation
- validation
- hidden comparison
- generated value

Do not automatically execute suspicious artifacts outside the controlled environment.

------------------------------------------------------------
FORENSICS SPECIALIST
------------------------------------------------------------

Reason about:

- file metadata
- filesystem artifacts
- archives
- deleted data
- timestamps
- logs
- memory artifacts
- network captures
- documents
- embedded files
- EXIF
- steganography indicators
- strings
- entropy
- file signatures
- carving
- browser artifacts
- process artifacts

Prefer:

identify artifact
→ determine likely hiding mechanism
→ extract
→ validate.

Do not run every available forensic tool blindly.

------------------------------------------------------------
PWN SPECIALIST
------------------------------------------------------------

Reason about:

- memory corruption
- stack layout
- heap behavior
- format strings
- integer issues
- buffer overflows
- use-after-free
- double free
- control-flow hijacking
- mitigations
- ROP
- ret2libc
- GOT/PLT
- canaries
- PIE
- NX
- ASLR
- RELRO
- libc behavior
- input constraints

First understand:

binary
→ protections
→ vulnerability
→ primitive
→ controllability
→ exploitability
→ verification.

Do not blindly generate payloads.

============================================================
9. USE THE EXISTING CTF CORPUS
============================================================

This is NOT a generic specialist implementation.

The Phase 1 corpus is a major source of domain expertise.

Use:

.agent_audit/
writeups/
historical trajectories
failure records
technique memory
tool memory
challenge patterns

Extract reusable patterns from successful historical reasoning.

Examples of useful knowledge types:

- mechanism → indicator
- indicator → discriminating test
- test → expected observations
- observation → interpretation
- failure → correct diagnosis
- technique → prerequisite
- technique → appropriate tool
- tool → expected result
- challenge pattern → likely mechanism

Do NOT simply copy challenge-specific flags or blindly reproduce old solutions.

The goal is GENERALIZABLE EXPERTISE.

For example:

BAD:

"Challenge X uses payload Y."

GOOD:

"Applications that construct SQL queries using unsanitized parameter interpolation may exhibit controlled response changes under syntax perturbation."

Historical knowledge should generate priors, not truth.

============================================================
10. FAILURE INTELLIGENCE
============================================================

Specialists must use historical failures correctly.

Examples:

If history shows:

SQL injection test → HTTP 429

the specialist should learn:

RATE LIMIT / TEST BLOCKED

not:

SQL injection disproven.

If history shows:

tool crashed

the specialist should distinguish:

TOOL FAILURE

from:

TARGET MECHANISM FAILURE.

If history shows:

candidate collision

the specialist should learn:

WEAK VERIFICATION

not:

candidate is correct.

Failure Memory is advisory.

Current evidence always wins.

============================================================
11. SPECIALIST SELECTION
============================================================

Do NOT invoke every specialist for every challenge.

The Strategic Brain should decide which specialists are relevant.

Example:

Web challenge:

Web Specialist
+
possibly Crypto if JWT/crypto mechanism appears

not:

Web + Crypto + Pwn + Reverse + Forensics + Stego simultaneously.

Specialist selection should consider:

- challenge category
- description
- hints
- available artifacts
- observed behavior
- current hypotheses
- previous evidence
- specialist relevance

Allow multiple specialists when the challenge genuinely crosses domains.

============================================================
12. CROSS-DOMAIN CHALLENGES
============================================================

Support specialist collaboration through the Strategic Brain.

Example:

WEB
→ identifies JWT

CRYPTO
→ analyzes token signing

WEB
→ interprets application behavior

The specialists do NOT directly communicate state with each other.

The Strategic Brain mediates:

Specialist A
→ proposal
→ Strategic Brain
→ Specialist B context
→ proposal
→ Strategic Brain

This prevents uncontrolled specialist-to-specialist state mutation.

============================================================
13. CONFLICT RESOLUTION
============================================================

Specialists may disagree.

Example:

Web Specialist:
"SSRF is plausible."

Crypto Specialist:
"JWT algorithm confusion is more directly supported."

Do NOT automatically choose the highest-confidence specialist.

The Strategic Brain should compare:

- evidence
- hypothesis state
- expected information gain
- test cost
- prerequisites
- contradictions
- historical relevance

Then select the next discriminating action.

Current evidence outranks specialist confidence.

============================================================
14. SPECIALIST MEMORY
============================================================

Do not create a completely separate memory database for every specialist.

Prefer shared memory with specialist/category metadata.

For example:

TechniqueMemory:
- technique
- category
- indicators
- prerequisites
- discriminating tests
- expected observations
- failure patterns
- source
- provenance

Specialists retrieve relevant knowledge.

Memory remains advisory.

============================================================
15. NO SPECIALIST TOOL EXECUTION
============================================================

This is critical.

A specialist may say:

"Run strings against the binary."

It does NOT run strings.

It returns:

CandidateAction(
    tool="strings",
    target="...",
    objective="identify embedded strings",
    expected_observation="human-readable strings",
    prerequisites=[...]
)

Then:

Strategic Brain
→ Action Planner
→ Trusted Adapter
→ ExecutionResult
→ Phase 2 Kernel

This preserves the architecture.

============================================================
16. TESTING
============================================================

Preserve ALL Phase 2 and Phase 3 tests.

Add specialist tests covering:

### Specialist contract

- valid structured output
- malformed proposal rejection
- missing required fields
- invalid action proposal
- unsupported tool proposal
- invalid hypothesis transition
- fabricated evidence rejection

### Specialist relevance

- relevant specialist selected
- irrelevant specialist not unnecessarily invoked
- multi-domain challenge selects multiple relevant specialists

### Evidence reasoning

- current evidence affects specialist analysis
- historical memory does not override current evidence
- tool failure does not become disproof
- environment failure does not become disproof
- ambiguous observation remains unresolved

### Planner integration

- specialist action proposal enters ActionPlanner
- duplicate action blocked
- missing prerequisite blocked
- action cost considered
- discriminating test preferred

### Verification

- specialist cannot verify flag
- specialist cannot directly create trusted evidence
- candidate still passes Phase 2 verification
- verified candidate causes STOP

### Conflict handling

- two specialists may disagree
- Strategic Brain resolves through evidence/planning
- specialist confidence alone cannot override evidence

============================================================
17. SPECIALIST EVALUATION SCENARIOS
============================================================

Create deterministic local/synthetic tests for at least:

1. WEB
2. CRYPTO
3. REVERSE
4. FORENSICS
5. PWN

Each scenario should test actual specialist reasoning, not just whether a class can be instantiated.

Each should include:

- challenge context
- relevant artifacts
- initial ambiguity
- at least one plausible wrong path
- useful evidence
- specialist proposal
- discriminating action
- updated hypothesis
- final candidate
- Phase 2 verification

At least some scenarios must deliberately produce:

- tool failure
- environment failure
- ambiguous evidence
- conflicting hypotheses
- duplicate action attempt

to ensure specialists behave correctly under failure.

============================================================
18. SPECIALIST QUALITY METRICS
============================================================

Measure:

- specialist relevance accuracy
- useful hypothesis rate
- useful action proposal rate
- duplicate proposal rate
- unsupported-action rate
- false-disproof rate
- false-verification rate
- unnecessary specialist invocation
- actions-to-solution
- evidence quality
- discriminating-test selection
- recovery from failed experiments

Do NOT optimize for:

- number of hypotheses
- number of tools
- amount of generated text
- number of specialist calls

Optimize for:

CORRECTNESS
+
INFORMATION GAIN
+
EVIDENCE QUALITY
+
LOW DUPLICATION
+
LOW FALSE DISPROOF
+
ZERO FALSE VERIFICATION

============================================================
19. SECURITY / EXECUTION BOUNDARY
============================================================

All actual execution remains controlled by Phase 3 Trusted Tool Adapters.

Specialists cannot execute arbitrary commands.

Do not introduce unrestricted real-world exploitation.

Synthetic/local CTF environments only for evaluation.

============================================================
20. DO NOT OVERBUILD
============================================================

Do NOT:

- redesign Phase 2
- redesign Phase 3
- replace the Trust Kernel
- create independent autonomous specialist agents
- create specialist-specific execution engines
- create unrestricted MCP/plugin systems
- create a swarm
- add RL
- add fine-tuning
- build vector databases without demonstrated need
- build cloud infrastructure
- build UI
- implement every CTF category
- blindly ingest all historical code

Keep specialists modular and replaceable.

============================================================
21. FILE STRUCTURE
============================================================

Prefer something similar to:

.agent/
    src/
        ctf_agent/
            specialists/
                __init__.py
                base.py
                web.py
                crypto.py
                reverse.py
                forensics.py
                pwn.py
                registry.py
                selection.py
            ...
    tests/
        specialists/
            ...
    runtime/
    docs/

Adapt this to the actual Phase 3 architecture rather than forcing an incompatible structure.

Do NOT modify:

.agent_audit/
.kiro/
existing writeups/
historical challenge artifacts

============================================================
22. BACKWARD COMPATIBILITY
============================================================

ALL existing Phase 2 and Phase 3 behavior must remain valid.

Run:

- all existing tests
- all historical regressions
- all Phase 3 synthetic scenarios

after specialist integration.

Do not accept "specialists work" if existing reasoning behavior regresses.

============================================================
23. FINAL VALIDATION
============================================================

Before declaring Phase 4 complete:

1. Run all tests.
2. Run all 12 historical regressions.
3. Run all Phase 3 tests.
4. Run all Phase 3 synthetic scenarios.
5. Run all specialist tests.
6. Run specialist end-to-end scenarios.
7. Run compileall.
8. Run static audit.
9. Verify Phase 2 Trust Kernel is unchanged.
10. Verify Phase 3 core behavior remains valid.
11. Verify specialists cannot bypass the kernel.
12. Verify specialists cannot directly verify candidates.
13. Verify specialists cannot directly mutate evidence.
14. Verify specialists cannot execute tools directly.
15. Verify historical files remain unchanged.

============================================================
24. PHASE 4 REPORT
============================================================

Create:

.agent/docs/phase4_report.md

Include:

- specialists implemented
- specialist contract
- specialist selection
- specialist-to-brain interface
- knowledge sources
- memory integration
- evidence handling
- failure handling
- cross-domain handling
- conflict resolution
- planner integration
- security boundaries
- tests
- synthetic scenarios
- evaluation metrics
- results
- limitations
- known gaps
- deviations from this specification
- exact recommendation for Phase 5

Be completely honest.

Do not claim a specialist is effective merely because its tests pass.

============================================================
25. FINAL STOP
============================================================

Phase 4 ends after:

- specialist implementation
- integration
- testing
- regression validation
- evaluation
- documentation

DO NOT start Phase 5.

DO NOT build the final full autonomous solver yet.

STOP after Phase 4.