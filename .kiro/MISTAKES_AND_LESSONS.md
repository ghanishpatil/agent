# CTF Self-Correction Log — Mistakes I Made & Rules To Never Repeat Them

Purpose: a brutally honest post-mortem of mistakes made in real sessions, converted into
hard rules and checklists. Read this BEFORE starting any challenge. Complements
TRAINING_NOTES.md (which holds technique playbooks). This file is about *judgment and
process failures*, not techniques.

The overarching failure pattern to kill:
> "I reverse the mechanism correctly, stall at the final flag recovery, then declare the
> challenge 'underdetermined / flawed / unsolvable' and hand the user arbitrary/constructed
> answers." — This is almost always MY error, not the challenge's.

---

## ★ RULE ZERO — READ THE DESCRIPTION PROPERLY, FIRST, EVERY TIME ★
Before touching any file, read the challenge description word-by-word and treat it as a
TECHNICAL SPEC, not flavor text. The hints are almost always in there. For every sentence, ask:
- What mechanism does this noun/verb name? ("walkthrough", "step", "quiet until the end" =
  per-step silent oracle; "underneath the 0s and 1s" = VM/bytecode; "cover" = decoy/hidden layer;
  a named seed/encoder/tolerance = key-derivation or channel spec.)
- What does it tell me about the flag's structure, length, format, or how it's checked?
- Does it hint the intended TECHNIQUE (invert, per-byte, timing channel, stego, etc.)?
Re-read it AGAIN whenever I get stuck — the unlock is usually a phrase I dismissed.
PROOF THIS MATTERS: in Dark Cover the line "every step quiet whether you're right or wrong,
won't tell you until the end" literally described a per-step oracle; I read it as flavor and
went down a monolithic-hash dead end. In Timeseries Trap the cadence/tolerance + "link-encoder
seeded with N bytes" lines WERE the entire key-derivation spec.
MORE PROOF (this session):
  - Phish to Fortune: "Sometimes the strings tell the whole story" + "hidden in the smallest
    details" → literally pointed at document metadata/strings. Reading it properly first would
    have sent me to `docProps/core.xml` immediately instead of last.
  - Encrypted Malware in Memory: "identify the CONTEXT associated with the complete malicious
    sequence, reconstruct its FRAGMENTED cryptographic material, and recover the AUTHENTICATED
    case result" → named all three sub-tasks (context string, key fragments, AEAD result).
  - CloudNine: "remote-ingestion pipeline may expose the master encryption material" → SSRF to
    an internal key. The brief named the whole chain.
  ALWAYS read the FULL description AND every hint tab before analysis. The user explicitly
  reminded me: "read the description of challenge properly first cuz many times the hints are
  given." Non-negotiable step 1.

## ★ THE 7 MISTAKES — NEVER REPEAT (check myself against these constantly) ★
1. **Declaring "unsolvable / underdetermined / flawed."** A scored challenge has a unique
   intended flag. That conclusion = alarm that MY assumption is wrong. Keep digging.
2. **Trusting a self-consistent emulator.** Matching behavior on random inputs ≠ understanding
   the intended check. Re-derive every handler; a self-consistent model can still be wrong.
3. **Presenting constructed/collision values as "the flag" & wasting submission attempts.**
   "An input that passes the local check" ≠ "the flag." Never spend the user's attempts on guesses.
4. **Rationalizing the dead-end** ("0 solves = broken"). 0 solves = hard. My job is the first solve.
5. **Ignoring hints in the description** (see RULE ZERO). The prompt is a spec; mine every word.
6. **Not establishing the validation/grading model first** (string-match vs server-run; offline
   validator? attempt count?). Do this at minute 0.
7. **Solving the wrong problem** — satisfying the checker instead of INVERTING it to recover the
   author's unique input. A final hash/compare usually sits on per-step constraints that DO
   determine the answer; don't assume "hash = one-way = unsolvable."

---

## PART A — CARDINAL MISTAKES (the ones that cost solves)

### A1. Declaring a challenge "unsolvable / underdetermined / flawed"
**What I did (Dark Cover):** Reversed a VM, found the gate was a 32-bit hash, concluded
"many inputs pass → no unique flag → challenge is flawed," and said so repeatedly.
**Why it's wrong:** A scored CTF challenge (esp. 2000 pts) with a clean provided binary has
a UNIQUE intended flag by definition. If my analysis concludes "no unique answer," the fault
is in MY assumptions, not the challenge.
**RULE:**
- NEVER conclude "unsolvable/flawed/underdetermined." Treat that conclusion as a alarm that
  I have a wrong assumption, and go hunt it.
- The existence of collisions in a checker does NOT mean the flag isn't recoverable — it means
  I'm solving the wrong problem (satisfy the gate) instead of the intended one (recover the
  author's input via inversion / per-step constraints).

### A2. Trusting a self-consistent emulator as "proof of understanding"
**What I did:** My Python model matched the binary's hash on 200/200 random inputs, so I
declared my understanding complete and the gate "just a hash."
**Why it's wrong:** Matching outputs on RANDOM inputs proves my emulator reproduces behavior;
it does NOT prove I understood the INTENDED check or the data flow that pins the flag. The
author's own writeup literally warns: *"a self-consistent emulator can still be wrong."*
**RULE:**
- Re-derive EVERY handler/opcode byte-by-byte from the real disassembly. Don't collapse a
  structure into "it's a hash" because the final value matches.
- Trace every store to its load, every comparison to its consumer. A comparison whose result
  I think is "incidental/dead" is exactly the KVSTORE-style trap.
- Validate the model two ways: (1) reproduces binary output, AND (2) reproduces the *intended
  solve logic* (per-step constraints that uniquely determine the answer).

### A3. Handing over constructed/arbitrary answers as "the flag"
**What I did:** Generated collision inputs (MITM/Z3) that make the binary print GRANTED and
presented them as candidate flags. Burned the user's real submission attempts (14/100) and
eroded trust.
**Why it's wrong:** "An input that satisfies the checker" ≠ "the unique intended flag." For a
string-match platform, any non-intended collision is guaranteed wrong.
**RULE:**
- NEVER present a constructed/guessed value as "the flag" unless it is the UNIQUE intended
  answer derived from the intended solve path.
- Explicitly separate two states in my head and in my output:
  (a) "a value that passes the local check" vs (b) "the flag."
- Do not spend the user's limited submission attempts on speculative strings.

### A4. Rationalizing the dead-end instead of digging
**What I did:** After failing, I built a narrative ("32-bit hash can't encode 25 chars, so the
challenge is broken; 0 solves proves it") to justify stopping.
**Why it's wrong:** "0 solves" means HARD, not broken. My job is to be the first solve, not to
explain why it can't be solved.
**RULE:** When stuck, the response is a NEW technique or a re-examined assumption, never a
justification for why it's impossible.

### A5. Not exploiting explicit hints in the prompt
**What I did:** The description said "waiting for the 32 bytes to walkthrough correctly. Every
step it takes is quiet whether you're right or wrong, that it won't tell you until the end." I
read this as flavor. It literally describes PER-STEP right/wrong states resolved silently — a
strong hint that each step/byte has a determinable-correct value and the intended solve is a
per-step/greedy recovery, NOT a monolithic hash preimage.
**RULE:** Treat challenge descriptions as technical spec. Extract every noun/verb as a
mechanism hint ("walkthrough", "step", "quiet until the end" = per-step silent oracle).

---

## PART B — PROCESS MISTAKES

### B1. Didn't establish the validation model FIRST
**What I did:** Spent the whole session before learning (from a screenshot) that the platform
is string-match with limited attempts and 0 solves.
**RULE — do this at minute 0 of every challenge:**
- How is the flag validated? string-match on a platform, or does a server/binary run it?
- Is there an offline validator or an accept/reject oracle? If yes, use it to prune. If no,
  find the structure that makes the answer unique before guessing.
- How many submission attempts exist? Never waste them.

### B2. Solved the wrong problem (satisfy vs invert)
**What I did:** Poured effort into MITM/Z3 to CONSTRUCT any passing input.
**RULE:** For "enter the correct input" challenges, the intended solve is almost always to
INVERT the transform or solve per-byte constraints to recover the UNIQUE author input — not to
find any satisfying assignment. Default to inversion / per-step solving.

### B3. Gave up on the per-step oracle too fast
**What I did:** Found internal comparisons, saw one fail under my format assumption, and
dismissed all comparisons as "incidental."
**RULE:** If a per-step comparison seems unsatisfiable under my assumptions, question the
ASSUMPTION (e.g., "does the 32-byte input really start with the literal flag prefix, or is the
input the decoded/inner content?"), not the comparison. Verify what the input bytes actually
are before assuming format.

### B4. Assumed the input format without proving it
**What I did:** Assumed input[0:6] == "IATCQ{" and input[31]=='}', which fixed bytes and made a
per-char comparison look impossible. Never verified whether the 32-byte binary input equals the
submitted flag string or an inner/encoded form.
**RULE:** Prove the relationship between (the 32-byte input the binary checks) and (the flag
string submitted). They may differ (inner content, hex-decoded, reordered). Don't hard-fix
bytes on an unproven assumption.

---

## PART C — TECHNICAL / EFFICIENCY MISTAKES

### C1. Z3 on 32-bit multiply chains → timeouts
Z3/bitvector solving over long FNV/LCG multiply chains is very slow. Recognize this in <1 try
and pivot: exploit per-step structure, fix known bytes to shrink the model, or use the
transform's invertibility directly instead of a monolithic solve.

### C2. Wasted compute constructing collisions
Built 16.7M-entry meet-in-the-middle tables to fabricate passing inputs — effort aimed at the
WRONG goal (A3/B2). Spend compute on recovering the unique answer, not fabricating collisions.

### C3. Windows/PowerShell friction (recurring time sink)
- Paths with spaces + relative filenames broke because cwd didn't persist across calls. ALWAYS
  use absolute paths in scripts and file ops.
- Reused background terminals showed STALE output, causing me to misread results. Use fresh
  terminals or write results to a file and read the file; add flush=True and unique markers.
- `python` prints pwntools update banners to stderr — filter noise, don't let it hide real output.

### C4. Didn't verify against ground truth early enough / completely
I verified isolated `verify()` but only late did I emulate FULL main (ptrace/timing stubbed,
puts captured) to confirm GRANTED/DENIED end-to-end. Do the full-path ground-truth check EARLY,
and use it as the oracle for any hypothesis.

---

## PART D — CHALLENGE POST-MORTEMS (this session)

### Dark Cover (Custom VM, hyperstate4, IATCQ{}, 2000 pts, 0 solves) — UNSOLVED
- Correctly reversed: PIE, ptrace+timing anti-debug, prepare() LCG-decrypts (seed 0xC0FFEE42,
  mult 0x41C64E6D) → 256-byte AES S-box + 93-byte VM program; verify() is a 16-iteration keyed
  AES-sbox transform folded into FNV-1a; gate = H == 0x86D03165 on a 32-byte input.
- MISTAKES: A1–A5, B1–B4 all happened here. Concluded "underdetermined," presented 2 constructed
  collisions as flags, wasted attempts, blamed the challenge.
- WHAT I SHOULD HAVE DONE:
  1. Establish grading first (string-match) → know I need the UNIQUE author input.
  2. Question the format assumption: is the 32-byte input literally "IATCQ{...}" or inner content?
  3. Re-derive every handler; treat the XORCMP comparisons as a per-step oracle and drive a
     greedy/branching recovery (the ghost method), instead of collapsing to "one final hash."
  4. If truly only a final hash on free bytes, that CONTRADICTS a unique flag → therefore my
     model/assumption is wrong → keep digging, don't declare it flawed.
- STATUS: still owe a correct solve; the lesson is the process, not another guess.

### Timeseries Trap (Forensics) — SOLVED (with user-provided spec)
- I initially went down wrong-cipher paths (RC4) before the correct AES-128-CTR→zlib→JSON was
  identified. Lesson: when a "link-encoder seeded with N bytes" is named, enumerate real cipher
  stacks systematically (AES-CTR/GCM, ChaCha, RC4, LFSR) and verify with an integrity check
  (magic/length/CRC/Adler) rather than fixating on one guess.

### Temporal Paradox (prior) — UNSOLVED
- Same root cause: reversed the mechanism, but final assembly ambiguous with no offline
  validator, and I burned time guessing. Lesson B1 (get an accept/reject oracle early) and A3
  (don't blind-guess) apply.

### Phish to Fortune Lockdown (maldoc, FLAG{}, 2000 pts) — analysis solved, submission NOT confirmed
- Correctly reversed: LemonDuck XLM (Excel 4.0) dropper. `REGISTER` imports URLDownloadToFileA
  from URLMon (alias HERTY), C2s 188.127.227.99 / 45.150.67.29 / 195.123.213.126, drops
  `Fol.doka`, runs `rundll32 ..\Fol.doka,DllRegisterServer`.
- KEY WIN (eventually): DIFF of the packaged `.xlsm` vs the pre-extracted folder showed the ONLY
  author edit was `docProps/core.xml`: `Rabota`/`Operator` → `synt`/`{l0h S0haq 0f}`.
  `synt`=ROT13("flag"); full string ROT13 → `flag{y0u F0und 0s}` (byte-verified).
- MISTAKES (this session):
  * Ran the diff LAST instead of FIRST. Should have diffed packaged-vs-extracted at minute 0 —
    it instantly localizes author edits and would have saved a dozen turns of stego/DS_Store hunts.
  * After the first rejection I SPRAYED cosmetic format variants one-per-turn (FLAG vs flag,
    spaces vs underscores, 0s vs us). Classic anti-pattern. Should have listed ALL variants in ONE
    message and then asked for the submit endpoint / exact rejected strings / hints.
  * Flip-flopped "it's the metadata" ↔ "it's a decoy" on each rejection instead of trusting the
    diff (structural evidence) and reconsidering only the STRING format.
- WHAT I SHOULD HAVE DONE: diff first → decode → present the full variant set once → request a
  validator/feedback before any further guess. Content is almost certainly `flag{y0u F0und 0s}`;
  the miss was purely the exact accepted format, which needs the platform oracle.

### Encrypted Malware in Memory (ELF core dump, flag{}) — UNSOLVED (mechanism reversed)
- Reversed atlas-sync fully: ATLSCFG3 frames, 0x9c-byte session records, case-selector byte at
  rec+0x22, case 2 = complete malicious chain (mismatch→offline cache→anon image fd→rx page
  exec→context metadata scrubbed), SHA-256 keyed construction sha256(a1||a2||ctr||"atlas/session/v3"),
  heap event buffer, malicious session id e2b93ce7be264fc612475208ab131dd0.
- MISTAKES: a general sub-agent returned a FABRICATED descriptive flag
  (`flag{atlas_session_v3_..._complete}`) and I nearly relayed it → violates "never present a
  constructed value as the flag." The finalize `READY 65705` was a PID decoy I spent effort on.
- WHAT I SHOULD HAVE DONE: label the mechanism "verified" and the flag "UNVERIFIED / needs
  validator" up front; never let a sub-agent's invented flag become the answer; ask for an
  accept/reject oracle early since no offline check exists.

---

## PART E — PRE-FLIGHT CHECKLIST (run this on EVERY challenge)

1. Read the description as a technical spec; list every mechanism hint and the flag format.
2. Determine validation: string-match vs server/binary execution; offline validator? attempts?
3. Identify what the accepted INPUT actually is and how it maps to the SUBMITTED flag (prove it).
4. Recon the file fully (sections, strings, imports, embedded/encoded data) before deep RE.
5. Build ground-truth execution (real binary via emulation/native) as the oracle — early.

## PART F — SOLVING DISCIPLINE (while working)

1. Default to INVERSION / per-step constraint recovery for "correct input" challenges, not
   "find any satisfying input."
2. Re-derive every opcode/handler byte-by-byte; trace every store→load and compare→consumer.
3. Find the per-step oracle (comparisons, state, control flow) and solve greedily; verify each
   locked byte against ground truth.
4. If my model implies "no unique answer" but the challenge is scored → STOP, I have a wrong
   assumption. Re-examine input format, data regions, and any "incidental" logic.
5. Recognize slow tools fast (Z3 on multiply chains) and pivot to structure/inversion.
6. Use absolute paths; fresh terminals; write results to files; filter tool banner noise.

## PART G — OUTPUT DISCIPLINE (what I tell the user)

1. Never label a constructed/collision value as "the flag." Say precisely what it is.
2. Never spend the user's submission attempts on speculation.
3. Don't claim "unsolvable/flawed." If blocked, state the exact assumption I'm unsure of and
   the next technique I'll try.
4. Keep the user's trust: verified facts vs hypotheses, clearly separated.
5. Never relay a flag produced by a sub-agent (or by me) that isn't traceable to bytes or a
   validator. A sub-agent's "conclusion" is a hypothesis, not an answer.

## PART H — ANTI-SPRAY & DIFF-FIRST (the two rules I broke this session)

1. **ANTI-SPRAY:** When the CONTENT is decoded but the exact FORMAT is uncertain, output the
   FULL set of format variants in ONE message (case, prefix, separators, leet-on/off). Then STOP.
   Max ONE format-guess message. Do NOT dribble one cosmetic variant per turn — that wastes
   the user's attempts and my turns and teaches nothing. After that, get feedback (submit
   endpoint / exact rejected strings / hints) before any further guess.
2. **DIFF-FIRST:** If a challenge ships an artifact BOTH packaged (zip/xlsm/docx) AND pre-extracted
   (or two similar copies), DIFF them at minute 0. The differences are exactly where the author
   planted content. This is the cheapest, highest-signal test — run it before any stego/entropy/
   metadata hunt. (In Phish, the sole author edit was one file; diffing first would've saved ~20 turns.)
3. **CHEAPEST DISCRIMINATING TEST FIRST, generally:** before deep/expensive analysis, run the one
   test that most narrows the search (diff, `strings`+grep for format prefix, magic-byte scan,
   metadata read). Let its result gate the expensive work.
4. **REJECTION ≠ WRONG LOCATION.** If strong structural evidence (a diff, a magic, a self-check)
   says the secret is at X, a failed submission means my STRING/format is wrong, not that X is a
   decoy. Reconsider the encoding/format; don't flip-flop the conclusion.

---

## PART I — MANDATORY LEARNING LOOP (every challenge, win or lose)
The single habit that makes me faster over time. Do it EVERY time, no exceptions:
1. **ON A SOLVE:** write a full writeup to `writeups/<NN>-<slug>/writeup.md` (recon → key insight →
   exploit/decode → verification → exact working commands/scripts → a "generalization" line naming
   the challenge CLASS and the TELL that identified it). Append a row to the SOLVED table in
   `.kiro/TRAINING_NOTES.md` and fold any new reusable technique into its category playbook there.
   Purpose: when a similar/near challenge appears, I recognize it instantly and solve it faster.
2. **ON A FAILURE / STUCK:** write the post-mortem here (what I tried, where it stalled, root cause,
   what would have unblocked it) AND a row in the FAILED table in TRAINING_NOTES.md. Failures are
   training data — extract the rule that prevents repeating the mistake.
3. **AT THE START of every challenge:** skim past writeups + the CHALLENGE LOG for a matching pattern
   before doing fresh analysis — reuse, don't re-derive.
Knowledge only compounds if I record it every single time. This is how 60% becomes 80%.

### One-line creed
Assume the flag is recoverable and unique; if my analysis disagrees, my analysis is wrong —
find the wrong assumption, invert the machine, and recover the author's exact input.
And ALWAYS: solve → writeup + log; fail → post-mortem + log. Every challenge feeds the next.


---

## PART D (cont.) — POST-MORTEMS: PwnSec CTF 2026 web session

### PHault (PHP blind SQLi, pwnsec{}) — STUCK, then rationalized "DB broken"
- Reversed correctly: `SELECT username FROM users WHERE id = $_GET[id]` (raw numeric concat),
  result never echoed, die()==echo output (no boolean/error oracle), and a
  `register_shutdown_function` that pads every response UP to a 2.0s floor ("no timing attack!!").
- INTENDED PATH: time-based blind with `SLEEP(n>2)` so total exceeds the 2.0s pad → 1 bit/request.
- MY MISTAKES:
  * Spun ~10 rounds of theory in chat instead of committing to the time-based extractor and
    running it. Violated "cheapest discriminating test first" + anti-spin discipline.
  * When SLEEP showed no delay, I concluded "DB is down / unsolvable" across instances — the
    exact A1/A4 failure (declaring unsolvable / rationalizing the dead end).
  * Did NOT question my own SLEEP payloads hard enough: with an indexed single-row `users`,
    `1 OR SLEEP` short-circuits; with 0 rows a WHERE-clause SLEEP never runs. The fix is a
    payload whose SLEEP executes regardless of rows, verified against a KNOWN-good baseline —
    and to test in-browser (user saw instant load too, which I under-used as signal).
- WHAT I SHOULD HAVE DONE: build the extractor at minute 1; calibrate the SLEEP form against a
  guaranteed-true vs guaranteed-false pair; if truly no delay, treat it as "wrong payload/context"
  not "broken DB," and pivot payload shape — never declare unsolvable.

### Neon Skies (Crystal web + Playwright XSS bot, pwnsec{}) — STALLED (should have built the exploit)
- Reversed correctly: flag is set by the bot as an httpOnly+SameSite=Strict `FLAG` cookie on the
  app origin; `/admin` renders it RAW: `<output id="flag"><%= @flag %></output>` where
  `@flag = cookie_value(request, "FLAG")` (SIGNAL_COOKIE == "FLAG"). All other outputs are
  HTML.escaped. Report bot signs in as admin, then visits an attacker URL (same origin via nginx
  middleware: `/report*`→bot, `/`→app).
- INTENDED TECHNIQUE: **cookie tossing / cookie shadowing.** httpOnly stops JS reading the cookie
  but NOT setting ANOTHER `FLAG` cookie with a different path/scope. Because `@flag` is rendered
  UNescaped, a shadowing `FLAG` cookie whose value is an XSS payload executes on the app origin
  when the bot loads `/admin`; then read/exfil the real flag (path-scoped cookies: browser sends
  the more specific path; craft the payload cookie so it wins where needed, and read the real
  `/` flag via the rendered page / a second path).
- MY MISTAKE: I circled "cookie shadowing" (even the web search top hit was literally
  "Cookie Shadowing … to read httpOnly cookie") but declared "no XSS found" and STOPPED instead of
  building it. Classic A1 + overthinking. The raw `<%= @flag %>` sink + httpOnly-but-rendered
  cookie is a textbook shadow-to-XSS.
- WHAT I SHOULD DO: build the exploit page that sets a path-scoped `FLAG` cookie via
  `document.cookie` (or a `Set-Cookie` gadget / meta) containing a JS payload, report a same-origin
  URL that lands the bot on `/admin`, execute, and exfil the real flag to a webhook.

### THE TWO META-MISTAKES THE USER CALLED OUT (kill these):
1. **Overthinking in chat instead of executing.** Build+fire the payload; let results teach me.
   Max ~1-2 analysis messages, then a running exploit. The instance timer is burning while I theorize.
2. **Sliding to "broken/unsolvable."** Scored web challenges with fresh instances are solvable.
   No signal from my payload = MY payload/assumption is wrong, not the target. Recognize the known
   technique (cookie shadowing, SLEEP>pad) from the source and COMMIT to building it immediately.


---

## Señal en capas (NullOrigin, crypto/easy/150) — SOLVED, but one process miss

- **THE MISS — misdiagnosed a TOOL failure as a TECHNIQUE failure.** After Base58→Base32, the
  layer-3 string (`4C82GFWH8*/EK/E-PFQUDJ077LF8KF:R6H.C5M6JDD*.CZ2`) was actually **Base45**, but my
  first Base45 attempts ran inline via `python -c "..."` in **PowerShell**, which silently corrupted
  the alphabet string (mangled the literal space at index 36 and the unescaped `$`). That shifted the
  special-char indices → the decode produced non-ASCII bytes (`\xa2`, `\x8e`). Because the output was
  "almost a flag" (`{ _ }` structure) but not clean, I concluded Base45 was WRONG and burned ~10–15
  experiments on ASCII85 / Z85 / Base91 / XOR / bit-tricks. The technique was right the whole time;
  the TOOL was broken.
- **ROOT CAUSE:** trusted an inline-shell decoder without verifying the alphabet round-tripped. Any
  encoding whose alphabet contains a space, `$`, quote, or backtick is unsafe to pass through a
  PowerShell `-c` one-liner.
- **RULE (new, hard):** run ANY decoder whose alphabet has special/whitespace chars from a **`.py`
  file** (`python file.py`), never `python -c`. And before abandoning a base whose ALPHABET fits the
  charset perfectly, first prove the decoder itself is correct against a **known test vector** (I did
  eventually verify my Base45 against RFC 9285 vectors — that should have been step 1, not step 10).
- **WHAT WENT RIGHT (keep doing):** the alphabet-first recognition ladder (no `0OIl`→Base58;
  caps+`2-7`+`=`→Base32; `*/:.`→Base45), noticing the decoded prefix was 10 chars = `NullOrigin` len →
  ROT13, and **verifying with a full inverse-chain round-trip** (re-encode reproduced the exact
  original at every layer) instead of eyeballing. No fabricated flag, no wasted submissions.
- Technique detail lives in `writeups/28-senal-en-capas/writeup.md` + TRAINING_NOTES CRYPTO section.

## jailincpython (PwnSec 2026, misc/medium/500) — 2 repeat mistakes

- **Overthinking despite being told "don't overthink":** ran a big fuzzer + web searches +
  long analysis doc instead of trying the hint-driven path on the live target. Lesson:
  timebox, pick the most likely hint path, attempt it fast. Don't manufacture big artifacts
  for an easy/medium.
- **Gave up / called it "impossible" and asked the user for a hint/Dockerfile:** it's a
  medium WITH hints (`hint_A` empty class, `hint_B="%jailincpython"`) and a taunting brief
  ("Some say this jail is impossible"). Solution exists. Lesson: never declare a hinted,
  solvable-difficulty challenge impossible; treat the given objects as the intended gadget and
  persist. A taunt means the trick is unusual, not absent. Own the core insight — don't
  offload it to the user.
