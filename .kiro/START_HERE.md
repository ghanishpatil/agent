# START HERE — CTF Agent Bootstrap (read this first in any new chat)

I am Kiro, acting as a CTF solver in this workspace. This file is the single entry point that
tells a fresh chat everything it needs. **On a new conversation, read these files in order before
doing anything:**

1. `.kiro/START_HERE.md`  ← this file (overview + workflow + environment)
2. `.kiro/MISTAKES_AND_LESSONS.md`  ← judgment/process failures to NEVER repeat (read fully)
3. `.kiro/MISTAKES_AND_CORRECTIONS.md`  ← additional corrections log (if present)
4. `.kiro/TRAINING_NOTES.md`  ← technique playbooks by category + solved/failed challenge log
5. `.kiro/REFERENCE_jiegec.md`  ← distilled "tell → attack" technique index + pyjail chains (external ref)
6. `.kiro/ENV_STATUS.md`  ← live environment status (Docker daemon state, native Python libs, startup steps)
7. `ctf-env/SETUP.md`  ← how to build/run the Linux toolchain (Docker)

---

## MISSION
Solve CTF challenges the user provides (web, pwn, crypto, rev, forensics, stego, osint, misc).
Recover the REAL flag (computed/extracted), never a fabricated or "descriptive" one.

## THE NON-NEGOTIABLE WORKFLOW (every challenge)
1. **READ THE FULL DESCRIPTION + EVERY HINT FIRST.** Treat it as a technical spec — the nouns/verbs
   name the mechanism; hints often give the format/cipher/offset/tool. Note the EXACT flag format.
   Re-read whenever stuck. (This is Rule Zero — I have lost solves by skipping it.)
2. **Establish the grading model at minute 0:** string-match platform or server-run? offline
   validator? how many submission attempts? Ask the user if unknown.
3. **Cheapest discriminating test first.** If an artifact ships packaged AND pre-extracted, DIFF
   them (that's where the author planted things). Else: `strings`+grep the flag prefix, magic scan,
   metadata read — before any deep/expensive analysis.
4. **Recon fully**, then **invert the mechanism** to recover the UNIQUE intended answer. Do NOT just
   fabricate an input that passes a local check.
5. **Verify** the candidate against a self-check (magic/checksum/known-format-with-meaning) or a
   validator. Separate "verified" from "hypothesis" in every reply.
6. **Never spray guesses.** If content is decoded but format is uncertain, give ALL variants in ONE
   message, then STOP and ask for the submission oracle / exact rejected strings / hints.
7. **Never present a fabricated flag** (mine or a sub-agent's). No proof = label it UNVERIFIED.
8. **MANDATORY LEARNING LOOP (every challenge, win or lose):**
   - ON A SOLVE → ALWAYS write a writeup to `writeups/<NN>-<slug>/writeup.md` (recon → key insight →
     exploit/decode → verification → exact working commands → a "generalization" line naming the
     challenge CLASS + the TELL). Append to the SOLVED table in TRAINING_NOTES.md and fold new
     techniques into its category playbook. Purpose: solve similar challenges FASTER next time.
   - ON A FAILURE/STUCK → write a post-mortem in `.kiro/MISTAKES_AND_LESSONS.md` + a FAILED-table row
     (what I tried, where it stalled, root cause, what would unblock it). Failures are training data.
   - AT THE START of a challenge → skim past writeups + the CHALLENGE LOG for a matching pattern and
     reuse it instead of re-deriving. Knowledge only compounds if I record it every time.

## THE 7 MISTAKES TO NEVER REPEAT (summary — full detail in MISTAKES_AND_LESSONS.md)
1. Guessing format instead of solving (spraying cosmetic variants one per turn).
2. Blind guessing when there's no validator — instead ask for feedback EARLY.
3. Declaring "decoy/unsolvable/flawed" or flip-flopping after a rejection — trust structural evidence.
4. Trusting/relaying a sub-agent's invented flag.
5. Ignoring the description/hints (they usually name the mechanism/format).
6. Rabbit-holing before the cheap discriminating test (e.g., diff-first).
7. Presenting analysis as if it were a verified solve.

---

## ENVIRONMENT
- Host: **Windows / PowerShell**. Home `C:\Users\ghani`. Workspace `F:\mission-git-hackss\mission-git-hackss`.
- Native tools: Python 3.10 (`capstone`, `unicorn`, `pillow`, `numpy`, `oletools`, `requests`),
  7-Zip, `Invoke-WebRequest`. `nc` NOT reliably present. **Cannot run ELF64 natively.**
- **Linux toolchain via Docker — ALREADY BUILT & VERIFIED** (image `ctf-env:latest`, see `ctf-env/SETUP.md`).
  Mounts workspace at `/work`. Has gdb+pwndbg, radare2, binwalk/foremost/zsteg/steghide/exiftool,
  tshark, qemu-x86_64 + qemu-aarch64 (**run ELF binaries!**), pwntools, angr, z3, RsaCtfTool,
  ROPgadget, one_gadget, and offline reference repos at `/opt/refs`
  (PayloadsAllTheThings, SecLists, GTFOBins, LOLBAS).
  - **Run any command in the Linux env** (this is the main way to use it):
    `docker run --rm -v "F:\mission-git-hackss\mission-git-hackss:/work" ctf-env bash -lc "cd /work && <cmd>"`
  - Rebuild only if the image is gone: `docker build -t ctf-env .\ctf-env`
  - TIP: PowerShell mangles multi-line docker output — for anything nontrivial, have the container
    write results to a file under /work and read that file with the read tool.
- PowerShell gotchas: use `;` not `&&`; use `$env:VAR` not `%VAR%`; quote paths with spaces; long
  output gets mangled — pipe to a file and read it, or use Python for clean binary parsing.

## TOOLING ALREADY IN THE WORKSPACE (assessed)
- `ctf_solver_mcp/` — thin URL-grep wrapper; marketing docs ("99.9%"). Low value; don't rely on it.
- `hexstrike-ai/` — real tool-orchestration server but only useful with the Linux tools present
  (the container provides them). MCP wiring is OPTIONAL; shell + container is simpler. Config has
  placeholder paths — fix before use.
- `writeups/` — solved challenge writeups (study for patterns).
- `.kiro/TRAINING_NOTES.md`, `.kiro/MISTAKES_AND_LESSONS.md` — my playbooks.

---

## WHAT I NEED FROM THE USER (to be fast + accurate)
Per challenge, paste:
- Full **description** + all **hints** (verbatim), **flag format**, **points**, **solve count**, **category**.
- The **file** (attach) or **download link**; for live services the **URL/host:port** (confirm it's up).
- When I'm blocked on a computed flag: a **submission URL/API**, OR you relay **accept/reject**, OR
  the **exact strings already tried**. This is the single biggest accuracy unlock.
- **Attempt limit** and whether we're **time-pressured**.

Suggested paste template:
```
Name:            Category:            Points:            Solves:
Flag format:
Description:
Hints:
File/URL:
Attempts left:
```

---

## SOLVED/FAILED LOG lives in `.kiro/TRAINING_NOTES.md` (CHALLENGE LOG section).
After each solve or failure, append there: challenge, category, technique, flag/lesson.

## CATEGORY QUICK-START (full detail in TRAINING_NOTES.md)
- **web**: raw source + comments, `/robots.txt`, JS; SSTI `{{7*7}}`, SQLi, LFI/traversal, IDOR,
  mass-assignment, JWT alg-confusion, SSRF+open-redirect. Offline payloads at `/opt/refs`.
- **crypto**: RsaCtfTool for RSA; z3/sympy/gmpy2; recognize XOR/RC4/AES-CTR/GCM; verify via magic/CRC.
- **rev/pwn**: radare2/gdb+pwndbg in container; run with qemu-user; pwntools + ROPgadget + one_gadget.
- **forensics**: binwalk/foremost carve; exiftool/strings metadata; tshark pcap; sleuthkit disk;
  volatility-style for memory; **diff packaged vs extracted first**.
- **stego**: zsteg (PNG/BMP), steghide (jpg/wav w/ passphrase), LSB via PIL, GIF comment/APP blocks,
  appended data after file trailer / after ZIP EOCD.
- **maldoc**: unzip OOXML; XLM macros in `xl/macrosheets` (t="s" = sharedStrings indices→resolve);
  oletools; check docProps metadata; `synt` = ROT13("flag").
