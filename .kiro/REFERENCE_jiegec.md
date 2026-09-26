# Technique Reference — distilled from jia.je/ctf-writeups (@jiegec / Jiajie Chen)

Attribution: condensed index of techniques from Jiajie Chen's CTF writeups
(https://jia.je/ctf-writeups/). Use as a fast "tell → attack" lookup. For full worked
detail, fetch the specific page. Complements TRAINING_NOTES.md and /opt/refs.

Only the two static pages carry content: `misc/solution.html` (by-technique index) and
`misc/pyjail.html` (pyjail cheatsheet). Other pages render client-side (no static text).

---

## CRYPTO — pick the attack by what's leaked/weak
- **RSA** (decision tree by given values):
  - small n → factor (factordb / sympy.factorint / RsaCtfTool).
  - small e (e=3) + small m → integer e-th root (`gmpy2.iroot`); or e-th root over few blocks.
  - factorable n → factordb, Fermat (p≈q), Pollard p-1, ECM.
  - small d → Wiener's attack / Boneh-Durfee.
  - same m, different e, same n (common modulus) → Bézout: m = c1^a·c2^b.
  - n & c share a factor → gcd(n,c) reveals p.
  - known n, p−q (or p+q) → solve quadratic for p,q.
  - known n,e,phi → derive d; known n,e,d → factor n (via e·d−1).
  - known n, pow(p,-q,q) & pow(q,-p,p) → CRT reconstruction.
  - non-coprime factors / message not coprime → handle gcd carefully.
  - TOOL: `RsaCtfTool` (container) automates most of these; try it first.
- **Discrete log**: BSGS (small); Pohlig-Hellman (smooth order, incl. "without large factors"
  variant); ECDLP; **Smart's attack** (anomalous curve, #E = p → additive transfer, instant).
- **AES**: chosen-plaintext (ECB byte-at-a-time), **padding oracle** (CBC), **XOR attack vs
  AES-CTR & CRC**, **GCM nonce reuse** (recover auth key H → forge). ECB = identical blocks.
- **DES**: weak keys; slide attack.
- **Double cipher** (2×block): meet-in-the-middle.
- **Classical**: Caesar/substitution → quipqiup.
- **Polynomial / lattice**: small coefficients via **LLL**; N-th root to cut unknowns; odd-degree
  coeff tricks.
- **LCG**: recover params from outputs; recover truncated LCG with only LSBs known; general LCG.
- **ECDSA**: reused nonce k (two sigs → private key); partial nonce leakage → lattice/HNP.
- **Python `random`**: MT19937 state recovery from 624 known 32-bit outputs (or from known bits).
- **C `rand()`**: brute the seed.
- **ACD** (approximate common divisor); **MIHNP** (modular-inverse hidden number, lattice);
  **differential cryptanalysis** (two keys differing in one bit); **LWE** (errors from small set).

## FORENSICS
- **Wireshark/pcap**: USB HID keyboard scancodes → keystrokes; TLS key injection (SSLKEYLOG);
  USB SCSI data extraction; NetBIOS → hostname. (tshark in container.)
- **Word**: extract VBA macros (olevba/oletools).
- **Editor history**: `.viminfo` replay.
- **Disk image**: binwalk / sleuthkit.
- **Password-protected archives**: fcrackzip, hashcat, john.
- **Audio**: spectrogram (text drawn in frequencies) — Sonic Visualiser / spectrogram tool.
- **Windows artifacts**: NTUSER.DAT & SYSTEM/SOFTWARE hives (regipy/hivex), `.evtx` (evtx_dump),
  USN journal (USN-Journal-Parser), `.lnk`/AutomaticDestinations jumplists (LECmd/JLECmd),
  RecentDocs, PSReadLine `ConsoleHost_history.txt`, GPO ScheduledTasks.xml, registry key mtimes.
- **Linux**: memory dump via **volatility3**; verify files vs package-manager checksums; recent
  mtime; trigger core dump to grab memory.
- **VNC**: TightVNC stored password extraction (fixed DES key).

## MISC / ENCODINGS
- Image stego → StegSolve (bit planes). Text stego → zero-width chars. Audio → Sonic Visualiser / LSB.
- Odd representations: Minecraft, **Zeckendorf** (Fibonacci), **EBCDIC**.
- Ligature fonts hide text. Timing side channel = blind exec. PDF → decompress `/FlateDecode` via qpdf.

## PWN
- Stack BOF → overwrite ret to `system`/one_gadget; ret2libc; ROP; shellcode on RWX stack.
- Format string → arbitrary read (`%N$s`), arbitrary write (`%n`), overwrite ret/GOT; blind printf.
- OOB read/write → arbitrary R/W; write to `stdin->_IO_buf_base`; **FSOP** (house of apple 2 /
  house of cat) for modern glibc.
- `/proc/self/mem` arbitrary file access. Integer overflow → negative/zero size.
- Jails: Ruby (define method / String#unpack CVE-2018-8778), JS (**JSFuck** 6 chars), shell
  (pager `!/bin/sh`, arithmetic eval), Perl (newline regex bypass, pipe-open), seccomp
  (**io_uring** to dodge syscall filter, `sendmsg` fd passing).

## REVERSE
- Fuzz for input that crashes-on-correct. JS: eval + inspect vars in devtools.
- Android: apktool, dex2jar + JD-GUI. Memory dump: dump in debugger; ltrace library args.
- **Patch conditional jump** to bypass validation. PyInstaller → pyinstxtractor.
- BPF: bpftool dump program/maps; read BPF asm. Side channel: loop-count leaks flag.
- **VM/bytecode**: transpile custom VM bytecode to RISC-V asm to reuse a decompiler.

## WEB
- XSS: inline JS, SSRF-in-JS, HTML injection, PDF.js CVE. GraphQL: schema introspection.
- SSRF: `gopher://` via curl; also open-redirect to reach internal.
- PHP: `php://filter` (base64 source read); >1000 input vars DoS/bypass.
- **Flask/Jinja SSTI**: `{{7*7}}` → leak via `config`/`self`, RCE via
  `{{cycler.__init__.__globals__.os.popen('id').read()}}`; Werkzeug debugger PIN leak.
- SQLi: enumerate unknown tables, UNION SELECT extra data, arbitrary file read.
- JSON query injection (blind string recovery); Mongo `$operator` injection.
- Info leak: robots.txt. **Next.js CVE-2025-29927**: `x-middleware-subrequest` header → auth bypass.
- YAML: 1.1 vs 1.2 (`NO`/`yes` parsed as bool in 1.1). Race conditions (session/lock file).
- Path traversal: leading `/` forces absolute; relative `../`. bcrypt: silently truncates at 72 bytes.
- DNS rebinding. Timing side channel on password compare.

## AI
- Jailbreak → system-prompt leak. KV-cache → recover prompt from cache.

## PYJAIL — escape chains (from pyjail.html)
- **Builtins banned** → subclasses chain:
  `().__class__.__base__.__subclasses__()[i].__init__.__globals__["system"]("sh")` where i =
  index of `os._wrap_close` (find via
  `str(().__class__.__base__.__subclasses__()).split(", ").index("<class 'os._wrap_close'>")`).
  Or BuiltinImporter: `[...][j].load_module("os").system("sh")`.
  With `__import__` avail: `().__reduce_ex__(2)[0].__globals__["__builtins__"]`.
- **No parens** → call via `obj.__class__.__getitem__ = func; obj[arg]`, or decorators
  `@exec\n@input\nclass a:pass`, or `__class_getitem__`.
- **No `=`** → walrus `[a:=1]`, or comprehension `[[a]for[a]in[[1]]]`.
- **No quotes/strings** → `().__doc__[i]` char extraction; `__getattr__=__import__` then `obj.os`.
- **No digits** → `True`=1, `-~x`=x+1, `len(...)`, `()<((),)`=1.
- **No alpha** → Unicode "Mathematical Alphanumeric Symbols"; NFKC fullwidth bypass of filters.
- **Get shell w/o builtins**: `os.system`/`execl`, `pdb.set_trace()`, `code.interact()`,
  `breakpoint()` (via `license._Printer__setup=breakpoint;str(license)`), `subprocess.Popen(['sh'])`.
- **Pickle jails**: STACK_GLOBAL (no newline), BUILD to overwrite Unpickler attrs, namedtuple
  default-arg eval (find_class limited to collections), BINPERSID for calls.
- Length/charcount limits → raise limit on the fly, reuse locals, unicode homoglyphs, hex literals.

---
Fast use: match the challenge's TELL (leaked value, banned chars, file type, header) to a bullet
above, then pull the full worked example from the site or /opt/refs if needed.
