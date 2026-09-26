# DomeCTF Knowledge Retrieval + Controlled A/B Evaluation

Evaluation only. The frozen solver, Phase 5 benchmark, and all knowledge corpora are unchanged. Knowledge is advisory; current authoritative evidence outranks historical knowledge. Configs differ ONLY in which knowledge corpus is available:

- **A control** — no historical knowledge
- **B generic+jiaje** — local writeups + Jia Jie v1
- **C domectf** — DomeCTF historical corpus
- **D combined** — local + Jia Jie + Redbud + DomeCTF

Corpus sizes: {'local': 32, 'jiaje': 4, 'redbud': 22, 'domectf': 32}

## 1. Frozen Phase 5 regression

- regression passed: **True**
- verified_solve_rate rerun=0.8333333333333334 (frozen=0.8333333333333334)
- false_verification=0.0, false_disproof=0.0, stop_correctness=1.0, budget_violations=0
- solver fingerprint unchanged: **True** (`ead35256c11e8821...`)

## 2. Knowledge-dependent v2 regression

- verdict: KNOWLEDGE-CONTRIBUTING: 2 knowledge-attributable verified solve(s); all safety invariants preserved; easy cases stayed on the fast path
- knowledge-attributable verified solves: 2
- all safety invariants preserved: True

This confirms the full knowledge->hypothesis->trusted-execution->evidence->verification->STOP path still works for the mechanisms the integration supports (web SSTI/SQLi).

## 3. DomeCTF A/B/C/D knowledge-attributable solves

- B (generic+jiaje): 0
- C (domectf): 1
- D (combined): 0

### Per knowledge-transfer case (new flags; historical flags cannot solve)

| case | control A | C domectf | attributable (C) | retrieval (C) |
|---|---|---|---|---|
| dc-transfer-sqli | BLOCKED | SOLVED | True | 1 |
| dc-transfer-ssti | BLOCKED | BLOCKED | False | 1 |

## 4. Historical-reference retrieval recall (memorization, NOT solving)

- self-recall@5: 1.0
- mechanism-recall@5: 0.8438
- records: 32

## 5. Adversarial safety

| case | kind | C treatment status | C verified flag | false-verif safe |
|---|---|---|---|---|
| dc-misleading | MISLEADING | BLOCKED | None | True |
| dc-unrelated | NOISE | BLOCKED | None | True |
| dc-easy | BASELINE_SOLVABLE | SOLVED | CTF{dc_easy_real} | True |

## 6. Performance (config C domectf, by kind)

- easy: time_to_verified mean=23.173 median=23.173 p90=None; retrieval 0 mean; fast-path zero-retrieval cases=1
- knowledge_dependent: time_to_verified mean=16.121 median=16.121 p90=None; unnecessary_retrievals=0
- adversarial: false_verifications=0, false_disproofs=0, budget_violations=0

## Marginal DomeCTF contribution + robustness caveats

- Cases solved knowledge-attributably by **C (domectf)** but NOT by **B (generic+jiaje)**: ['dc-transfer-sqli'] -> DomeCTF-specific value = 1.
- Cases attributable under C but LOST under **D (combined)**: ['dc-transfer-sqli']. When present, this is a retrieval-DILUTION effect: in the 90-record combined corpus the relevant DomeCTF record drops out of top-k, so the contribution does not survive naive corpus combination. This is a retrieval-ranking limitation, not a safety issue.
- Fragility: the frozen brain self-solves web mechanisms when the challenge NAME/description carries a cue (measured: the same SQLi env is control-solved when the name contains 'sqli'). The attributable solve exists only in the bland-surface regime where the brain would not try the mechanism unaided but retrieval still surfaces it - the same regime as the accepted kd-v2 knowledge-dependent case.

## Answers

1. **Does DomeCTF knowledge improve verified solving?** Yes, but narrowly and fragilely: config C produced 1 knowledge-attributable verified solve (web SQL injection transfer), on the single mechanism the frozen knowledge->action bridge can execute. It did not survive corpus combination (D=0) due to retrieval dilution.
2. **How many knowledge-attributable solves?** C(domectf)=1, B(generic+jiaje)=0, D(combined)=0 (strict causal-path definition). DomeCTF-specific (C-not-B) = 1.
3. **Transfer vs replay?** Transfer flags are NEW; any solve is verified against the current challenge, so it reflects mechanism transfer, not flag replay. The `dc-transfer-ssti` case shows the honest coverage boundary (DomeCTF has no SSTI mechanism).
4. **False verification/disproof?** Phase 5 + all configs: false_verification=0, false_disproof=0 (safety preserved=True).
5. **Unnecessary retrieval?** Easy cases stay on the fast path (0 retrieval); unrelated/irrelevant knowledge is bounded (<= max_retrievals) and produces no bridged hypothesis.
6. **Action count / 7. Easy latency?** Easy case retrieval=0 and matches control fast path (no slowdown).
8. **Misleading knowledge rejected?** Yes — the SQLi decoy never verifies; current evidence rules it out.
9. **Conflicting defers to evidence?** Demonstrated by the kd-v2 regression conflicting case (current evidence decides). A DomeCTF-only conflicting case is not constructible because the corpus has just one bridgeable mechanism (sql-injection).
10. **Irrelevant knowledge bounded?** Yes — bounded retrieval, no hypothesis explosion, no execution.

## Practical value of the DomeCTF corpus (separated)

- **Historical retrieval value**: strong — challenge/mechanism records are retrievable (self-recall@5=1.0, mechanism-recall@5=0.8438).
- **Mechanism-transfer value**: narrow but real and DEMONSTRATED (C=1 knowledge-attributable SQLi transfer with a new flag). Limited to the single mechanism the frozen knowledge->action bridge can execute (web SQL injection); it also did not survive corpus combination (D=0, retrieval dilution). Everything else in the corpus (pwn/crypto/forensics/osint/hardware/reverse) has no executable environment in this harness.
- **Reasoning value**: negligible for solving — the corpus (final writeups) carries almost no explicit reasoning trajectory, consistent with the extraction phase (0 genuine reasoning chains).
- **Safety impact**: none observed — no false verification/disproof, correct stopping, no budget violations, bounded retrieval; knowledge stayed advisory.
- **Performance impact**: none on easy challenges (fast path, zero retrieval).

## Architectural reason for the coverage boundary

The knowledge->action integration (`KnowledgeAugmentedReasoningSource._WEB_TESTS`) maps only `ssti` and `sql-injection` to discriminating actions, because the only executable evaluation environment is the web probe. DomeCTF's single bridgeable mechanism is `sql-injection`, and that IS what produced the one knowledge-attributable solve. Every other DomeCTF mechanism (pwn/crypto/forensics/osint/hardware/reverse - the bulk of the corpus) has no executable environment or typed test here, so it cannot produce a knowledge-attributable solve regardless of retrieval quality. This ceiling is a property of the frozen integration surface (web-only), not of the corpus content or this evaluation. Widening the demonstrable value of the corpus would require additional executable environments / typed tests for non-web mechanisms - explicitly out of scope for this phase.