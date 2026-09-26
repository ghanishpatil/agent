# Proposed Memory Architecture (schemas + semantics)

Five memory stores. **Governing rule: memory provides PRIORS, not COMMANDS.** Current evidence always
overrides stale memory. Every record carries `confidence`, `last_verified`, and `source` so the agent
can weight it and detect staleness.

## Global fields on every record
```
{ "id":"...", "confidence":"VERIFIED|SUPPORTED|PLAUSIBLE|HISTORICAL|CHALLENGE_SPECIFIC|LOW_CONFIDENCE",
  "source":"path or event", "last_verified":"iso-date-or-null",
  "generalizes":"bool/short", "provenance":"how derived" }
```

## Memory-as-priors semantics (retrieval contract)
1. Retrieve by matching current evidence to `indicators`/`patterns` (not by keyword alone).
2. Rank by `confidence × recency × specificity-match`.
3. A retrieved item proposes a **hypothesis + a cheap test**, never a forced action.
4. If current evidence contradicts memory, **trust evidence**; lower that record's confidence.
5. `CHALLENGE_SPECIFIC` and `LOW_CONFIDENCE` items may seed ideas but must never become hard rules.
6. Never emit a flag because memory says so — only `verification` gates emission.

---
## 1. Technique Memory  (→ knowledge/technique_memory.jsonl)
Reusable attack knowledge keyed by observable indicators.
```
{ ...global,
  "technique","category","indicators":[],"prerequisites":[],
  "cheap_tests":[],"discriminating_tests":[],"expected_observations":[],
  "interpretation_rules":[],"common_mistakes":[],"failure_modes":[],
  "recovery":[],"verification":[],"examples":[] }
```
Query: `indicators ⊇ current_evidence` → returns ranked techniques + their cheap tests.

## 2. Experience Memory  (→ trajectories/trajectories.jsonl)
Full solved reasoning paths for analogy/retrieval.
```
{ ...global,
  "challenge","category","context","grading_model",
  "steps":[{hypothesis,action,observation,result_class,interpretation,update}],
  "key_insight","solution","verification","wasted_actions":[],
  "generalizes","challenge_specific" }
```
Query: by category + context similarity → returns nearest solved trajectory as a template (not a script).

## 3. Failure Memory  (→ failures/failures.jsonl)  ★ highest anti-repeat value
```
{ ...global,
  "challenge","category","failed_action","observed_result",
  "initial_interpretation","correct_diagnosis",
  "cause":[<taxonomy>],"evidence","correct_hypothesis_update",
  "recovery","lesson" }
```
Cause taxonomy (env/tech | hypothesis/method | process): `RATE_LIMIT, AUTH, AUTHZ, TIMEOUT, NETWORK,
TOOL_FAILURE, ENV_FAILURE, STATE_MISMATCH, MISSING_PREREQUISITE | WRONG_HYPOTHESIS, WRONG_INPUT,
WRONG_TARGET, WRONG_TECHNIQUE, INCORRECT_ASSUMPTION | SOLVING_WRONG_PROBLEM, OUTPUT_INDISCIPLINE,
OVER_DELEGATION, DEFEATISM, PAYLOAD_GRAVITY, CHEAP_TEST_LATE, OVERFITTING`.
Query: **before updating any belief after a failed action**, and before declaring a dead end — check
whether the observed_result matches a known environmental/process cause. Enforces "failure ≠ disproof".

## 4. Tool Memory  (→ tools/tool_memory.jsonl)
```
{ ...global,
  "tool","category","availability":"native|native-limited|native-installable|container-only|uninstalled|low-value",
  "purpose","inputs","useful_options":[],"expected_outputs",
  "common_errors":[],"failure_interpretation","when_to_use","when_not_to_use","prerequisites":[] }
```
Query: capability needed → returns available tool + how to read its errors; blocks reliance on
unavailable tools (Docker removed).

## 5. Challenge-Pattern Memory  (new; seed from knowledge/CHALLENGE_CATALOG.md)
Higher-level "smell" of a challenge → likely class, so the agent recognizes families fast.
```
{ ...global,
  "pattern_name","tells":[<brief keywords/artifacts/headers>],
  "likely_category","candidate_techniques":[<T-###>],
  "typical_decoys":[],"typical_verification","events_seen":[],"notes" }
```
Examples to seed:
- tells=["no upload/DNS/mail/print","telemetry pcap","perfect payload clock"] → forensics/timing → [T-021]; decoys=["val series","missing-sample runlengths"].
- tells=["RS256 JWT","published jwks"] → web/auth → [T-006]; decoys=["alg:none only"].
- tells=["/report admin bot","format param","eval(`type_${x}`)"] → web/XSS → [T-012].
- tells=["ceremony/ashes","secret file","bellman/vk.bin"] → crypto/zk → [T-020].
- tells=["struct + loop counter + win flag","SNAPSHOT int3"] → pwn → [T-024].
- tells=["srand(time)","big payout leaps threshold","lose ends cleanly"] → pwn → [T-025].
- tells=["flavor hint about char-by-char","constant 0x00 responses"] → web/custom-encoding → [T-015].

---
## Storage & lifecycle notes
- Format: JSONL for machine ingestion; small enough to keep in a vector index keyed on `indicators/tells`.
- **Writes:** append-only after every challenge (win: technique+trajectory; loss: failure). Mirrors the
  operator's existing "learning loop" but into structured stores instead of prose logs.
- **Decay:** `last_verified` drives staleness; environment-dependent items (tools) re-checked at session start.
- **Conflict:** if two records disagree, keep both, prefer higher confidence + more recent + evidence-backed.
