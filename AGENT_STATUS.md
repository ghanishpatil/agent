# AGENT_STATUS

Current dated status of the CTF Autonomous Solver project. Figures are verified from repository
artifacts; where a value could not be verified it is marked accordingly.

- **Current date:** 2026-09-24 (session environment date).
- **Python / platform:** 3.10.7 · Windows.
- **Run location for tests:** `.agent/` (`python -m pytest`; `pyproject.toml` sets `pythonpath=["src"]`).

---
Knowledge-attributable solve accounting:
The 2 KAVS reported by the knowledge-dependent v2 experiment are
synthetic injected-knowledge path-validation cases. They are not
attributable to the real ingested corpora.

The DomeCTF evaluation produced 1 knowledge-attributable solve using
real ingested corpus knowledge (SQL injection transfer).

Therefore, the current demonstrated real-corpus-attributable solve
count is 1, while the synthetic knowledge-integration validation
count is 2.

## 1. Completed work

- **Phases 1–5 complete.** Failure/knowledge audit (Phase 1), Trust Kernel (Phase 2), Strategic Brain
  + Trusted Execution (Phase 3), Specialist Intelligence Layer (Phase 4), Full Autonomous Solver +
  Evaluation Baseline (Phase 5). Phase 5 is **frozen**.
- **Additive external-knowledge track (outside frozen solver):**
  - Ingestion of Jia Jie (`jiaje_v1`), Jia Jie Redbud (`jiaje_redbud_v1`), and DomeCTF (`domectf_v1`)
    corpora; DomeCTF source discovery/verification (`domectf_sources_v1`).
  - Retrieval layer + advisory projection; knowledge-augmented A/B harnesses (v1, v2).
  - DomeCTF knowledge retrieval + controlled A/B evaluation (`domectf_eval_v1`).

## 2. Phase 5 frozen fingerprint

- Frozen package: `.agent/src/ctf_agent/` (45 Python files).
- Aggregate SHA-256 (over sorted relpath + file digest):
  **`ead35256c11e882157688410a9618de1e45c3f80a57f4bfb4be7728ebdffdb88`**
- Recorded in `.agent/docs/phase5_freeze.md`. Test count at freeze: 264 passed. Historical
  regressions at freeze: 12/12.
- Verified unchanged in the most recent session (recomputed aggregate matched).

## 3. Phase 5 benchmark results (frozen, `.agent/docs/phase5_results.json`)

- Case count: 6 (small deterministic synthetic suite — not evidence of general CTF-solving ability).
- Verified solve rate: **0.833**
- Solve rate: 0.833
- False verification: **0**
- False disproof: **0**
- Stopping correctness: **1.0**
- Budget violations: **0**
- Terminal-state correctness: 1.0

## 4. Current test count

- **383 passed** (full suite, most recent run). Note: the freeze manifest records 264 at Phase 5
  freeze; the additional tests come from the additive ingestion/experiment tracks (all under
  `.agent/tests/`, none modifying frozen `ctf_agent`).

## 5. Knowledge corpus status

| Corpus | Records | Status |
|---|---|---|
| `knowledge/local_writeups/` | 32 | frozen (do not modify) |
| `knowledge/jiaje_v1/` | 4 | frozen |
| `knowledge/jiaje_redbud_v1/store/` | 22 | frozen |
| `knowledge/domectf_v1/store/` | 32 | frozen (DomeCTF 2019/2020/2021 individual writeups) |
| `knowledge/domectf_sources_v1/` | 40 refs / 49 raw | frozen (source inventory, not KnowledgeRecords) |
| `knowledge/domectf_eval_v1/` | — | evaluation outputs (this track) |

Known data-quality note (frozen, recorded not fixed): in `domectf_v1`, the technique_ids `rop` and
`hardware-tpm` appear on ~20 Beagle Security records due to "Related Articles" sidebar chrome in the
source pages; this is an extraction-phase artifact, The DomeCTF extraction contains rop and hardware-tpm technique_ids
across approximately 20 records. Their presence is recorded in the
extracted records/statistics; the extraction report does not establish
their precise source or causal origin..

## 6. Retrieval evaluation results (prior, `.agent/docs/`)

- **Retrieval quality** (`retrieval_quality.json`): labeled synthetic k=5 — mean precision@5 ≈ 0.486,
  mean recall@5 = 1.0, MRR = 1.0; real-store category consistency ≈ 0.72.
- **Knowledge-dependent v1** (`knowledge_dependent_results.json`): **KNOWLEDGE-SAFE / NON-CONTRIBUTING**,
  0 knowledge-attributable verified solves; all safety invariants preserved (advisory memory is
  observability-only in the frozen architecture).
- **Knowledge-dependent v2** (`knowledge_dependent_results_v2.json`): **KNOWLEDGE-CONTRIBUTING**,
  2 knowledge-attributable verified solves; all safety invariants preserved; easy cases stayed on
  the fast path.

## 7. DomeCTF evaluation results (`knowledge/domectf_eval_v1/`)

Controlled A/B/C/D (only available knowledge varied): A control (none), B generic+jiaje, C domectf,
D combined.

- Frozen **Phase 5 regression PASSED**: verified_solve_rate 0.833, false_verification 0,
  false_disproof 0, stopping 1.0, budget_violations 0, `ctf_agent` fingerprint unchanged
  (`ead35256…`). Knowledge-dependent v2 regression re-confirmed (KAVS=2, safety preserved).
- **1 knowledge-attributable verified transfer solve** (config C, DomeCTF corpus).
  - The transfer was **SQL injection**.
  - **Control was blocked** on the same challenge.
  - DomeCTF knowledge enabled the **typed SQLi candidate hypothesis and the discriminating probe**,
    which the frozen pipeline then verified against a **new** (non-historical) flag → STOP.
  - **False verification / false disproof remained zero.**
  - The **easy challenge remained on the fast path** (0 retrievals).
  - **Combined corpus (D) did not reproduce** the DomeCTF transfer, due to **retrieval dilution** in
    the larger combined corpus (the relevant record dropped out of top-k).
  - The current executable **knowledge-to-action bridge is limited to SSTI and SQL injection**;
    DomeCTF's only bridgeable mechanism is SQL injection.
- Historical-reference retrieval recall@5: self-recall 1.0, mechanism-recall ≈ 0.844
  (memorization/retrieval measurement only — not a solve).
- Artifacts: `reports/domectf_ab_results.json`, `domectf_transfer_results.json`,
  `domectf_adversarial_results.json`, `domectf_performance_results.json`,
  `domectf_evaluation_report.md`; `regression/phase5_regression.json`, `regression/kd_v2_regression.json`.

## 8. Known limitations

- The Phase 5 benchmark is a **small (6-case) deterministic synthetic suite**; it is not evidence of
  general or real-world CTF-solving ability.
- The knowledge→action bridge can execute only **web SSTI and SQL injection**; the bulk of the
  corpora (pwn/crypto/forensics/osint/hardware/reverse) has **no executable environment** in the
  current harness and cannot yield a knowledge-attributable solve.
- Retrieval over a large **combined corpus dilutes** relevant records out of top-k (observed: the
  DomeCTF transfer solve did not survive corpus combination).
- DomeCTF corpus **reasoning-trajectory content is near-zero** (final writeups, not think-aloud);
  its value is technique/solution knowledge, not reasoning.
- Retrieval is **not integrated** into the production frozen solver; it is exercised only in the
  experiment harnesses.
- The three 2019 DomeCTF GitHub writeups are JS-rendered blob pages whose static HTML lacked the
  markdown body; their records carry identity but MISSING solution content (documented, not fixed).
- Constitution provenance: no single in-repo file enumerates all 28 principles verbatim; six
  principle names are reconstructed (see `AGENT_CONSTITUTION.md`).

## 9. Current next objective

**REAL-WORLD CTF SOLVING AND EVALUATION.** Not another architecture phase.

Explicitly out of scope unless the user requests it: ingesting more sources, recovering GitHub JS
content, building new solver architecture, adding specialists, fine-tuning, or reinforcement
learning. Frozen boundaries in `AGENT_CONTEXT.md` §8 remain in force.
