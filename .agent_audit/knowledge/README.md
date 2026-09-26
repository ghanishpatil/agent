# knowledge/ — Dataset A: Technique Memory

`technique_memory.jsonl` — one JSON object per line, each a reusable technique distilled from the
historical corpus. Designed to be ingested as **priors, not commands** (see `../memory_schema/`).

## Schema (per line)
```
{
  "id": "T-###",
  "technique": "short name",
  "category": "web|crypto|rev|pwn|forensics|stego|misc|ai|multi",
  "confidence": "VERIFIED|SUPPORTED|PLAUSIBLE|HISTORICAL|CHALLENGE_SPECIFIC|LOW_CONFIDENCE",
  "indicators": ["what you observe that suggests this technique"],
  "prerequisites": ["what must be true/available to attempt it"],
  "cheap_tests": ["low-cost high-information probes to run first"],
  "discriminating_tests": ["tests that confirm/deny vs neighbours"],
  "expected_observations": ["what a positive result looks like"],
  "interpretation_rules": ["how to read ambiguous results; failure != disproof"],
  "common_mistakes": ["traps seen in this corpus"],
  "failure_modes": ["how it fails + what that failure usually means"],
  "recovery": ["what to do when blocked"],
  "verification": ["how a real success is confirmed (minimum sufficient evidence)"],
  "examples": ["Challenge (event) -> outcome [source path]"]
}
```

## Confidence semantics
- **VERIFIED** — technique produced a server-accepted / self-validating flag in this corpus.
- **SUPPORTED** — documented working solve, single instance, not independently re-derived here.
- **PLAUSIBLE** — reversed/understood but not confirmed against a live target.
- **HISTORICAL** — recorded in a meta-log only; low traceability.
- **CHALLENGE_SPECIFIC** — worked once but generalizes poorly; keep as a pattern, not a rule.
- **LOW_CONFIDENCE** — guessed or ambiguous in the source.

## Usage rule for the agent
Retrieve by matching `indicators` to current evidence. Run `cheap_tests` before `discriminating_tests`.
Treat `interpretation_rules` as the guard against "experiment failed → hypothesis false". Never emit a
flag without satisfying `verification`.
