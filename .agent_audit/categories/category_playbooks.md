# Category Playbooks (adaptive, evidence-gated — NOT linear scripts)

Each category lists: **first recon** (cheap, high-info), **useful artifacts**, **common attack
surfaces**, **cheapest discriminating tests**, **common dead ends/decoys**, **verification**,
**specialist tools** (with availability), and **common failure patterns**. The agent must branch on
evidence, not run these top-to-bottom. Technique IDs (`T-###`) reference `knowledge/technique_memory.jsonl`.

---
## WEB
- **First recon:** raw HTML + comments (Invoke-WebRequest), `/robots.txt`, linked JS, `/changelog`, a random path (Django `DEBUG=True` dumps URLconf), `/api/profile`, `/backup/*`, `/.well-known/*`. Establish framework from headers.
- **Useful artifacts:** JS bundles (grep `eval(`, `Function(`, `$("#"+`, `flag`, `TextDecoder`), comments (`<!-- legacy-callback -->`), changelog entries (new feature = new bug).
- **Attack surfaces / techniques:** cmd-injection T-001; SSTI T-002; LFI/traversal T-003; mass-assign T-004; client-side/cookie T-005; JWT confusion T-006; SSRF+redirect T-007; time-blind SQLi T-008; race/TOCTOU T-009; param-type/array poisoning T-010; client-side flag T-011; jQuery∩eval XSS T-012; cookie-shadow XSS T-013; prototype pollution T-014; custom server encoding T-015.
- **Cheapest discriminating tests:** `{{7*7}}`; `;id`/`|id`; `?path=/etc/flag.txt`; add `role=admin`; send field as array; grep JS for a local reveal fn.
- **Dead ends/decoys:** anti-devtools JS (bypass via raw HTTP); HTML-comment decoy flags (names announce them); IMDSv2 via GET-only SSRF; solving a captcha/game gate when the flag is client-side.
- **Verification:** flag appears on the unlocked page / in response; for XSS-bot, exfil arrives at collector.
- **Failure patterns:** 429/timeout misread as "no vuln" (FAIL-005/012); recognizing a technique then not building it (FAIL-006); spraying format variants (FAIL-003).
- **Tools:** requests, Invoke-WebRequest, node+jsdom+jQuery (all native); ffuf/gobuster (container).

---
## CRYPTO
- **First recon:** identify what is leaked (n/e/c, matrix, oracle, cipher name). For netcat: read the prompt keyword.
- **Useful artifacts:** source code (read as spec), key/param files, a `secret` file (may be ROT13/obfuscated).
- **Attack surfaces / techniques:** single-byte XOR T-016; classical ladder T-017; linear MAC forgery T-018; RSA decision tree T-019; Groth16/tau forgery T-020; netcat auto-decode T-030. See `.kiro/REFERENCE_jiegec.md` for the full RSA/DLP/AES/LCG/ECDSA decision tree.
- **Cheapest discriminating tests:** brute 256 XOR keys; try Caesar/ROT13/ROT47/Atbash/base-chain; `sympy.factorint(n)`; prove `sign(a^b)=sign(a)^sign(b)` locally.
- **Dead ends/decoys:** running generic RSA tools on a modulus needing a specific attack; z3 on multiply chains (FAIL-008) → invert instead.
- **Verification:** decrypted bytes contain the flag format; or server accepts a forged tag/proof (self-validating).
- **Failure patterns:** garbage plaintext read as "uncrackable" (it's wrong key/mode/order); trying to recover a matrix instead of exploiting linearity.
- **Tools:** pycryptodome, sympy, z3 (native); gmpy2/RsaCtfTool (container/installable).

---
## REV
- **First recon:** `file`/magic; strings (look for `L...{`-shaped ROT'd flags); imports; section sizes; anti-debug (ptrace/timing).
- **Useful artifacts:** encrypted `.rodata` blobs (often LCG-decrypted at runtime), embedded S-boxes/bytecode.
- **Attack surfaces / techniques:** custom VM reversal T-026; crackme ROT decode; PyInstaller extract; patch conditional jumps (jiegec).
- **Cheapest discriminating tests:** strings+grep flag prefix; decrypt the runtime blob; emulate a slice with unicorn.
- **Dead ends/decoys:** a self-consistent emulator that matches random inputs but doesn't pin the flag (FAIL-010); a 32-bit hash gate over free bytes (collisions ≠ flag, FAIL-001).
- **Verification:** self-validating decode or platform acceptance — never a collision.
- **Failure patterns:** payload gravity (emulate a stripped binary for an easy challenge, FAIL-002); declaring "underdetermined".
- **Tools:** capstone+unicorn (native); gdb+pwndbg/radare2/qemu/angr (container/WSL).

---
## PWN
- **First recon:** `checksec`; source/objdump; map local offsets to array indices; find win()/one_gadget.
- **Useful artifacts:** provided libc.so.6 + ld.so.2 (⇒ ret2libc), SNAPSHOT/int3 stack leaks.
- **Attack surfaces / techniques:** index-escape/local-aliasing T-024; predictable-RNG reconnect T-025; heap off-by-one→tcache (jiegec/Note Taking); format string; ROP/ret2libc.
- **Cheapest discriminating tests:** simulate the vulnerable loop signed-correctly; compute a stake that leaps a threshold; leak layout via SNAPSHOT.
- **Dead ends/decoys:** an "arbitrary write" gated by `addr<=&stackvar` can't reach vars ABOVE it; return-overwrite when a negative index is simpler.
- **Verification:** local `-no-pie` build reaches win() BEFORE remote; remote prints /flag.
- **Failure patterns:** going remote before local proof; ignoring int-overflow limits on stakes.
- **Tools:** pwntools (native-limited, remote I/O ok); gdb/qemu/ROPgadget/one_gadget (container/WSL).

---
## FORENSICS
- **First recon:** `file`/magic; strings; **DIFF packaged vs pre-extracted FIRST** (localizes author edits); inventory small config/log files (they hold the spec).
- **Useful artifacts:** pcap (capture ts vs device ts), disk images, docProps/core.xml, SQLite freelist (deleted rows), .cal/calibration files (key material).
- **Attack surfaces / techniques:** covert timing channel T-021; maldoc metadata T-022; disk carve/recover; PDF redaction removal.
- **Cheapest discriminating tests:** diff; strings+grep prefix; per-entity timing stats; unzip OOXML and read core.xml.
- **Dead ends/decoys:** modelling `val`/payload when the channel is timing (payload gravity); missing-sample run-lengths that match logged timeouts (Timeseries LT-107); loud decoy carriers without a magic anchor.
- **Verification:** magic + balancing length + checksum (Adler/CRC) = bit-perfect; flag inside decrypted JSON.
- **Failure patterns:** cheap test (diff) run late (FAIL-003); over-modelling the loud artifact (FAIL-002).
- **Tools:** PIL/numpy, 7-Zip, oletools, pure-Python pcap parser (native); binwalk/foremost/tshark/sleuthkit/volatility (container).

---
## STEGO
- **First recon:** exiftool/strings; file magic; look for data after IEND / after ZIP EOCD.
- **Useful artifacts:** images (LSB/bitplane), wav (spectrogram/LSB), ICMT comment (zip password).
- **Techniques:** LSB/spectrogram/bitplane T-023.
- **Cheapest discriminating tests:** R/G/B LSB row-scan → base64; render spectrogram.
- **Dead ends/decoys:** uniform LSB across all bytes (not the channel); a decoy flat-gradient image.
- **Verification:** decoded base64 matches flag format.
- **Failure patterns:** reaching for zsteg/steghide (container-only now) instead of native PIL.
- **Tools:** PIL/numpy (native); zsteg/steghide (container).

---
## MISC / JAILS / AI / MULTI-STAGE
- **First recon:** read the brief as a spec; identify the interpreter/jail rules or the state machine.
- **Techniques:** pickle jail (omit STOP) T-027; pyjail no-paren escape T-028; AI prompt-injection state machine T-029; multi-decode chains.
- **Cheapest discriminating tests:** confirm deployed filter == public source (send a probe); take flavor hints literally (Kohli).
- **Dead ends/decoys:** anti-debug UI (decoy); generic jailbreaks (deflected); declaring a hinted jail "impossible" (FAIL-007).
- **Verification:** /flag read, shell obtained, or bot reveals real flag (not comment decoy).
- **Failure patterns:** overthinking when told not to; offloading the core insight to the operator.
- **Tools:** native Python; `.kiro/REFERENCE_jiegec.md` pyjail chains.

---
## CATEGORIES PRESENT BUT THIN IN CORPUS (lower confidence, expand later)
- **OSINT** (Timoplayzz, Budapest, Intel): social/geo/metadata — mostly guides, few confirmed flags.
- **MOBILE** (KaalRaj APK, Greetings): apktool/jadx, hardcoded secrets — reversed but light documentation.
- **CLOUD/IOT/HARDWARE:** essentially absent — treat as knowledge gaps (see architecture_recommendation §gaps).
- **ZK/CRYPTO-advanced** (Groth16): one strong example (T-020); high value, low volume.
