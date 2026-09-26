# .agent_audit/ — Structured Knowledge Base for a Future Autonomous CTF Agent

Read-only audit of this workspace's historical CTF work, converted into ingestible, evidence-tagged
knowledge. **Nothing outside this folder was created, and nothing existing was modified, moved, or
deleted.** Paths reference existing artifacts; no large files were copied.

## Contents
| File / dir | What it is |
|------------|-----------|
| `workspace_inventory.md` | Directories, file-type census, challenge-dir map, environment, corpus scale. |
| `file_classification.md` | A–H classification + per-class **ingestion strategy** (full-parse / extract / index-by-ref / skip) + the 1,310-`.py` cluster map. |
| `knowledge/technique_memory.jsonl` (+README) | **Dataset A** — 30 reusable techniques (tell→test→interpret→verify), confidence-labelled. |
| `trajectories/trajectories.jsonl` (+README) | **Dataset B** — 12 reconstructed expert solving paths (hypothesis→action→observation→interpretation→update→verify). |
| `failures/failures.jsonl` (+README) | **Dataset C** — 12 failure records with a cause taxonomy; enforces "failure ≠ disproof". |
| `tools/tool_memory.jsonl` (+README) | 19 tool profiles + the **environment dependency matrix** (Docker removed → native-first). |
| `categories/category_playbooks.md` | Adaptive per-category knowledge (recon, cheap tests, decoys, verification, failure patterns). |
| `memory_schema/schemas.md` | The 5 proposed memories (technique/experience/failure/tool/challenge-pattern) + **memory-as-priors** semantics. |
| `legacy_conflicts.md` | Old rules that conflict with the constitution (OLD → WHY → NEW), incl. inflated MCP claims and stale Docker assumptions. |
| `architecture_recommendation.md` | Next-gen agent = 7 strategic components + 5 execution layers; maps all 28 principles; build order. |

## Provenance & trust
Every record carries a `confidence` label (`VERIFIED > SUPPORTED > PLAUSIBLE > HISTORICAL >
CHALLENGE_SPECIFIC > LOW_CONFIDENCE`) and a `source` path. Flags are transcribed from historical docs,
**not re-verified live in this audit**. The JSONL files are validated as parseable.

## Primary sources mined
`writeups/` (30), `.kiro/{TRAINING_NOTES,MISTAKES_AND_LESSONS,MISTAKES_AND_CORRECTIONS,REFERENCE_jiegec,ENV_STATUS}.md`,
`knowledge/` (prior audit's CHALLENGE_CATALOG/TECHNIQUE_INDEX), and sampled root writeups
(KOHLI, VAULTNET). Tooling assessed: `ctf_solver_mcp/`, `hexstrike-ai/`, `ctf-env/`.

## How the future agent should consume this
1. Load Failure Memory + Verification rules FIRST (biggest historical losses were misclassified
   failures and fabricated flags).
2. Load Technique + Challenge-Pattern memory as priors; Tool memory for capability awareness.
3. Use Experience trajectories for analogy, not as scripts.
4. Everything in classes D/F/G stays **indexed by reference** — never bulk-loaded.
