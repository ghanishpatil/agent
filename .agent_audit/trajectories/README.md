# trajectories/ — Dataset B: Expert Solving Trajectories

`trajectories.jsonl` — one JSON object per solved (or fully-reversed) challenge, capturing the
**reasoning path**, not just "tool → flag". This is the highest-value data for teaching an agent
*how to think*: how hypotheses were formed, which action was chosen and why, how each observation
updated belief, and how the solution was verified.

## Schema (per line)
```
{
  "id": "TRAJ-###",
  "challenge": "name (event)",
  "category": "...",
  "confidence": "VERIFIED|SUPPORTED|PLAUSIBLE",
  "flag_status": "confirmed|per-instance|reversed-not-fired|unverified",
  "context": "the brief/keywords as a technical spec",
  "grading_model": "string-match | server-run | offline-validator | unknown",
  "steps": [
     {"hypothesis":"...","action":"...","observation":"...",
      "result_class":"SUPPORTS|DISPROVES|INCONCLUSIVE|ENV_CONSTRAINT",
      "interpretation":"...","update":"kept|dropped|refined|new"}
  ],
  "key_insight": "the crux that unlocked it",
  "solution": "the exploit/decode in one paragraph",
  "verification": "minimum sufficient evidence used",
  "wasted_actions": ["actions that added no information (for dedup training)"],
  "generalizes": "what transfers to other challenges",
  "challenge_specific": "what does not transfer",
  "source": "path"
}
```

## Curation note
These are reconstructed from the writeups and are as faithful as the sources allow. Where a source
recorded a lucky guess, an undocumented jump, or an unverified flag, it is flagged in
`result_class`/`flag_status` rather than presented as clean reasoning. Trust `VERIFIED` > `SUPPORTED`
> `PLAUSIBLE`.
