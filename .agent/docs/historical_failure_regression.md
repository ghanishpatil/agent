# Historical Failure Regression

**Result: 12/12 PASS.**

Each row maps Phase 1 history to a separately curated structured replay and expectation.

| Case | Historical situation | Old incorrect interpretation | New classification | Hypothesis impact | Recovery / control | Result |
|------|----------------------|------------------------------|--------------------|-------------------|--------------------|--------|
| FAIL-001 | binary accepts many distinct 32-byte strings; burned real submission attempts | 'check is underdetermined -> challenge is flawed/unsolvable' | SUCCESS | NO_IMPACT | re-derive every handler for a per-step oracle; question input format; get grading model; never submit a collision (`SUPPORTED:CONTINUE`) | PASS |
| FAIL-002 | answer wrong; no offline validator; many byte-orderings equally plausible | the impressive binary + 12 R9CF records ARE the flag source; my concatenation is the flag | SUCCESS | NO_IMPACT | check solve count first; read sibling writeup; inventory small files; detrend timing; ask for accept/reject EARLY (`SUPPORTED:CONTINUE`) | PASS |
| FAIL-003 | ~20 wasted turns; repeated rejections; flip-flopped 'metadata' vs 'decoy' | each rejection means the location (metadata) is wrong | INPUT_REJECTION | BLOCKS_TEST | diff packaged-vs-extracted FIRST; then present ALL format variants in ONE message; ask for the submit oracle (`DUPLICATE`) | PASS |
| FAIL-004 | fabricated flag with no byte/validator traceability | the sub-agent's conclusion is an answer | SUCCESS | NO_IMPACT | own the core insight; never relay a sub-agent flag without reproducing its self-validating step; label mechanism 'verified' and flag 'UNVERIFIED' up front (`SUPPORTED:CONTINUE`) | PASS |
| FAIL-005 | no timing delta observed on given instances | SQLi doesn't work / the database is broken | TARGET_RESPONSE | UNRESOLVES | build a calibrated boolean-timing extractor at minute 1; force SLEEP on every scanned row / UNION SELECT SLEEP(n>2) (`UNRESOLVES`) | PASS |
| FAIL-006 | no exploit built; event ended unsolved | there is no usable XSS here | AMBIGUOUS | NO_IMPACT | build the exploit page + report same-origin URL; exfil to webhook; commit to building the recognized technique immediately (`NO_IMPACT`) | PASS |
| FAIL-007 | no solve; time/context burned; core solve offloaded to the user | no escape primitive exists -> challenge impossible under exposed namespace | AMBIGUOUS | NO_IMPACT | timebox; try the hint-driven path on the live target fast; treat provided objects as the gadget; never declare a hinted challenge impossible (`NO_IMPACT`) | PASS |
| FAIL-008 | Z3 timeouts | need a bigger/longer solve | TIMEOUT | UNRESOLVES | recognize slow-tool signature in <1 try and pivot to exploiting invertibility (`UNRESOLVES`) | PASS |
| FAIL-009 | quote/semicolon mangling, garbled/wrapped output, stale output misread, cwd didn't persist | tool results (sometimes) looked like real failures | ENVIRONMENT_FAILURE | UNRESOLVES | write .py files and run them; redirect output to a file and READ the file; use ABSOLUTE paths; fresh terminals; ';' not '&&'; $env:VAR (`UNRESOLVES`) | PASS |
| FAIL-010 | model matched outputs but did not pin the intended flag | matching random outputs proves I understand the check | SUCCESS | NO_IMPACT | trace every store->load and compare->consumer; find the per-step oracle (`SUPPORTED:CONTINUE`) | PASS |
| FAIL-011 | effort misdirected toward constructing any-passing-input | the goal is to make the checker say GRANTED | AMBIGUOUS | BLOCKS_TEST | at minute 0 determine: string-match vs server-run; offline validator?; attempts left (`BLOCKS_TEST`) | PASS |
| FAIL-012 | non-2xx, no useful body, or dropped connection | the vulnerability does not exist / the payload failed | RATE_LIMIT | UNRESOLVES | UNRESOLVES (`UNRESOLVES`) | PASS |

## Interpretation
- Environmental/tool/auth/network/timeout outcomes never become automatic disproof.
- Compound historical cases are replayed at their relevant control layer rather than forced into fabricated raw output.
- Collision, readability, behavioral matching, and model suggestions remain unverified.
- Missing historical fields remain null; no evidence or recovery data is invented.
