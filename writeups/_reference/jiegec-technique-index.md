# CTF Technique Index (by solution type)

> Source: **CTF Writeups by @jiegec (Jiajie Chen)** — https://jia.je/ctf-writeups/misc/solution.html
> Paraphrased/condensed for offline reference and quick pattern-matching. Full writeups + code are
> on the source site. Content was rephrased for compliance with licensing restrictions.
> USE THIS AT THE START of a challenge: match the challenge's symptoms → the named attack below →
> then look up the concrete method (here, in TRAINING_NOTES.md, or the source site).

---

## AI
- **Jailbreak / system-prompt leak** — coax the model to reveal its hidden system prompt.
- **KV-cache prompt recovery** — reconstruct the original prompt from a leaked KV cache.

## CRYPTO
- **RSA** — attack paths by what's leaked/weak:
  - small `n` → factor it (factordb, sympy).
  - small `e` (e.g. 3) → integer/`e`-th root when message unpadded, or Håstad broadcast.
  - factorable `n` → factordb / Fermat (close primes) / Pollard.
  - small `d` → Wiener / Boneh-Durfee.
  - same `m`, same `n`, different `e` (common modulus) → Bézout combine.
  - `n` shares a common factor with another modulus → gcd to split.
  - known `n`, `p−q` → solve quadratic for p,q.
  - known `n,e,phi⁻¹·d mod n` / known `n,e,d` → derive/factor.
  - known `n, pow(p,-q,q), pow(q,-p,p)` → CRT-style recovery.
  - non-coprime factors in message → adjust recovery.
- **Discrete log** — BSGS; Pohlig-Hellman (smooth order); PH even without large factors; ECDLP;
  **Smart's attack** (anomalous curves, trace 1).
- **AES** — chosen-plaintext (ECB byte-at-a-time); **padding oracle** (CBC); **GCM nonce reuse**
  (recover auth key H); **CTR + CRC XOR** malleability.
- **DES** — weak keys; slide attack.
- **Double block cipher (2DES-style)** — meet-in-the-middle.
- **Caesar / substitution** — quipqiup for automatic solve.
- **Polynomial / lattice (LLL)** — find small coefficients via LLL; n-th root to cut unknowns;
  recover odd-degree coefficients.
- **LCG** — recover parameters from outputs; recover truncated LCG with known LSBs; general LCG types.
- **ECDSA** — reused nonce k (recover priv key); partial nonce leakage (lattice).
- **Python `random` (MT19937)** — reconstruct state from 624 known outputs / from known bits.
- **C `rand()`** — brute the seed.
- **Approximate Common Divisor (ACD)**, **Modular Inverse Hidden Number Problem (MIHNP)** — lattice algos.
- **Differential cryptanalysis** — recover key using two keys differing in one bit.
- **Learning With Errors (LWE)** — exploit small error sampling.

## FORENSICS
- **Wireshark/pcap** — USB keyboard HID → keystrokes; TLS key injection (decrypt with keylog);
  USB SCSI data extraction; NetBIOS hostname extraction.
- **MS Word** — extract/analyze VBA macros.
- **Editor history** — replay `.viminfo`.
- **Disk image** — binwalk carve.
- **Password-protected archives** — fcrackzip / hashcat (zip2john etc.).
- **Audio** — spectrogram visualizer.
- **Shell** — find files by date/time.
- **Windows artifacts** — NTUSER.DAT (MiTeC WRR); `.evtx` (evtx_dump); SYSTEM/SOFTWARE hives
  (reged/hivexregedit); NTFS USN journal (USN-Journal-Parser); registry key mtimes (regipy);
  recent files (`Recent\*.lnk` via lnkinfo/LECmd; AutomaticDestinations via JLECmd; RecentDocs);
  PowerShell history (`ConsoleHost_history.txt`); scheduled tasks XML in Group Policy History.
- **Linux** — memory dump via **volatility3**; verify files vs package-manager checksums; recent
  mtimes; trigger a **core dump** to dump memory.
- **TightVNC** — extract stored VNC password.

## MISC
- **Image stego** — StegSolve (bit planes).
- **Text stego** — zero-width characters.
- **Audio stego** — Sonic Visualiser; LSB.
- **Unusual encodings** — Minecraft (books/signs), Zeckendorf (Fibonacci) representation, EBCDIC.
- **Font** — ligatures encode hidden text.
- **Side channel** — blind execution via timing.
- **PDF** — decompress `/FlateDecode` with qpdf.
- **DNS** — recon.

## PWN
- **Stack buffer overflow** — overwrite return → `system`; **ROP**; run shellcode on stack.
- **Format string** — blind arbitrary read via `printf`; overwrite return address; random-address write.
- **OOB read/write** — arbitrary read; write to `stdin->_IO_buf_base`; **FSOP** (incl. house of apple 2,
  house of cat).
- **Arbitrary file access** — read memory via `/proc/self/mem`.
- **Integer overflow** — to negative / to zero to bypass checks.
- **Jails**: Ruby (define method / disassemble / memory scan / CVE-2018-8778 unpack under-read);
  JavaScript (JSFuck — any JS with 6 chars); Python (see pyjail cheatsheet); Shell (pager `!/bin/sh`,
  arithmetic eval); Perl (newline to bypass regex, pipe operator for cmd+output).
- **Environment variable** — `KEY==VALUE` confusion.
- **Seccomp jail** — syscalls via io_uring; send fd via sendmsg.

## REVERSE
- **Fuzzing** — crash on correct input reveals it.
- **JavaScript** — evaluate + inspect vars in devtools.
- **Android** — apktool; dex2jar + JD-GUI.
- **Memory dump** — dump in debugger; ltrace to log library-call args.
- **Validation bypass** — patch the conditional jump.
- **PyInstaller** — pyinstxtractor to recover .pyc.
- **BPF** — bpftool dump program+maps; read BPF assembly.
- **Side channel** — use loop count to recover the flag byte-by-byte.
- **VM/bytecode** — convert VM bytecode to RISC-V asm to reuse a decompiler.

## WEB
- **XSS** — inline JS; SSRF from JS; HTML injection; PDF.js vuln.
- **GraphQL** — schema introspection to map hidden queries.
- **CURL/SSRF** — `gopher://` for smuggled requests.
- **PHP** — `php://filter` chains for arbitrary file read; >1000 input vars DoS/bypass.
- **Flask/Jinja** — SSTI to leak data or RCE; Werkzeug debugger PIN leak.
- **SQLi** — enumerate/read unknown tables; arbitrary file read; UNION SELECT for extra data.
- **JSON query injection** — blind recovery of a hidden string.
- **MongoDB** — `$operator` injection (e.g. `$ne`, `$regex`).
- **Info leak** — robots.txt.
- **Next.js** — CVE-2025-29927 middleware auth bypass.
- **YAML** — v1.1 vs v1.2 differences; `NO` parsed as boolean false.
- **Race condition** — cookie/session race; lockfile race (TOCTOU).
- **Path traversal** — leading `/` to force absolute; relative path escapes.
- **bcrypt** — 72-byte truncation collision.
- **DNS** — rebinding attack to bypass host checks.
- **Side channel** — timing on password validation.
