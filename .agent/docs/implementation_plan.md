# Phase 2 Implementation Plan

## Baseline
Implement the trust/control kernel from `.agent_audit/architecture_recommendation.md` and
`.agent_audit/memory_schema/schemas.md`. Historical JSONL is read-only input. The legacy nested
solver is not reused because its `success: bool + flag` model bypasses evidence and verification.

## Scope
1. Define minimal frozen dataclasses/enums for execution results, state, hypotheses, observations,
   evidence, failures, flag candidates, verification, and action identity.
2. Implement pure deterministic classification and hypothesis-impact functions.
3. Implement provenance-enforcing evidence creation and current-evidence-over-memory conflict rules.
4. Load/normalize/retrieve `.agent_audit/failures/failures.jsonl` without mutating it.
5. Implement challenge-relevant flag verification, STOP-on-verified, anti-spray, and action dedup.
6. Compose the mandatory Action→Observation→Classification→Evidence→Impact→State chain in a thin kernel.
7. Test the 15 required scenarios, 8 invariants, and all 12 historical failure records.

## Explicit deviations from Phase 1
- Phase 1 trajectory `result_class` values (`SUPPORTS`, `DISPROVES`) are legacy hypothesis impacts,
  not Phase 2 raw result classes.
- Historical failure records lack several proposed global fields; the loader preserves originals and
  assigns transparent `HISTORICAL`/null defaults rather than inventing facts.
- Compound failure records are tested at the appropriate control layer or split into structured cases;
  they are not forced into a fabricated raw execution result.
- Challenge-pattern memory and all Phase 3 autonomy are deferred.

## Verification
- RED: tests must fail because `ctf_agent` does not yet exist.
- GREEN: all tests pass.
- Static: `python -m compileall src tests`; JSONL source parses; no writes outside `.agent/`.
