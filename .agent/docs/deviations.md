# Deviations and Resolved Audit Inconsistencies

No architecture was redesigned. These are narrow resolutions required by Phase 2's stricter separation.

1. **Legacy trajectory `result_class` conflates observation and meaning.** Phase 2 does not import
   `SUPPORTS`/`DISPROVES` as raw result classes; they are hypothesis impacts.
2. **Failure causes mix environment, method, and process concepts.** They remain lossless root-cause
   tags. Cause aliases are normalized, but a raw result class is never blindly selected from `cause[0]`.
3. **Historical records lack proposed global fields.** Loader assigns explicit `HISTORICAL`, null
   verification date, and source-line provenance. It does not invent event timestamps or confidence.
4. **Actual inconsistency discovered:** `FAIL-012` lacks `recovery`. Contrary to Phase 1 README/schema
   assumptions, the loader preserves this as `None`; the audit source was not edited.
5. **Compound failures are not forced into fabricated tool outputs.** FAIL-006/007 test the no-observation
   process control; FAIL-009 uses an environment-failure fixture; FAIL-012 uses its canonical 429 branch.
6. **Challenge-pattern memory deferred.** Phase 1 proposes it but no dedicated JSONL exists, and Phase 2
   only requires minimal failure retrieval.
7. **No integration into the legacy nested solver.** Its boolean `success + flag` and first-success return
   path would bypass evidence/verification. Phase 3 should use a narrow adapter producing observations.
8. **Runtime failure append is deliberately local-only.** `FailureMemory.append` writes normalized
   JSONL records in append mode and refuses any path under `.agent_audit`; persistence locking and
   multi-process coordination remain Phase 3 concerns.
9. **Validation tooling:** pytest exists. Ruff/mypy are not installed and were not added; compilation and
   a deterministic AST/static audit supplement pytest. Runtime has zero third-party dependencies.

## Remaining limitations
- Classifier trusts structured executor fields; Phase 3 adapters must populate them honestly.
- HTTP status alone cannot distinguish every rejection type (e.g., application-level 200 errors).
- Retrieval is lexical and intentionally minimal; no semantic/vector retrieval yet.
- Registries are in-memory and single-process; persistence/concurrency are deferred.
- Verification trusts only evidence produced by current observations from composition-time trusted
  tool names, with candidate/method/basis binding. Phase 3 adapters remain the external trust boundary
  and must populate structured fields honestly.
- No action planner, executor, retry strategy, or specialist layer is present by design.

## Recommended Phase 3 (do not implement here)
Connect a replaceable Strategic Brain through strict adapters:
1. `ToolAdapter.execute(Action) -> ExecutionResult` with honest structured fields.
2. Context model + hypothesis set + action planner that consults Failure Memory before belief updates.
3. Persistent state/event journal under `.agent/data/` with append-only locking.
4. Challenge-pattern retrieval and category specialists, beginning with web/crypto/rev/forensics/pwn.
5. End-to-end evaluation where every proposed flag must pass this Phase 2 verifier before emission.
Do not add swarm/RL/model fine-tuning until the deterministic evaluation harness demonstrates low
false-disproof, zero false-verification, and low duplicate-action rates.

## Post-review hardening
A semantic trust-boundary review found and drove additional tests/fixes: candidate status is derived;
verification resolves current ledger evidence and composition-time trusted tool policies; action and
execution IDs/tools are bound; disproof needs a pre-registered test plus a doubly trusted source;
dedup validation occurs before registry mutation; candidate attempts require non-empty candidate-bound
evidence; candidate submissions pass anti-spray before processing; failed outputs cannot verify; and a
verified STOP prevents all later observations. Historical replay behavior moved from failure-ID branches
to a separate structured replay fixture interpreted generically.
