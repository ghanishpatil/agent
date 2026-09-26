# Legacy Conflicts

Old instructions/assumptions in the workspace that conflict with the CORE AGENT CONSTITUTION.
**Nothing is deleted or modified** — this only catalogs conflicts so the new agent supersedes them.
Format: OLD RULE → WHY PROBLEMATIC → NEW PRINCIPLE (constitution # in parentheses).

---

## C1. "Solve any CTF — 99.9% success rate / 100+ types / self-training RL" (ctf_solver_mcp/COMPLETE_CAPABILITIES.md)
- **OLD:** Marketing doc asserts near-universal automated solving, fabricated per-category success-rate tables, RL/self-training, "no blind guessing" by branding.
- **WHY PROBLEMATIC:** Unbacked by any real solve in the corpus; presents fabricated metrics as fact. Directly violates **No Fabrication (13)**, **Zero Blind Guessing (3)**, **Hard Verification (12)**, **Evidence-Driven Reasoning (2)**. Relying on it would inject unverified confidence.
- **NEW PRINCIPLE:** Treat these claims as UNVERIFIED marketing. Capability is proven per-technique by evidence in Technique/Experience memory, with explicit confidence. No global success-rate claims.

## C2. "ctf-env Docker image is ALREADY BUILT & VERIFIED (ctf-env:latest)" (start_prompt.txt, ctf-env/SETUP.md)
- **OLD:** Bootstrap says the Linux toolchain is ready; many playbooks assume qemu/zsteg/RsaCtfTool/tshark are one `docker run` away.
- **WHY PROBLEMATIC:** **Docker was deleted by the user.** Acting on this assumption causes tool-not-found failures misread as challenge failures. Violates **Resource & Environment Awareness (19)**, **Evidence Freshness (26)**, **Preconditions & Recovery (27)**.
- **NEW PRINCIPLE:** Verify environment at session start (Tool Memory `availability`). Prefer native Python; container/WSL tools require an explicit availability check + setup step before use.

## C3. ".kiro/ENV_STATUS.md Docker daemon startup guidance"
- **OLD:** Detailed steps to start Docker Desktop from a specific path and poll `docker info`.
- **WHY PROBLEMATIC:** Now obsolete (Docker removed); following it wastes turns. Violates **Evidence Freshness (26)**, **Dead-End Detection (24)**.
- **NEW PRINCIPLE:** Environment facts are session-verified and dated; obsolete startup paths are ignored until the operator reinstalls.

## C4. Three overlapping, drifting meta-index logs (CTF_BRAIN.md, CTF_PLAYBOOK.md, PROJECT_CONTEXT.md) + partial duplication with .kiro/TRAINING_NOTES.md
- **OLD:** Four separate "solved flag / technique" logs with copy-paste drift; no single source of truth. Some challenges (e.g. online-roulette flag) recorded in one file only.
- **WHY PROBLEMATIC:** Conflicting/duplicated memory → contradictory priors. Violates **Persistent CTF Knowledge (16)**, **Action Deduplication (22)**, **Clean Internal State (20)**.
- **NEW PRINCIPLE:** One canonical index (knowledge/CHALLENGE_CATALOG.md from the prior audit) + structured JSONL memories here. Legacy logs are HISTORICAL, read-only inputs, not authorities.

## C5. hexstrike-ai treated as an available orchestrator (CTF_SOLVER_GUIDE.md, QUICK_START.md)
- **OLD:** Guides describe a running server at :8888 with CTF endpoints.
- **WHY PROBLEMATIC:** QUICK_START itself states install is incomplete (disk space); server not running; most value needs the (now-absent) container tools. Assuming availability violates **Resource & Environment Awareness (19)**, **Autonomous Tool Orchestration (9)** (orchestrate only what exists).
- **NEW PRINCIPLE:** Mark uninstalled; use only if actually set up. Native Python + shell is the default toolpath.

## C6. Bootstrap "READ these files first" as authoritative operating rules (start_prompt.txt)
- **OLD:** A fixed 5-file read + 8-step workflow presented as the operating contract; assumes Docker and specific file layout.
- **WHY PROBLEMATIC:** The *judgment* content (Rule Zero, anti-spray, no-fabrication, learning loop) is excellent and should be kept; but the *environment/tooling* assumptions are stale, and a fixed linear bootstrap conflicts with **Adaptive Strategy (7)** and **Autonomous Ambiguity Resolution (18)**.
- **NEW PRINCIPLE:** Keep the judgment rules (they map 1:1 to the constitution). Replace the stale env/bootstrap parts with session-verified environment + evidence-gated planning.

## C7. "self-training / learns from each solve / knowledge.json auto-updates" (ctf_solver_mcp)
- **OLD:** Implies an automatic learning system already improves success over time.
- **WHY PROBLEMATIC:** No such loop is actually running; the real learning loop is manual prose logs in `.kiro`. Overstating automation violates **No Fabrication (13)**, **Failure Intelligence (15)** (which must be real, not claimed).
- **NEW PRINCIPLE:** Implement a REAL append-only learning loop into the five JSONL memories (win→technique+trajectory, loss→failure), with confidence + provenance.

## C8. Aspirational category coverage vs. actual corpus (ctf_solver_mcp lists blockchain/mobile/OSINT/IoT at high success)
- **OLD:** Claims strong coverage across categories barely represented in real solves.
- **WHY PROBLEMATIC:** Corpus is heavy on WEB/CRYPTO/REV/FORENSICS/PWN; thin on OSINT/MOBILE; absent on CLOUD/IOT/HARDWARE. Claiming coverage violates **Evidence-Driven Reasoning (2)**.
- **NEW PRINCIPLE:** Confidence is proportional to evidence; thin/absent categories are flagged as knowledge GAPS to fill, not strengths.

---
## What is NOT a conflict (keep as-is — high value)
- `.kiro/MISTAKES_AND_LESSONS.md`, `.kiro/MISTAKES_AND_CORRECTIONS.md`: the 7 mistakes, Rule Zero, anti-spray, diff-first, no-fabrication, invert-don't-satisfy — these ARE the constitution in prose. Promote to Failure Memory, don't discard.
- `.kiro/REFERENCE_jiegec.md`: dense, accurate tell→attack index. Promote to Technique Memory priors.
- `writeups/`: primary trajectory source. Keep and mine.
