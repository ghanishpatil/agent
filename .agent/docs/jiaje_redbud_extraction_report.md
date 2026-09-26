# Jia Jie Redbud Extraction Report

Generated: 2026-09-25T06:38:43.516703+00:00 · extraction: redbud-extract-1.0

Extracted the 22 frozen Redbud raw writeups into `knowledge/jiaje_redbud_v1/` by extending ctf_ingest (reused models/normalize/technique-table/store/dedup). Raw source is immutable. Not connected to the solver; benchmark not run; nothing fine-tuned. Reasoning stages are recorded EXPLICIT only when a section heading denotes them — never fabricated.

## Answer: how much genuine reusable reasoning knowledge?

- documents: 22
- distinct techniques: 25
- category distribution: {'crypto': 10, 'forensics': 2, 'misc': 1, 'pwn': 8, 'reverse': 1}
- mean trajectory completeness: 0.2438 (median 0.1818, min 0.0909, max 0.5455)
- **genuine reasoning trajectories** (description→analysis/approach→solution/verification): 8/22 (0.3636)
- failure/correction coverage: 0.0
- provenance completeness: 1.0
- duplicates: internal=1, vs local=0, vs jiaje_v1=0

### Trajectory stage presence (of 22 documents)

| stage | docs with stage |
|---|---|
| CHALLENGE_CONTEXT | 8 |
| OBSERVED_CLUE | 0 |
| CANDIDATE_MECHANISM | 0 |
| HYPOTHESIS | 10 |
| DISCRIMINATING_TEST | 0 |
| OBSERVATION | 1 |
| INTERPRETATION | 8 |
| HYPOTHESIS_UPDATE | 0 |
| NEXT_ACTION | 0 |
| EXPLOIT_SOLUTION | 22 |
| VERIFICATION | 10 |

## Per-document statistics (no averaging hides weak extraction)

| event | challenge | cat | tech | stages | complete | genuine | fails | flags |
|---|---|---|---|---|---|---|---|---|
| Redbud Puppeteer | Easy Random 1 | crypto | 1 | 5 | 0.4545 | yes | 0 | 1 |
| Redbud Puppeteer | Easy Random 2 | crypto | 2 | 5 | 0.4545 | yes | 0 | 0 |
| Redbud Puppeteer | The Old Gods Are Whispering | forensics | 2 | 6 | 0.5455 | yes | 0 | 1 |
| Redbud Puppeteer | Easy Pyjail 1 | crypto | 3 | 5 | 0.4545 | yes | 0 | 2 |
| Redbud Puppeteer | Easy Random 3 | crypto | 2 | 4 | 0.3636 | yes | 0 | 0 |
| Redbud Puppeteer | Easy RE 1 | crypto | 5 | 5 | 0.4545 | yes | 0 | 1 |
| Redbud Puppeteer | Rosetta 3 | misc | 1 | 4 | 0.3636 | yes | 0 | 1 |
| Redbud Puppeteer | RSA All in One | crypto | 3 | 3 | 0.2727 | yes | 0 | 0 |
| Redbud Puppeteer | Easy Random 4 | crypto | 3 | 2 | 0.1818 | no | 0 | 12 |
| Redbud Puppeteer | ECDSA Nonce Reuse | crypto | 3 | 2 | 0.1818 | no | 0 | 4 |
| Redbud Puppeteer | Easy Random 5 | crypto | 3 | 3 | 0.2727 | no | 0 | 0 |
| Redbud Puppeteer | RSA Partial Factorization | crypto | 3 | 3 | 0.2727 | no | 0 | 0 |
| Redbud Puppeteer | Easy Random 6 WP | forensics | 3 | 2 | 0.1818 | no | 0 | 2 |
| Redbud Summer 2026 | ret2shellcode | pwn | 1 | 1 | 0.0909 | no | 0 | 0 |
| Redbud Summer 2026 | ret2shellcode-orw | pwn | 4 | 1 | 0.0909 | no | 0 | 0 |
| Redbud Summer 2026 | baby_rop | pwn | 1 | 1 | 0.0909 | no | 0 | 0 |
| Redbud Summer 2026 | babysyscall | pwn | 2 | 1 | 0.0909 | no | 0 | 0 |
| Redbud Summer 2026 | jarvisoj_x64 | pwn | 2 | 1 | 0.0909 | no | 0 | 0 |
| Redbud Summer 2026 | stack_pivot | pwn | 3 | 1 | 0.0909 | no | 0 | 0 |
| Redbud Summer 2026 | setcontext | pwn | 4 | 1 | 0.0909 | no | 0 | 0 |
| SunshineCTF 2025 | Jupiter | reverse | 3 | 2 | 0.1818 | no | 0 | 1 |
| Redbud Summer 2026 | paragraph | pwn | 5 | 1 | 0.0909 | no | 0 | 0 |

## Interpretation

These are solution-oriented expert writeups: most contain description → analysis/approach → solution (+ often a final flag), which yields moderate trajectory completeness. They are largely NOT full hypothesize→test→observe→update narratives, and explicit failure/correction sequences are rare — so the reusable knowledge is strongest as technique + challenge-pattern + solution knowledge, and weaker as step-by-step reasoning trajectories. Values above are measured from section headings, not inferred.
