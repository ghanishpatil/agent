# Auto-Writeup + Continuous Experience Learning — Implementation Report

Status: **COMPLETE / GREEN**. Additive to `ctf_runtime` only. Frozen `ctf_agent/**` and all
external knowledge corpora are byte-for-byte unchanged.

## A. Objective

Give the runtime a memory: after every terminal challenge attempt, derive grounded learning
artifacts from the authoritative `SolveResult` — a human-readable writeup (successes) and a neutral
`ExperienceRecord` (successes and failures) — and persist them append-only for future retrieval.
The learning path must be identical for both drivers (internal `ctf_run` and Architecture-A
Kiro-driven `ctf_observe`/`ctf_propose`), must never touch the frozen solver or external corpora,
and must never be able to change a solve result, a verified flag, or verification state.

## B. What was built (all under `.agent/src/ctf_runtime/`)

| File | Responsibility |
|------|----------------|
| `experience_store.py` | `ExperienceProvenance`, `ExperienceRecord` (frozen dataclass, `to_dict`, `content_hash`), `ExperienceStore` (append-only JSONL + manifest, `O_APPEND` under a per-file lock, `for_kind()` splitting success/failure). Constants `SOURCE_SUCCESS="AGENT_SUCCESS_EXPERIENCE"`, `SOURCE_FAILURE="AGENT_FAILURE_EXPERIENCE"`, `EXPERIENCE_SCHEMA_VERSION="1.0"`. |
| `writeup.py` | `generate_writeup()` (deterministic, grounded-by-construction Markdown) + `validate_writeup()` (defensive grounding validator). |
| `experience.py` | `extract_success_experience()` / `extract_failure_experience()` — grounded field derivation from `SolveResult` + journal + observations. |
| `learning.py` | `PostTerminalObserver` — the single, failure-safe, post-terminal seam that generates + persists artifacts, wrapped top-to-bottom in `try/except`. |

Integration edits (additive, backward-compatible):
* `mcp_gateway.py`: optional `learning_root` (default `None` = **learning disabled**); `_Session.learned`/`learning`; `_fire_observer()` (fires at most once per session) invoked at the internal terminal in `ctf_run`, at the kiro success in `ctf_propose` (on kernel `is_verified()`), and at the kiro failure in `close_session`; read-only `get_writeup()` / `get_experience()` accessors.
* `kiro_bridge.py` + `kiro_driven.py`: `get_result()` + `recent_observations()` passthroughs so the observer reads the authoritative projection identically for both drivers.
* `mcp_server.py`: two read-only tools `ctf_writeup` / `ctf_experience`; demo gateway now learning-enabled (temp root).
* `real_environment.py`: `build_operator_gateway(enable_learning=True, learning_root=...)`.
* `__init__.py`: exports the new public surface.

## C. Store layout (append-only, auditable)

```
<learning_root>/                 # e.g. knowledge/agent_experience_v1  (operator-chosen; tests use tmp_path)
  success/  records.jsonl  manifest.json
  failure/  records.jsonl  manifest.json
  writeups_generated/<run_id>.md          # only for grounded SOLVED writeups
  learning_errors.jsonl                    # soft errors (never raised)
```
Each `manifest.json` carries `total_records` + `records_sha256` over the raw file, rebuilt on every
append. Success and failure never share a file, so their baselines cannot mix.

## D. Writeup rules (enforced + tested)

* Produced **only** when `result.status == SOLVED` and a verified flag exists.
* The flag is copied **verbatim** from `SolveResult.verified_flag`; it is never inferred, and the
  validator rejects any `## Flag` value that differs.
* Sections (`Description`, `Initial Analysis`, `Enumeration`, `Hypothesis`, `Exploitation`,
  `Dead Ends`, `Verification`, `Flag`) are **omitted when unsupported**.
* Dead ends are labelled honestly: rate-limit/timeout/network/tool/env/auth failures are shown as
  "not a disproof of the approach"; only an authoritative `DISPROVEN` hypothesis reads as disproven;
  unresolved reads as unresolved.
* `generate_writeup()` is deterministic (every sentence maps to a trace field) → grounded by
  construction; `validate_writeup()` is the independent guard (and the gate for any future
  model-phrasing pass), catching ungrounded tools/targets, wrong flags, and unobserved snippets.

## E. Experience-extraction rules (the critical safety property)

Failure classification is read straight from the runtime (`ResultClass` on actions/evidence and
hypothesis status). Therefore:

* **Environmental / rate-limit / timeout / network / tool / auth failures are recorded as
  `failure_classes` + `dead_end_actions`, never as technique disproof.**
* **Only a hypothesis whose authoritative status is `DISPROVEN` appears in `disproven`.**
* **Unresolved hypotheses stay unresolved** (and `remaining_hypotheses` are merged into
  `unresolved`). `terminal_reason` and `unresolved_blockers` are preserved verbatim.
* Failure records never carry a flag.

## F. Failure-safety

`PostTerminalObserver.observe()` and the gateway `_fire_observer()` are both wrapped in top-level
`try/except`. Any learning error is written softly to `learning_errors.jsonl` and swallowed; it can
never raise into a tool response, and `session.learned` is set **before** work begins so an error
can never cause a re-fire loop. Learning is post-terminal and read-only over a `SolveResult`
projection — it never drives, mutates, or re-verifies the pipeline. With `learning_root=None`
(the default, and what the entire pre-existing suite uses) nothing is written at all.

## G. Verification

| Check | Result |
|-------|--------|
| Full suite (`python -m pytest`) | **459 passed, 0 failed** (417 baseline + 42 new) |
| New tests (writeup 1-11, success 12-19, failure 20-26, persistence 27-33, failure-safety 34-38, Architecture A 39-42) | 42/42 pass |
| Frozen fingerprints (`ooc/fpcheck.py`) | **45 matched (raw bytes), 0 mismatched, 0 missing** |
| Internal MCP smoke (`scripts/mcp_stdio_smoke.py`) | PASS — SOLVED `CTF{mcp_demo_ssti_verified}`; 14 tools incl. `ctf_writeup`/`ctf_experience` |
| Kiro-driven MCP smoke (`scripts/mcp_kiro_smoke.py`) | PASS — observe/propose → VERIFIED_FLAG |
| External corpora | Untouched — no `agent_experience_v1` under the real knowledge tree; all learning roots are `tmp_path`/system-temp only |

## H. Scope discipline

* No changes to `ctf_agent/**` (frozen) or to `ingestion`/external corpora.
* `knowledge_translation.py` was **not** implemented (out of scope for this task). Experience
  records are future retrieval *input*; a separate, later translation step would be required to make
  them advisory to solving. They are non-authoritative over any runtime evidence today.
* No model fine-tuning, no API keys, no network. The writeup generator is deterministic; no model
  runs inside the runtime on any path.

## I. Public surface added

`ExperienceStore`, `ExperienceRecord`, `ExperienceProvenance`, `SOURCE_SUCCESS`, `SOURCE_FAILURE`,
`EXPERIENCE_SCHEMA_VERSION`, `extract_success_experience`, `extract_failure_experience`,
`WriteupResult`, `generate_writeup`, `validate_writeup`, `PostTerminalObserver`;
gateway `get_writeup`/`get_experience`; MCP tools `ctf_writeup`/`ctf_experience`;
`build_operator_gateway(enable_learning=…, learning_root=…)`.
