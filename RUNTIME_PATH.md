# RUNTIME_PATH — CTF Solving Runtime Audit (read-only)

Scope: determine whether the observed behavior

> "Targeted guesses missed. Let me pull a real wordlist and run a proper crack — this is the
> standard Flask-cookie escalation pattern for a medium challenge."

was produced *through* the `.agent` architecture (and its anti-guessing/evidence/state controls) or
*outside* it. No files were modified. Evidence is cited by file/function/class.

---

## 0. Verdict (up front)

**AGENT_BYPASSED.**

The observed behavior did not pass through the `.agent` architecture at any point. It was generated
and executed by the IDE-level LLM assistant (Kiro) using its own tool-execution surface
(`execute_pwsh` shell and/or the repo-root MCP tools), which is entirely outside `.agent/` and is
not wired to `ctf_agent.autonomy.solve()`, the `TrustKernel`, the planner, the adapters, or the
reasoning-source validation.

**Exact bypass point:** there is no runtime bridge from the IDE agent to the `.agent` solver. The
first step of the mandated pipeline — *LLM output → typed `*Suggestion` → `proposals.validate_*`* —
never happens for live behavior, because nothing outside `.agent/tests`, `.agent/scripts`,
`ctf_agent.autonomy.evaluation.EvaluationHarness`, and the `ctf_experiment` harnesses ever calls
`solve()` / `solve_with_knowledge()`. The live actor executes tools directly.

---

## 1. What the code shows (facts verified this audit)

### 1a. No LLM is invoked by the agent at all
- `.agent/src/ctf_agent/llm_boundary.py` defines the `ReasoningSource` Protocol and a
  `ScriptedReasoningSource` explicitly documented as *"A deterministic test double standing in for a
  real LLM"* and *"Real integration (Phase 4+) **would** implement `ReasoningSource` against an
  actual model"*. No actual model client is implemented.
- Repo-wide search of `.agent/src/**/*.py` for `import openai` / `anthropic` / `requests.post` →
  **no matches**. The agent contains no LLM/network-model call site.
- The live reasoning "brain" in both composition roots is the **deterministic**
  `SpecialistReasoningSource(SpecialistRegistry.default(), …)`:
  - `ctf_agent/autonomy/solver.py` → `solve()` (line ~199)
  - `ctf_experiment/knowledge_solver.py` → `solve_with_knowledge()` (line ~120)
- `ctf_agent/specialists/brain.py` `SpecialistReasoningSource` returns structured
  `HypothesisSuggestion` / `ActionSuggestion` dataclasses. It *"never executes a tool, never touches
  kernel/evidence state, and never verifies a flag."* It does not emit natural-language chat.

### 1b. Which ReasoningSource is active (by entrypoint)
- Frozen path `solve()`: `RoutedReasoningSource(SpecialistReasoningSource(...))`
  (`ctf_agent/autonomy/reasoning.py`).
- Experiment path `solve_with_knowledge()`:
  `RoutedReasoningSource(KnowledgeAugmentedReasoningSource(SpecialistReasoningSource(...)))`
  (`ctf_experiment/knowledge_reasoning.py`).
- **Neither is reachable at live runtime** (see §3). For the observed behavior, *no* `ReasoningSource`
  was active — including `KnowledgeAugmentedReasoningSource`.

### 1c. The only tool-execution path inside the agent is the trusted adapter
- `ctf_agent/loop.py` `ReasoningLoop._execute_one()` executes exclusively via
  `self.adapters.execute(action)` (`AdapterRegistry`).
- `ctf_agent/adapters/subprocess_adapter.py` `SubprocessAdapter` is a strict allowlist: the
  executable is **fixed at construction** (`SubprocessCommand.executable`, resolved via
  `shutil.which`), and `Action.input_data` supplies **arguments only, never the executable path**.
  An action "can never redirect execution to an arbitrary binary."
- The only other `subprocess.run` sites in `ctf_agent` are `autonomy/baseline.py` (git state capture)
  — not on the action path. No `os.system` / `Popen` / `shell=True` anywhere in `ctf_agent`.

---

## 2. The mandated pipeline as implemented (canonical path through `.agent`)

This is what *would* happen if a real challenge were routed through `solve()` /
`solve_with_knowledge()`. Traced from `ctf_agent/loop.py` `ReasoningLoop.run()`:

| # | Stage | Code (file · function/class) |
|---|---|---|
| 1 | Challenge input → understanding/metadata | `autonomy/solver.py` `solve()` → `understand_challenge`, `to_metadata` |
| 2 | Kernel + controller + brain composed | `solve()` builds `TrustKernel`, `AutonomyController`, `SpecialistReasoningSource`, wrapped by `RoutedReasoningSource` (and `KnowledgeAugmentedReasoningSource` in the experiment root) |
| 3 | Loop start | `loop.py` `ReasoningLoop.run(state, max_actions)` |
| 4 | Reasoning source proposes hypotheses | `_seed_hypotheses()` → `reasoning_source.suggest_hypotheses()` → `validate_hypothesis_suggestion()` → `board.propose_hypothesis()` (OPEN only) |
| 5 | Reasoning source proposes actions | `_select_next()` → `reasoning_source.suggest_actions()` (typed `ActionSuggestion`s) |
| 6 | Planner validates + ranks + dedups | `_select_next()` → `ActionPlanner.propose_with_diagnostics(…, completed_fingerprints=…)` |
| 7 | Action fingerprint / dedup | `_execute_one()` uses `deduplication.fingerprint_action` + `fingerprint_state`; duplicates rejected (planner `completed_fingerprints`); `ControlDecision.DUPLICATE` recorded |
| 8 | Trusted adapter executes | `_execute_one()` → `self.adapters.execute(action)` → `AdapterRegistry` → `SubprocessAdapter`/`HttpAdapter`/`FileAdapter` |
| 9 | Result classification | `kernel.process()` → `classifier.py` (`ExecutionResult` → `ResultClassification`) |
| 10 | Evidence manager receives observation | `kernel.process()` → `evidence.py` (classification-bound evidence + provenance) |
| 11 | Hypothesis impact updates hypothesis | `kernel.process()` → `impact.py` → `board.record(result)` (`hypothesis.py` immutable transition) |
| 12 | Verification / stop | `kernel.process()` → `verification.py`; `ControlDecision.STOP` on verified; loop returns `LoopOutcome.VERIFIED` |

Candidate-flag safety (relevant to "guessing"): in `_execute_one()`, a candidate flag is only
attached if `existing_evidence_ids` already bind that exact value to the hypothesis
(`_evidence_is_bound_to`), and `RoutedReasoningSource._eligible_candidate` additionally requires the
source hypothesis to be `FactState.SUPPORTED` with matching bound evidence. Naming a candidate
"can never itself verify it." This is the zero-blind-guessing control — **but it only governs code
that runs inside this loop.**

---

## 3. The actual observed path (why it did not use the agent)

### 3a. Nothing live invokes the agent
- Callers of `solve()`: `ctf_agent/autonomy/evaluation.py` (`EvaluationHarness.run` over
  `ctf_bench` benchmark cases) and `ctf_experiment/knowledge_dependent_harness.py`.
- Callers of `solve_with_knowledge()`: `ctf_experiment/knowledge_dependent_harness_v2.py`.
- These are **tests / benchmarks / experiment harnesses** with synthetic environments and synthetic
  permitted tools (e.g. `decode_tool`, `http_probe`, `flag_verifier`, `ClassicalTool`,
  `LocalVerifier` in `ctf_bench/phase5_benchmark.py`).
- Repo-wide search **outside** `.agent/` for `ctf_agent` / `autonomy.solve` / `solve_with_knowledge`
  / `ReasoningLoop` → **no matches**. No live/interactive runner, MCP server, or root script imports
  or invokes the agent.
- **No persisted `journal.jsonl`** exists anywhere under `.agent/` outside ephemeral test temp dirs
  (searched). There is no runtime record of any real challenge ever flowing through the agent.

### 3b. The observed text is not agent output
- It is free-form natural-language narration ("Let me pull a real wordlist…", "this is the standard
  Flask-cookie escalation pattern"). The deterministic `SpecialistReasoningSource` emits typed
  `*Suggestion` dataclasses, not chat prose.
- "Targeted guesses missed" describes **blind guessing that already occurred** — which the kernel's
  candidate-binding rules (`verification.py`, `RoutedReasoningSource._eligible_candidate`,
  `loop._evidence_is_bound_to`) forbid inside the loop.
- The named tools ("wordlist", "crack", "Flask cookie") do not exist as permitted tools in any
  `.agent` `EnvironmentConfig`. An `Action` for them could not be constructed, planned, or executed
  by the agent.

### 3c. The direct execution surface the live actor used (outside the adapter)
Execution paths available to the IDE agent (Kiro) that bypass the trusted adapter entirely:
- Kiro's own `execute_pwsh` shell tool (arbitrary commands; no allowlist, no `SubprocessCommand`).
- Repo-root MCP / automation tooling, present but **not** part of `.agent`:
  - `hexstrike-ai/hexstrike-ai-mcp.json` — an MCP server ("HexStrike AI v6.0 … Advanced
    Cybersecurity Automation Platform. Turn off alwaysAllow if you dont want autonomous execution!",
    `python3 hexstrike_mcp.py --server http://IPADDRESS:8888`).
  - `ctf_solver_mcp/` — a second MCP server package (`CTFSolver`, `app`).
  - `hexstrike-ai/ctf_toolkit.py`, `ctf-env/` — direct tool wrappers.
- `.agent_audit/legacy_conflicts.md` already flags these as **not** constitution-governed and
  assuming their availability as a violation of the agent's principles.

None of these route through `AdapterRegistry` / `SubprocessAdapter` / `TrustKernel`.

---

## 4. Point-by-point proof (the 14 requested items)

1. **Which code invokes the LLM.** None inside `ctf_agent`. `llm_boundary.py` only *defines* the
   `ReasoningSource` interface + a scripted test double; no model client exists (no
   `openai`/`anthropic`/HTTP-model call). The live "brain" is the deterministic
   `SpecialistRegistry.default()`. The observed prose was produced by the IDE LLM (Kiro) itself.
2. **Which ReasoningSource is active.** For live behavior: **none** (the agent was not invoked).
   Architecturally, `solve()` uses `RoutedReasoningSource(SpecialistReasoningSource)`;
   `solve_with_knowledge()` adds `KnowledgeAugmentedReasoningSource`.
3. **Whether `KnowledgeAugmentedReasoningSource` or another source is active.** Not active — it only
   exists on the `solve_with_knowledge()` experiment path, which no live runtime calls.
4. **Whether LLM output becomes a typed hypothesis/action proposal.** No. No `HypothesisSuggestion`/
   `ActionSuggestion` was created; `proposals.validate_*` was never reached.
5. **Whether the proposal passes through the planner.** No. `ActionPlanner.propose_with_diagnostics`
   was never called for this behavior.
6. **Whether action fingerprinting/deduplication runs.** No. `deduplication.fingerprint_action` /
   `fingerprint_state` / `completed_fingerprints` never ran (they run only inside
   `ReasoningLoop._execute_one`).
7. **Whether the action passes through the trusted adapter.** No. `AdapterRegistry.execute` /
   `SubprocessAdapter` was not on the path; execution used Kiro's shell / MCP tools.
8. **Whether the observation passes through the Result Classifier.** No. `classifier.py` was not
   invoked (reached only via `kernel.process`).
9. **Whether Evidence Manager receives the observation.** No. `evidence.py` recorded nothing for
   this behavior.
10. **Whether Hypothesis Impact Engine updates the hypothesis.** No. `impact.py` / `board.record`
    were not called.
11. **What hypothesis state existed immediately before the wordlist/cracking action.** None —
    there was no `HypothesisBoard`, no `Hypothesis`, no `FactState` for this behavior (no agent run;
    no `journal.jsonl`). The state does not exist in the agent.
12. **What evidence justified that action.** None in the agent's `EvidenceManager`. The justification
    was the LLM's own narration ("standard Flask-cookie escalation pattern"), which is a heuristic
    prior, not classification-bound evidence with provenance.
13. **Whether the action was generated by the CTF Agent or directly by Kiro.** **Directly by Kiro**
    (the IDE LLM assistant), not by `ctf_agent`.
14. **Whether any direct shell/browser/tool execution path exists outside the trusted adapter.**
    **Yes.** Kiro's `execute_pwsh`, plus the repo-root `hexstrike-ai` MCP server, `ctf_solver_mcp`,
    `hexstrike-ai/ctf_toolkit.py`, and `ctf-env/` — all execute tools without passing through
    `AdapterRegistry`/`SubprocessAdapter`/`TrustKernel`.

---

## 5. Final verdict

**AGENT_BYPASSED.**

- **Bypass point:** the very first pipeline step. The live LLM (Kiro) produced an intent and executed
  it through its own tool surface (`execute_pwsh` / MCP servers) with **no call to
  `ctf_agent.autonomy.solve()` / `solve_with_knowledge()`**. Consequently the LLM output never became
  a typed `*Suggestion`, never crossed `proposals.validate_*`, the `ActionPlanner`,
  `deduplication.fingerprint_action`, `AdapterRegistry`/`SubprocessAdapter`, `classifier.py`,
  `evidence.py`, `impact.py`, or `verification.py`.
- **Root structural cause:** the `.agent` solver is *not integrated* into the live runtime. It is
  reachable only from `.agent/tests`, `.agent/scripts`, `EvaluationHarness`, and `ctf_experiment`
  harnesses (confirmed: no external importer of `ctf_agent`; no persisted runtime journal). Its
  anti-guessing / evidence / state / verification controls are real and enforced **inside** the loop,
  but they cannot govern actions that never enter the loop.

This is `AGENT_BYPASSED`, not `AGENT_INVOKED_BUT_NOT_GOVERNING`: no control "failed"; the governed
pipeline was simply never on the execution path.

---

## 6. Audit method / caveats

- Read-only. No implementation file was modified. This file (`RUNTIME_PATH.md`) is the only artifact
  created, at the repository root, as requested.
- Evidence is from static code reading (`ctf_agent/llm_boundary.py`, `specialists/brain.py`,
  `autonomy/reasoning.py`, `autonomy/solver.py`, `loop.py`, `adapters/subprocess_adapter.py`,
  `ctf_experiment/knowledge_solver.py`, `knowledge_reasoning.py`, `knowledge_dependent_harness{,_v2}.py`,
  `autonomy/evaluation.py`, `ctf_bench/phase5_benchmark.py`) and repo-wide searches for LLM clients,
  external invokers of the agent, and persisted runtime journals.
- Caveat: I could not trace an actual challenge *through the agent* because no such execution exists
  (no `journal.jsonl` outside test temp dirs; no external caller of `solve()`). That absence is
  itself the core evidence: the runtime that produced the observed behavior is Kiro's own tool loop,
  not the `.agent` architecture. The exact shell/MCP command behind the quoted line is not persisted
  in a `.agent` artifact and therefore cannot be reconstructed from the agent; it originated on the
  IDE agent's execution surface.
