# failures/ — Dataset C: Failure Intelligence

`failures.jsonl` — documented dead-ends, misdiagnoses, and wasted effort from the corpus, each
converted into a reusable anti-pattern. **This is the most important dataset for preventing repeat
mistakes.** The central rule it enforces:

> **A failed experiment does NOT mean the hypothesis is false.** Classify the *cause* first.

## Failure-cause taxonomy (result_class for any action outcome)
Environmental/technical (hypothesis stays UNRESOLVED):
`RATE_LIMIT` · `AUTH` · `AUTHZ` · `TIMEOUT` · `NETWORK` · `TOOL_FAILURE` · `ENV_FAILURE`
· `STATE_MISMATCH` · `MISSING_PREREQUISITE`
Hypothesis/method (belief may update):
`WRONG_HYPOTHESIS` · `WRONG_INPUT` · `WRONG_TARGET` · `WRONG_TECHNIQUE` · `INCORRECT_ASSUMPTION`
Process/judgment (agent behavior):
`SOLVING_WRONG_PROBLEM` · `OUTPUT_INDISCIPLINE` (spray/fabricate) · `OVER_DELEGATION` · `DEFEATISM`
· `PAYLOAD_GRAVITY` · `CHEAP_TEST_LATE` · `OVERFITTING`

## Schema (per line)
```
{
  "id":"FAIL-###","challenge":"...","category":"...",
  "failed_action":"what was done","observed_result":"what came back",
  "initial_interpretation":"the WRONG read","correct_diagnosis":"what actually happened",
  "cause":["taxonomy tags"],"evidence":"why the correct diagnosis is right",
  "correct_hypothesis_update":"what belief should have changed (often: stays UNRESOLVED)",
  "recovery":"what unblocked / would have unblocked it",
  "lesson":"the reusable rule","source":"path"
}
```

## The canonical example the agent must internalize
Hypothesis "SQLi possible" → action → **HTTP 429** → correct class `RATE_LIMIT` (environmental) →
SQLi hypothesis stays **UNRESOLVED** (not disproven). The wrong move is "SQLi doesn't work". See
FAIL-005 (PHault) for the real-corpus instance of this exact error.
