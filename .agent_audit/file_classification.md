# File Classification & Ingestion Strategy

Classifies the corpus into the A–H scheme. **Ingestion strategy** tells the future agent's memory
builder *how* to consume each class (full-parse, extract-only, index-by-reference, or skip).
Principle: **information density over volume** — most bytes in this workspace are low-value scratch.

| Class | What it is | Where (representative) | Importance | Ingestion strategy |
|-------|-----------|------------------------|------------|--------------------|
| **A. High-value knowledge** | solved writeups, technique playbooks, challenge log, mistakes/corrections, reference index | `writeups/*`, `.kiro/TRAINING_NOTES.md`, `.kiro/MISTAKES_AND_LESSONS.md`, `.kiro/MISTAKES_AND_CORRECTIONS.md`, `.kiro/REFERENCE_jiegec.md`, `knowledge/*` | **CRITICAL** | Full-parse → distill into Technique + Trajectory + Failure memory. This is the seed corpus. |
| **B. Expert trajectories** | the reasoning path inside each solved writeup | `writeups/20-cloudnine`, `21-timeseries-trap`, `19-impossible-groth16`, `23-cry-pto`, `24-big-win`, `25-polynomial-evaluator`, `26-pickle`, root `KOHLI_*`, `VAULTNET_*`, `EQUATOR_*` | **CRITICAL** | Extract as step sequences (see `trajectories/`). Do NOT collapse to "tool→flag". |
| **C. Failure intelligence** | documented dead-ends, misdiagnoses, wasted effort | `.kiro/MISTAKES_AND_LESSONS.md`, `.kiro/MISTAKES_AND_CORRECTIONS.md`, FAILED table in TRAINING_NOTES, `writeups/22-dark-cover-vm`, `27-jailincpython`, `26-phault`, `25-neon-skies` | **CRITICAL** | Extract as failure records with a cause taxonomy (see `failures/`). Highest anti-repeat value. |
| **D. Raw artifacts** | binaries, APK, images, wav, pcap-like, disk images, db, onnx, wld, archives | `*.zip/.rar/.iso/.apk`, `*.png/.jpg/.wav`, `challenge_final*.onnx`, `AWholeNewWorld.wld`, `historian_cache.db`, `Cases/`, `disk1_extracted/` | **MED** (evidence, not knowledge) | **Index by reference only** (path + type + which challenge). Never load into agent context; re-open on demand. Note the 5× ONNX / duplicate zip redundancy. |
| **E. Tooling** | env setup, Docker, MCP servers, helper scripts | `ctf-env/`, `hexstrike-ai/`, `ctf_solver_mcp/`, `CTF-Solver/`, `node_modules/` | **MED / LOW** | Extract capability + env-dependency facts into Tool memory. Note Docker deleted; MCPs uninstalled. |
| **F. Challenge-specific implementations** | one-off exploit scripts, custom solvers, payloads | most of the 1,310 root `.py` (`cn_*.py`, `waf_*.py`, `tp_*.py`, `kohli_*.py`, `aiml_*.py`), `emu2.py`, `wld_*.py`, `chal*.c/.py` | **LOW individually / MED as patterns** | **Cluster by theme prefix, sample 1–2 representatives per cluster**, extract the reusable pattern into Technique memory, then index the rest by reference. Do not read all. |
| **G. Scratch / low-value** | duplicate files, tool logs, debug leftovers, generated output, progress snapshots | `*_out.txt`, `waf_gdb_*.txt`, `phantom_accounts_progress_*.csv`, `foremost_output/`, `scalpel_output/`, `__pycache__/`, dup archives, dup ONNX | **NONE** | **Skip.** Optionally keep a one-line "exists" note. Never ingest. |
| **H. Legacy / conflicting instructions** | inflated/aspirational claims, obsolete env assumptions, drifting duplicate logs | `ctf_solver_mcp/COMPLETE_CAPABILITIES.md`, `.kiro/ENV_STATUS.md` (Docker), `PROJECT_CONTEXT.md`/`CTF_BRAIN.md`/`CTF_PLAYBOOK.md` (overlap/drift) | **REVIEW** | Do not ingest as rules. Catalog conflicts in `legacy_conflicts.md`; keep files untouched. |

## Cluster map of the 1,310 root `.py` (theme prefix → challenge, sample-don't-dump)
`tp_*`/`temporal_*`/`timeseries_*` (~50) → timing-forensics twins · `stolen_*` (36) → Stolen Schematics · `kohli_*` (28) → Kohli · `kaal*` (27) → Kaalchakra misc · `vault*` (24) → VaultNet/QuantumVault · `deckforge_*` (22) → DeckForge · `waf_*` (20) → WAF pwn · `cn_*` (18) → CloudNine · `ghost_*` (18) → Ghost Draft/Pipeline · `aiml_*` (14) → ONNX/AIML · `nuclear_*` (13) → Nuclear web chain · `quantumvault_*` (12) → QuantumVault · `spacectf_*` (10) → SpaceCTF pentest · smaller: `stones/knock/flight/board/chord/qr/race/ssrf/jwt/onnx/apk/disk`.
**Rule:** one representative read per cluster is enough to recover the technique; the rest are iteration noise.

## What to ingest FIRST (highest density)
1. `.kiro/TRAINING_NOTES.md` + `.kiro/MISTAKES_AND_LESSONS.md` + `.kiro/MISTAKES_AND_CORRECTIONS.md`
2. `writeups/` (all 30 — small, dense)
3. `.kiro/REFERENCE_jiegec.md`
4. `knowledge/CHALLENGE_CATALOG.md` (from prior audit; unifies the scattered flags)
Everything else: index-by-reference or skip.

## What to NEVER bulk-load
- The 1,310 `.py`, the 211 images, the 5× ONNX, all archives, all `*_out.txt`. Reference only.
