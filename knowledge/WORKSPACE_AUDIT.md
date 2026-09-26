# Workspace Audit Report

**Scope:** full audit of `F:\mission-git-hackss\mission-git-hackss` to convert historical CTF work
into structured knowledge. **Constraint honored: create-only. No existing file was modified, moved,
renamed, or deleted.** All outputs live under the new `knowledge/` folder.

---

## 1. What this workspace is
A long-running, single-operator CTF working directory spanning **9+ CTF events**
(HackWars/TDHT, Chakravyuh/HexNova, Kaalchakra, VishwaCTF, ctf7, K17/secso, NNS, PwnSec, plus
side/practice challenges) and some real-world pentest assessments. It is "messy by design" —
rapid live-competition iteration left ~2,000 loose files at the root.

## 2. Inventory (root level)
| Group | Count | Notes |
|-------|-------|-------|
| `.py` scratch/solver scripts | **1,310** | throwaway iterations (`absolute_final_*`, `advanced_*`, `aggressive_*`, `aiml_*`, `tp_*`, `waf_*`, `cn_*`…). Signal-to-noise is low; many are near-duplicates. |
| `.md` docs | 83 | ~55 are per-challenge writeups/status reports; the rest are tool guides & pentest reports & 3 meta-index docs. |
| `.txt` docs | 114 | ~30 challenge writeups + many `*_out.txt` tool logs, wordlists, recon dumps. |
| Images (`.png`/`.jpg`/`.bmp`/`.gif`) | 211 | stego/forensics artifacts + intermediate renders. |
| `.wav` | 18 | audio-stego challenges. |
| Web sources (`.html`/`.js`/`.css`) | 102 | captured challenge frontends. |
| Archives (`.zip`/`.rar`/`.iso`/`.apk`/`.tar.gz`) | ~40 | packaged handouts (several duplicated, e.g. `handout (1..8).zip`, `stones_eMfRx10 (1).zip`). |
| `.bin` | 32 | collisions (`md5_coll_*`, `unicoll*`, `puppy*`), LSB extracts, carve output. |
| `.onnx` | 5 | **all copies of the same 42 MB model** (`challenge_final*.onnx`) — ~205 MB of duplication. |
| `.json`/`.csv` | 31 | session/state dumps, `phantom_accounts_progress_*` (11 snapshots), pentest reports. |
| Other | — | `AWholeNewWorld.wld`, `historian_cache.db` (12 MB), `validator.wasm/.wat`, `flight_record.dat`, wordlists incl. `rockyou.txt`. |
| **Top-level directories** | 60+ | mostly `*_extracted/` handout unpacks + per-challenge scratch dirs (see catalog). |

## 3. Knowledge assets found (4 layers, not reconciled with each other)
1. **`.kiro/` playbooks (current source of truth):** `START_HERE`, `TRAINING_NOTES` (CHALLENGE LOG),
   `MISTAKES_AND_LESSONS`, `MISTAKES_AND_CORRECTIONS`, `REFERENCE_jiegec`, `ENV_STATUS`. High quality.
2. **`writeups/` folder:** 30 writeup files (numbered `01`–`27` + `AWholeNewWorld` + `_reference/`).
3. **Root meta-index docs (older, overlapping):** `CTF_BRAIN.md`, `CTF_PLAYBOOK.md`, `PROJECT_CONTEXT.md`.
4. **Root per-challenge docs (~55 `.md` + ~30 `.txt`):** the bulk of historical solves — **mostly never
   folded into layers 1–2.**

## 4. Coverage gap — the core finding
The `.kiro` CHALLENGE LOG records **~25 solved** challenges. The actual workspace contains
**~70 catalogued challenges (~45 with CONFIRMED flags).** So the structured knowledge base captures
only about **one-third** of the real solved history.

**Solved work documented ONLY at root (absent from `.kiro` log AND `writeups/`):**
- Entire **Kaalchakra** event (~20 challenges): Calculator, Equator/Null Island, Final Whisper,
  Forgotten Sequence, Greetings 1&2, Guarded Input, Hidden Comment, Kohli, Online Store, VaultNet,
  Varys, Suspiciously Attentive, TATA, Welcome, Words of Throne, Signal & Noise, Dream Within a Dream,
  Impossible Road, Feedback Form, Budapest, Ghosts in Disk, …
- **VishwaCTF:** Flag Market, Ghost Draft.
- **ctf7:** ProfileHub (WASM + prototype pollution).
- **Chakravyuh P2 set** present in `CTF_PLAYBOOK.md` only: Breach Stark, Sanctum Archives, Ultron,
  HYDRA, ROT47 Quantum, Loki's Cipher, Kavach-X, Chakra Story.
- **Side:** Independence Day, Tubular Druid, Joyful Mandazi.

**Inconsistencies detected:**
- `writeups/14-kavach-x/` and `writeups/16-lokis-cipher-phase1/` are **empty** (no `writeup.txt`),
  yet both are recorded as solved in `CTF_PLAYBOOK.md`. → writeups never written.
- `writeups/25-online-roulette/writeup.md` describes the exploit but does **not** contain the literal
  flag; the actual flag `K17{th1s_minib0lt_guy_must_b3_rlly_lucky_huh}` is only in `ro_exploit_out.txt`.
- CHALLENGE LOG numbering has two `#24` and two `#25` rows (big-win/reverse-captcha; neon/roulette/poly).
- **Phish to Fortune** is in `.kiro/TRAINING_NOTES` (#22) but its exact accepted flag format was never
  confirmed (content `flag{y0u F0und 0s}` derived; format unresolved).

## 5. Duplicate / competing knowledge (single-source-of-truth risk)
- **Three root meta-index docs** (`CTF_BRAIN`, `CTF_PLAYBOOK`, `PROJECT_CONTEXT`) overlap with each
  other and with `.kiro/TRAINING_NOTES` + `.kiro/START_HERE`. Flags/techniques are copied across all
  four with drift. There is no single canonical index — this catalog is the first attempt to unify them.
- **Duplicated large binaries:** 5× `challenge_final*.onnx` (~205 MB total), `greetings.zip` +
  `greetings_JQWfzrE.zip` (17 MB each), `stones_eMfRx10*.zip`, `handout (1..8).zip`, `chall_media*`.
- **Redundant status docs:** e.g. `STOLEN_SCHEMATICS_*` ×5, `KOHLI_*` ×4, `HACKWARS_*` ×3,
  `SMARTKOPARGAON_*` ×3, `SPACECTF_*` ×3, `BETRAYAL_*` ×3, `VAULTNET_*` ×3.

## 6. Non-challenge material (worth separating mentally)
- **Tool guides** (not challenges): `COMMIX_*`, `HASHCAT_*`, `KALI_*`, `SKIPFISH_*`,
  `install_tesseract.md`, `GET_SDL2_AND_RUN.md`.
- **Real pentest / bug-bounty reports** (appear to be assessments, not CTF): `HACKWARS_*`,
  `SMARTKOPARGAON_*` (+`.json`), `SPACECTF_*` (+`.json`), `CYBERSPACE_VULN_REPORT.json`,
  `TEAM_T1_ASSESSMENT_REPORT.md`, `FINAL_SECURITY_REPORT.md`, `SECURITY_*`.
- **Tooling projects:** `ctf-env/` (Docker toolchain — image was deleted by the user to save space;
  Dockerfile/SETUP remain), `hexstrike-ai/`, `ctf_solver_mcp/`, `CTF-Solver/` (MCP Kali server),
  `node_modules/` (used by the JS/jsdom web-XSS work), nested `mission-git-hackss/` sub-project.

## 7. Environment note (changed since docs were written)
`ctf-env/SETUP.md` and `.kiro` describe a built Docker image `ctf-env:latest`. **The user has since
deleted all Docker data to reclaim space.** Current native capability (verified this session):
Python 3.10 with `capstone, unicorn, pillow, numpy, requests, pycryptodome (Crypto), z3, sympy,
pwntools, oletools` (missing `gmpy2`, `angr`); Python 3.13 also present; 7-Zip; WSL2 engine present
but no general Linux distro. ELF-execution (qemu) is the main lost capability — install a slim WSL
Ubuntu on demand only if a pwn/rev challenge needs to *run* a Linux binary.

## 8. Recommendations (all non-destructive; nothing done automatically)
1. **Adopt `knowledge/CHALLENGE_CATALOG.md` as the single index** and, going forward, add new solves
   there (or regenerate). Treat the 3 root meta-index docs as historical/read-only.
2. **Backfill the missing writeups** for CONFIRMED-flag challenges that only have root docs
   (Kaalchakra set, VishwaCTF, ProfileHub, Chakravyuh P2) into `writeups/NN-slug/` — the raw material
   already exists in the root `*_WRITEUP.md` files; it just needs to move into the standard structure.
2b. **Write the two empty writeups** (`14-kavach-x`, `16-lokis-cipher-phase1`) from `CTF_PLAYBOOK.md`.
3. **Re-verify ⚠️ CANDIDATE flags** before ever submitting: Crackme (guessed), Board, Spartans,
   Final Whisper (two conflicting values), Words of Throne, Feedback, Budapest spacing.
4. **De-clutter later (optional, only with explicit go-ahead):** the 1,310 root `.py` scratch files
   and duplicate large binaries could move into per-challenge `archive/` folders to cut noise and
   ~250 MB+ of duplication. **Not done here** (create-only audit).
5. **Fix the CHALLENGE LOG numbering collisions** (two `#24`, two `#25`).

## 9. Integrity statement
This audit **created** the following new files only:
- `knowledge/README.md`
- `knowledge/CHALLENGE_CATALOG.md`
- `knowledge/TECHNIQUE_INDEX.md`
- `knowledge/WORKSPACE_AUDIT.md`

No pre-existing file was edited, renamed, moved, or deleted. Two scratch files used during scanning
(`_audit_rootdocs.tmp.txt`, `_audit_flags.tmp.txt`) were created by the audit and removed at the end;
if present, they are safe to delete.
