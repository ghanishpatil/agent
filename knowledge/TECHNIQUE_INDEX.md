# Technique Index — Tell → Attack → Example

> Derived from every writeup and solution doc in the workspace. Maps a recognizable **tell**
> (what you observe) to the **attack** and the **historical example(s)** that used it, so a new
> challenge can be pattern-matched to prior work instantly. Complements `.kiro/TRAINING_NOTES.md`
> and `.kiro/REFERENCE_jiegec.md` (this one is scoped to *challenges actually solved in this repo*).

---

## WEB

| Tell (what you see) | Attack | Historical examples |
|---------------------|--------|---------------------|
| ping/host input box, "command injection" | shell metachar `;` `\|`; space filter → `${IFS}` | Don't Ping L1/L5 (TDHT), Ultron Diagnostics (CHAKRA) |
| search/template field echoes math | Jinja2 SSTI `{{7*7}}` → `lipsum.__globals__.os.popen` | Status Page (TDHT) |
| `?path=`/`?file=`/image loader | LFI absolute path; source via `php://filter` | Northline Market (TDHT), Online Store (Kaal), Sanctum Archives (CHAKRA) |
| LFI with `../` stripped once | single-pass `str_replace` bypass `.....///`→`../` | Shopping L2/L3 (TDHT) |
| profile/update JSON API returns `role` | mass assignment: add `"role":"admin"` | Switch It Up (TDHT), 7 Gates (CHAKRA) |
| JS-only auth, cookies set client-side | set cookies manually (`role=admin;verified=true`), open `/admin` raw | Admin ERP (CHAKRA) |
| `md5(role)` cookie | cookie forge `admin\|`+md5("admin") | HYDRA Portal (CHAKRA) |
| RS256 JWT + public JWKS endpoint | alg-confusion RS256→HS256 (HMAC key = JWK `n` string); or `alg:none` | CloudNine, Equator Navigation (Kaal) |
| admin-gated server-side URL fetch | SSRF; bypass host blocklist via app's own open-redirect | CloudNine, Webhook Pinger (Kaal) |
| internal YAML config endpoint w/ custom tags | `!env` / `!include` → read secret file | CloudNine |
| "deleted"/draft record | soft-delete bypass `?deleted=true&pass=` → often b64 | Ghost Draft (Vishwa) |
| market/purchase with balance | race/TOCTOU: concurrent buys (asyncio/runspaces) | Flag Market (Vishwa) |
| robots.txt disallow entries | hidden dir → ROT13/Caesar; watch decoys | Server's Secret (CHAKRA) |
| infra API on internal IP (chall-manager/k8s/docker) | unauth GET `/api/v1/challenge` leaks flag | Stolen Schematics (TDHT) |
| deep-merge / `__proto__` in body | prototype pollution `{"__proto__":{"role":"admin"}}` | ProfileHub (ctf7), Spectral_Override |
| user input → BOTH `$("#"+x)` selector AND `eval(\`type_${x}()\`)` | selector∩JS payload: `x:eval(atob(...))` (unknown `:pseudo()` don't throw) | polynomial evaluator (K17) |
| flag delivered as httpOnly cookie but rendered raw on authed page | cookie shadowing / tossing → same-origin XSS → exfil | neon-skies (PwnSec) |
| flag revealed by frontend JS after a "gate" (captcha/timer/game) | gate is a decoy; reproduce the local decode offline | reverse captcha (K17) |
| SQLi, result never echoed, response padded to fixed time | time-based blind with `SLEEP(n) > pad`; calibrate against known true/false | phault (PwnSec) |
| login form | SQLi tautology `' OR '1'='1` | Breach Stark (CHAKRA) |

## CRYPTO / ENCODING (netcat & offline)

| Tell | Attack | Examples |
|------|--------|----------|
| hex ciphertext, "single-byte XOR" | brute 256 keys, pick printable | Wakandan Vault (CHAKRA) |
| letters shifted | Caesar brute 25 / ROT13 / ROT47 (33–126 by 47) / Atbash (self-inverse) | Loki's Cipher, ROT47 Quantum, Mirror Dimension, Admin ERP Caesar-14 (CHAKRA) |
| dot/dash | Morse standard table | Stark Telemetry (CHAKRA), Kavach-X |
| b64 that decodes to b32 alphabet | peel base chain in reverse | S.H.I.E.L.D. Intercept (CHAKRA) |
| "reversed then hex" | hex-decode then reverse | I Am Groot (CHAKRA) |
| signature = `popcount(row & msg)%2` / matrix·vector, no nonce/nonlinear | **linear MAC forgery over GF(2)**: `sign(a⊕b)=sign(a)⊕sign(b)`; query `root⊕user` | cry-pto (K17) |
| Groth16 verifier + leaked `tau`/"ceremony ashes" | forge proof for any public input; A=α₁,B=β₂, solve C; watch scaled generators | impossible (NNS) |
| Playfair / multi-stage substitution | try both orderings; acrostic first-letters | Spartans (Kaal, candidates) |
| RSA broadcast e=3 / nonce reuse | Håstad CRT+cube root; XOR crib drag | Stones RSA (Kaal) |

## REVERSE ENGINEERING

| Tell | Attack | Examples |
|------|--------|----------|
| `L...{`-shaped strings in binary | ROT of flag prefix (e.g. ROT25) | Crackme (Kaal) |
| PyInstaller ELF/EXE | `pyinstxtractor` → search `.pyc` | Greetings (Kaal) |
| XOR + rail-fence layered | invert both stages | Guarded Input (Kaal) |
| custom bytecode VM, stripped | decrypt program (LCG), re-derive every opcode; emulate w/ unicorn | Dark Cover (IATCQ, unsolved) |
| ONNX model handout | hidden data in weight-tensor float LSBs | AIML/ONNX (Kaal, `challenge_final.onnx`) |
| `.wasm`/`.wat` validator | disassemble, trace logic (often red herring) | ProfileHub, validator.wasm |
| APK | apktool/jadx, search strings/firebase | KaalRaj (Kaal) |
| Terraria `.wld` "won't open" | fix magic/pointers, decode tile RLE, render type-122 letters | A Whole New World (K17) |

## PWN

| Tell | Attack | Examples |
|------|--------|----------|
| struct with sibling scalars + loop counter nudged past bound + signed index | index-escape aliasing; reach field *below* array at negative index | big-win (K17) |
| `srand(time)` + one lucky payout leaps threshold; losing ends cleanly | reconnect-brute the RNG (no PRNG modelling) | online-roulette (K17) |
| heap off-by-one size field | clear PREV_INUSE → overlap → tcache poison → `__free_hook`=system | Note Taking (ctf7/Kaal) |
| ships libc.so.6 + ld.so.2 | ret2libc / one_gadget; leak then return | WAF (waf_chal) |
| port-knock sequence | connect ports in order to open service | Sector7 (Kaal) |

## FORENSICS / STEGO

| Tell | Attack | Examples |
|------|--------|----------|
| "no upload/DNS/mail/print but data left" + telemetry feed | covert **timing** channel: `delay=capture_ts−device_ts`, trimodal→bits, byte-aligned magic, key=cal bytes | Timeseries Trap (CTF) |
| image, suspected LSB | R/G/B LSB row-scan → often b64 | Raven, LOVE SANJIVANI |
| WAV | spectrogram (text in freq), RIFX/RIFF fix, LSB, ICMT=zip pass | Infinity Stones, Final Whisper |
| disk image / ISO | 7z extract; FAT32/ISO9660 parse; slack/deleted inodes | Disk Forensics, Ghosts in Disk (Kaal) |
| corrupted QR | threshold + inpaint + morphology | Corrupted QR (Kaal) |
| PDF redaction / protected | remove overlay, OCR, pikepdf | Emails, Cases (Kaal) |
| maldoc (xlsm/docx) | unzip OOXML, XLM macros, **check docProps/core.xml** (`synt`=ROT13("flag")) | Phish to Fortune |
| ext4 image, "secure_delete OFF" | recover dropped SQLite table from freelist | Temporal Paradox (failed) |

## MISC / AI / MULTI-STAGE

| Tell | Attack | Examples |
|------|--------|----------|
| AI chatbot guardian + thematic story | prompt injection using the challenge's OWN language after completing its state machine | Manas-Yantra (CHAKRA) |
| `/begin /trial /vow /heart` oracle | loop trials (PoW nonce) then GET flag; watch time-gates | Love is Complicated (BPCTF) |
| hash-chain seals + PoW witness | verify `sha256(h\|parent\|data)`, mine `00000`, respect cooldown | Ashen Checkpoint |
| pyjail: eval, no `()`/quotes/digits | no-paren call primitives; label-smuggling; unicode/NFKC (see `.kiro/REFERENCE_jiegec.md`) | jailincpython (unsolved) |
| pickle jail bans opcode-in-dis output | omit STOP (`.`) → dis() crashes → REDUCE ban bypassed; `__builtins__` via allowed module | pickle (PwnSec) |
| multi-decode chain (b64+morse+b64+ROT13) | peel layers, then join/reverse/leet | Chakra Story (CHAKRA) |

---

## Cross-cutting meta-rules (from the failure logs)
1. **Read the description as a spec first** — nouns/verbs name the mechanism; note exact flag format.
2. **Establish the grading model at minute 0** (string-match vs server-run; validator; attempts).
3. **Cheapest discriminating test first** (diff packaged-vs-extracted, `strings`+grep prefix, magic, metadata).
4. **Invert to recover the unique intended flag**, don't fabricate a passing collision (Dark Cover lesson).
5. **Prove, don't tune** — self-validating decode (magic + length + checksum) beats a hand-tuned threshold (Timeseries Trap).
6. **The flag NAME is a hint; decoys announce themselves** ("N0TH1NG", "FAKE", "honeypot", "keep_trying").
7. **No offline validator → ask for accept/reject EARLY**; never spray guesses; give all format variants in ONE message (Temporal Paradox / Phish lessons).
8. **Never declare "impossible"** for a hinted, solvable-difficulty challenge; attack the hints harder (jailincpython lesson).
