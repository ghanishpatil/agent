# Workspace Inventory

> READ-ONLY audit snapshot. Paths are references, not copies. Counts are approximate (metadata-based).
> Workspace root: `F:\mission-git-hackss\mission-git-hackss`.

## Top-level shape
- **~2,007 loose files at root** + **60+ directories**. "Messy by design" — live-competition scratch.
- Dominant type: **1,310 `.py`** (mostly throwaway solver iterations, low S/N).

## File-type census (root, approx)
| Type | Count | What it mostly is |
|------|-------|-------------------|
| `.py` | 1,310 | one-off solvers/iterations (`absolute_final_*`, `advanced_*`, `aiml_*`, `tp_*`, `waf_*`, `cn_*`) |
| `.md` | 83 | ~55 per-challenge writeups/status + 3 meta-index docs + tool guides + pentest reports |
| `.txt` | 114 | ~30 writeups + tool logs (`*_out.txt`), wordlists, recon dumps |
| `.png/.jpg/.bmp/.gif` | 211 | stego/forensics artifacts + intermediate renders |
| `.html/.js/.css` | 102 | captured challenge frontends (web/XSS work) |
| `.wav` | 18 | audio-stego challenges |
| archives (`.zip/.rar/.iso/.apk/.tar.gz`) | ~40 | packaged handouts (many duplicated: `handout (1..8).zip`) |
| `.bin` | 32 | hash collisions, LSB extracts, carve output |
| `.onnx` | 5 | **all copies of one 42 MB model** (~205 MB dup) — ONNX-weights rev challenge |
| `.json/.csv` | 31 | session/state dumps, `phantom_accounts_progress_*`, pentest reports |
| other | — | `AWholeNewWorld.wld`, `historian_cache.db` (12 MB), `validator.wasm/.wat`, `flight_record.dat`, `rockyou.txt` |

## Key directories (purpose)
| Dir | Role | Audit value |
|-----|------|-------------|
| `.kiro/` | operator playbooks: START_HERE, TRAINING_NOTES, MISTAKES_AND_LESSONS, MISTAKES_AND_CORRECTIONS, REFERENCE_jiegec, ENV_STATUS, specs/sector-7-solver | **HIGH** (knowledge + failure intel) |
| `writeups/` | 30 writeup files (`01`–`27` + AWholeNewWorld + `_reference/`) | **HIGH** (trajectories) |
| `knowledge/` | prior audit output (CHALLENGE_CATALOG, TECHNIQUE_INDEX, WORKSPACE_AUDIT, README) | HIGH (my earlier pass) |
| `ctf-env/` | Docker toolchain (Dockerfile, SETUP, smoke) — **image deleted by user** | MED (env ref, now inert) |
| `ctf_solver_mcp/` | thin URL-grep wrapper, inflated marketing docs | **LOW** (+ legacy conflict) |
| `hexstrike-ai/` | 3rd-party tool orchestrator, **never installed** (disk space) | LOW (optional) |
| `CTF-Solver/` | MCP↔Kali bridge concept | LOW/aspirational |
| `node_modules/` | JS deps for jsdom+jQuery web-XSS harnesses | tooling dependency |
| `*_extracted/`, per-challenge dirs (~50) | unpacked handouts + scratch (see catalog) | RAW artifacts |
| `mission-git-hackss/` (nested) | sub-project `api/config/core/data/docs` — looks like an app, not a handout | inspect separately |

## Challenge working directories → challenge (resolved map)
`bigwin`=big-win(K17) · `custom_vm`=Dark Cover VM · `emm`=Encrypted Malware in Memory · `imp_ex`=impossible(Groth16) · `timeseries_trap`+`temporal_paradox`+`tp_files`+`blobs`(R9CF)=timing forensics twins · `phish`=Phish-to-Fortune maldoc · `pickle_chal`=pickle jail · `jail_chal`=jailincpython · `poly`/`polytest`=polynomial-evaluator · `neonskies_src`=Neon Skies · `phault_src`=PHault · `waf_chal`/`waf`=ret2libc pwn (ships libc.so.6+ld.so.2) · `game`/`SDL2_temp`=SDL2 PE · `apk_extracted`/`KaalRaj_extracted`=KaalRaj APK · `stones_extracted`/`mind_stone_3rd_extracted`=Infinity Stones audio/RSA · `disk1_extracted`/`disk_files`=disk forensics · `Cases`=multi-PDF forensics (Case-1..6, protected) · `chakra_story_ctf_extracted`=Chakra Story · `spidy_*`=Spider Whispers · `ghcr_extract`=Stolen Schematics registry · `d1`=driveone · `maw`=make-a-wish · `hb1`=huge-binary-1 · `notjson_x`/`dptest`=notjson(Node) · `whatsnew`=What's New web · `taptap`/`taptap_x`=taptap · `AUTOMATONS_SECRET`=automatons.

## Knowledge layers found (4, not reconciled with each other)
1. `.kiro/` playbooks (current operator source of truth; high quality).
2. `writeups/` (30 structured writeups).
3. Root meta-index docs (older, overlapping, drifting): `CTF_BRAIN.md`, `CTF_PLAYBOOK.md`, `PROJECT_CONTEXT.md`.
4. ~55 root per-challenge `.md` + ~30 `.txt` (the bulk of solves — mostly never folded into 1–2).

## Events represented (≥9)
HackWars/**TDHT**, Chakravyuh/HexNova (**CHAKRA**), **Kaalchakra** (Kaal), **ctf7** (Kohli/ProfileHub), **VishwaCTF**, **K17/secso**, **NNS**, **PwnSec** (pwnsec), plus side/practice (**CTF{}**, **BPCTF**) and one deleted-tool challenge set. Plus real pentest reports (SmartKopargaon, SpaceCTF, CyberSpace, Team T1) that are **not CTF**.

## Environment (verified this session, supersedes ENV_STATUS.md)
- Host: Windows / PowerShell. **Docker removed by user** (image + daemon gone).
- Native Python **3.10.7**: `capstone, unicorn, PIL, numpy, requests, Crypto(pycryptodome), z3, sympy, pwntools, oletools`. Missing: `gmpy2`, `angr`. Python 3.13 also present.
- 7-Zip present. WSL2 engine present but **no general Linux distro**. **Cannot execute ELF natively** (qemu was the lost capability).
- Node/`node_modules` present (used for jsdom+jQuery XSS harnesses).

## Approx knowledge scale (for training-corpus sizing)
- **~30 formal writeups** + **~55 informal root writeups** ≈ **~70–85 distinct challenges** documented.
- **~45 CONFIRMED flags**, ~12 CANDIDATE/per-instance, ~8 documented UNSOLVED/failures.
- Failure post-mortems: **~10 high-detail** (in `.kiro/MISTAKES_*`).
