# Next-Generation CTF Agent — Architecture Recommendation

Grounded in the evidence in this workspace (30 writeups, ~10 detailed failure post-mortems, the
jiegec reference, and the tooling assessment). The 28 constitution principles are **not 28 modules** —
they collapse into **7 strategic-brain components + 5 execution/support layers**, with the principles
realized as behaviors *inside* those components.

```
                 ┌────────────────────────── STRATEGIC BRAIN ──────────────────────────┐
   evidence ──▶  │ 1 Context Model → 2 Hypothesis Engine ⇄ 3 Evidence Manager           │
                 │        ▲                     │                    │                   │
                 │        │                     ▼                    ▼                   │
                 │ 7 Memory/Retrieval ─▶ 4 Action Planner ─▶ 5 Decision Controller       │
                 │                                                   │                   │
                 │                                    6 Verification/Stopping Controller │
                 └───────────────────────────────────┬──────────────────────────────────┘
                                                      ▼
   ┌───────────── EXECUTION & SUPPORT LAYERS ──────────────────────────────────────────┐
   │ A Deterministic Executor · B Result Classifier · C Environment/State Manager       │
   │ D Specialist Layer (per-category experts) · E Evaluation Harness                   │
   └────────────────────────────────────────────────────────────────────────────────────┘
```

## 1. Context Model  — *Deep Context Understanding (1), Mechanism-First (6)*
- Parses the brief/hints AS A TECHNICAL SPEC (Rule Zero). Extracts: flag format, category, points,
  solve count, every noun/number/name/date → candidate mechanism/parameter.
- Maintains the **grading model** (string-match | server-run | offline-validator | unknown) — set at
  minute 0 (principle 6/verification). Feeds Challenge-Pattern retrieval ("tells").
- Output: a structured Context object other components consume; re-read trigger when stuck.

## 2. Hypothesis Engine  — *Hypothesis Management (11), Adaptive Strategy (7)*
- Holds a **ranked set of hypotheses**, each with state `{OPEN, SUPPORTED, DISPROVEN, UNRESOLVED}` and
  a confidence. Never collapses to a single track prematurely (Controlled Exploration 17).
- Seeds hypotheses from Technique + Challenge-Pattern memory (priors) and from Context tells.
- **Critical rule:** only `WRONG_HYPOTHESIS/INCORRECT_ASSUMPTION`-classed results move a hypothesis
  toward DISPROVEN; environmental/process results leave it UNRESOLVED (see Result Classifier).

## 3. Evidence Manager  — *Evidence-Driven (2), Evidence Freshness (26), Clean State (20)*
- Single source of truth for observations: each tagged `{source, timestamp, confidence, supersedes}`.
- Enforces **freshness** (stale observations decay; environment facts re-verified per session) and
  **evidence > memory** (memory is a prior; a contradicting observation wins and lowers that prior).
- Deduplicates observations so the planner never re-derives known facts (Action Deduplication 22).

## 4. Action Planner  — *Cheapest Discriminating Test First (5), Max Info/Action (4), Cost-Aware (28), Minimal Sufficient Evidence (25)*
- Proposes candidate actions from the active hypotheses; scores each with a **simple heuristic**, not
  heavy math: `value ≈ information_gain / (cost + risk)` gated by `prerequisites_met` and
  `not_redundant`. Prefer the one test that most splits the hypothesis space.
- Emits `preconditions` and a `recovery` plan per action (principle 27).

## 5. Decision Controller  — *Speed w/o Recklessness (21), Action Deduplication (22), State-Aware Planning (23), Dead-End Detection (24)*
- Chooses the next action(s); may run **parallel independent probes** (Parallel Investigation 10).
- **Dedup gate:** blocks an action already run unless {env changed, hypothesis changed, input changed,
  target changed, objective changed, prior run invalid, new evidence justifies repeat}.
- **Dead-end handling:** marks a branch `low-value/closed` (preserved, not "never revisit") when it is
  repeatedly disproven / low-information / an identified decoy; reopens if new evidence raises its value.
- Consults Failure Memory *before* acting on any "it failed → abandon" impulse.

## 6. Verification / Stopping Controller  — *Hard Verification (12), No Fabrication (13), Minimal Sufficient Evidence (25)*
- A flag is emitted ONLY when it meets a `verification` gate: server-accept, self-validating decode
  (magic+length+checksum), deterministic inversion, or challenge output. Distinguishes **candidate** vs
  **verified** flag explicitly.
- Stops at **minimum sufficient evidence** (no redundant proofs). Never emits a constructed collision
  or a sub-agent's unproven conclusion. If blocked with no validator → emit ONE clearly-labeled
  CANDIDATE + ALL format variants in one message, then request an oracle (anti-spray).

## 7. Memory / Retrieval Layer  — *Persistent Knowledge (16)*
- The five JSONL stores (`memory_schema/schemas.md`): Technique, Experience, Failure, Tool,
  Challenge-Pattern. **Priors, not commands.** Retrieval keyed on indicators/tells; ranked by
  `confidence × recency × specificity`. Append-only learning loop after every challenge.

---
## Execution & Support layers
### A. Deterministic Executor  — *Autonomous Tool Orchestration (9)*
Wraps tools with fixed I/O contracts, timeouts, and retry/backoff. Writes multi-line output to files
(PowerShell reliability). Idempotent where possible. Never free-forms a tool the Env Manager says is absent.

### B. Result Classifier  — *Rejection-Aware / Fault-Diagnostic (14), Failure Intelligence (15)* ★
The linchpin. Maps every raw result to a `result_class` using the Failure cause taxonomy:
`SUPPORTS | DISPROVES | INCONCLUSIVE | ENV_CONSTRAINT(RATE_LIMIT/AUTH/AUTHZ/TIMEOUT/NETWORK/TOOL/ENV/STATE/PREREQ)`.
Enforces the canonical rule: **429/timeout/auth ≠ hypothesis false** (hypothesis stays UNRESOLVED).
Feeds the Hypothesis Engine and appends to Failure Memory on genuine dead ends.

### C. Environment / State Manager  — *Resource & Environment Awareness (19), Preconditions (27)*
Session-start capability probe (native libs, Docker/WSL presence, tool availability). Tracks target
state (sessions, cookies, instance freshness, rate-limit budgets). Supplies `availability` to the planner
so it never depends on missing tools (Docker-removed reality).

### D. Specialist Layer  — *Specialist Expertise (8)*
Per-category expert profiles (web/crypto/rev/pwn/forensics/stego/misc-jails/ai), each = the relevant
slice of Technique + Category playbook + Specialist tool set. The Decision Controller routes to the
specialist matching the Context category; specialists can run in parallel for multi-category challenges.

### E. Evaluation Harness  — *(supports 12/15/16; enables safe iteration)*
Offline replay of the Experience + Failure datasets as regression tests: does the agent (a) pick the
cheap discriminating test, (b) classify a 429 as ENV not disproof, (c) refuse to emit a collision,
(d) reuse a known technique instead of re-deriving? Measures solve-rate, actions-to-solve,
wasted-action rate, and repeat-mistake rate.

---
## Principle → component coverage map (all 28)
- Context Model: 1, 6 · Hypothesis Engine: 7, 11, 17 · Evidence Manager: 2, 20, 26 ·
- Action Planner: 4, 5, 25, 28 · Decision Controller: 10, 21, 22, 23, 24 ·
- Verification/Stopping: 12, 13, 25 · Memory: 16 ·
- Executor: 9 · Result Classifier: 14, 15 · Env/State Manager: 19, 27 · Specialist: 8 ·
- Autonomous Ambiguity Resolution (18): shared Context+Planner (infer most-useful action, else ask ONE
  targeted question) · Evaluation Harness validates the whole.

---
## Build order (evidence-based)
1. **Result Classifier + Failure Memory** first — the corpus shows the biggest losses were *misclassified
   failures* and *fabricated/collision flags*, not missing techniques. This single component prevents the
   most historical damage.
2. **Verification/Stopping Controller** — enforce candidate-vs-verified + anti-spray.
3. **Memory/Retrieval (5 JSONL) + Environment Manager** — priors + real capability awareness.
4. **Context Model + Hypothesis Engine + Action Planner/Decision Controller** — the reasoning loop.
5. **Specialist Layer** — start with WEB/CRYPTO/REV/FORENSICS/PWN (where evidence is strong).
6. **Evaluation Harness** — regression on the datasets before trusting autonomy.

## Do NOT build yet
- Full autonomous end-to-end solver, RL/"self-training", multi-agent swarms, or heavy MCP wiring.
  Evidence is insufficient (thin categories, no labeled step-level dataset) and the historical failures
  were judgment/verification problems that automation would amplify, not fix.
