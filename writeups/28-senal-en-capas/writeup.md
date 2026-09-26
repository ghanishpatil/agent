# Señal en capas — NullOrigin CTF (crypto, easy, 150 pts, 44 solves)

**Flag:** `NullOrigin{5y57em_m34ns_3Lv1sh}`
**By:** CYBxM0nk · First blood: Xer0
**Artifact (single string, no files):**
```
n5TTDgmuT1yYA5g4dKUQsFst7uDGxUQoTnZm2SAzZ9t3R8o5vtdFMuYZf9BALRZzEeXkuzbpHHUx7Sv3Br9Ny1qqo7XSomvFy1vGqQLru1y24
```
Flag format: `NullOrigin{}`. Title = "signal in layers" (Spanish) → nested encodings. Pure offline
"peel the onion" — no key, no server, no infra.

## Solve path (decode chain)
Four stacked transformations. Decode in reverse order:

1. **Base58** — the very first tell: the string has **no `0 O I l`** (109 chars, mixed case,
   digits). That absence is the Base58 alphabet signature. Decoding (bignum → bytes) gives:
   ```
   GRBTQMSHIZLUQOBKF5CUWL2FFVIEMUKVIRFDANZXJRDDQS2GHJJDMSBOIM2U2NSKIRCCULSDLIZA====
   ```
2. **Base32** — pure `A–Z` + `2–7` + `====` trailing padding = textbook RFC4648 Base32. Decode:
   ```
   4C82GFWH8*/EK/E-PFQUDJ077LF8KF:R6H.C5M6JDD*.CZ2
   ```
3. **Base45** (RFC 9285) — 47 chars, charset `0–9 A–Z` plus `* / - : .`. All of those specials are
   in the Base45 alphabet `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:` and `len % 3 == 2` (valid
   Base45 grouping). Decode (3 chars → 2 bytes big-endian, final 2 chars → 1 byte):
   ```
   AhyyBevtva{5l57rz_z34af_3Yi1fu}
   ```
   Note the flag-shaped structure: a **10-char prefix** (`AhyyBevtva`), `{ ... }`, and `_`.
   `NullOrigin` is also 10 chars → the letters have just been substituted, so one classical layer
   remains.
4. **ROT13** — per-letter shift is a constant **13** (`A→N, h→u, y→l, …`), digits/symbols untouched:
   ```
   NullOrigin{5y57em_m34ns_3Lv1sh}
   ```
   Leetspeak reads: `system_means_Elvish`.

## Verification (authoritative, offline)
For a pure-encoding challenge with no server, the strongest offline proof is a **full-chain
round-trip**: re-encode the recovered flag `ROT13 → Base45 → Base32 → Base58` and confirm it
reproduces the exact original artifact, layer by layer:
```
re-b45 == layer3   : True   (4C82GFWH8*/EK/E-PFQUDJ077LF8KF:R6H.C5M6JDD*.CZ2)
re-b32 == layer2   : True
re-b58 == ORIGINAL : True
```
All three match → deterministic, not a guess. Also matches the required `NullOrigin{}` format with
coherent leetspeak content.

## Reproduce (Python)
```python
import base64, codecs

s = 'n5TTDgmuT1yYA5g4dKUQsFst7uDGxUQoTnZm2SAzZ9t3R8o5vtdFMuYZf9BALRZzEeXkuzbpHHUx7Sv3Br9Ny1qqo7XSomvFy1vGqQLru1y24'

# 1) Base58 (bignum -> bytes)
A58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
n = 0
for c in s: n = n*58 + A58.index(c)
l1 = n.to_bytes((n.bit_length()+7)//8, 'big')            # base32 text

# 2) Base32
l2 = base64.b32decode(l1.decode())                       # base45 text

# 3) Base45 (RFC 9285)
T45 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'     # NOTE the real space at index 36
def b45decode(x):
    if isinstance(x, bytes): x = x.decode()
    o = bytearray()
    for i in range(0, len(x), 3):
        ch = x[i:i+3]
        if len(ch) == 3:
            v = T45.index(ch[0]) + T45.index(ch[1])*45 + T45.index(ch[2])*2025
            o += bytes([v >> 8, v & 0xff])
        else:
            v = T45.index(ch[0]) + T45.index(ch[1])*45
            o.append(v)
    return bytes(o)
l3 = b45decode(l2).decode()                              # rot13 text

# 4) ROT13
flag = codecs.encode(l3, 'rot_13')
print(flag)   # NullOrigin{5y57em_m34ns_3Lv1sh}
```

## Generalization (the CLASS + the TELL)
- **Class:** *multi-layer encoding puzzle ("stacked bases" + a final classical cipher).* The whole
  challenge is decode → decode → decode → tiny cipher. No math, no key.
- **Order of tells (this is the reusable recognition ladder):**
  1. **No `0 O I l` and mixed alnum** → **Base58** (also: Bitcoin/Solana vibe). Decode as bignum.
  2. **All caps `A–Z2–7` (+ `=` padding)** → **Base32**.
  3. **`A–Z 0–9` plus `* / - : . $ % +` (and maybe space), `len%3 ∈ {0,2}`** → **Base45**
     (RFC 9285). It is the ONLY common base whose alphabet includes `: * .` together. If length is a
     multiple of 5 and alphabet is `!..u` or z85 set → try ASCII85 / Z85 first instead.
  4. **A decoded string that already looks like `PREFIX{...}` but the letters are scrambled while
     digits/underscore/braces are intact** → a **letter-only substitution remains**: try **ROT13**
     first (constant shift 13), then generic Caesar, then Atbash. Confirm by aligning the known
     flag-prefix length against the mystery prefix (both were 10 chars here → strong ROT hint).
- **Fast heuristic:** if a base-decode yields *fully printable ASCII with brace/underscore
  structure but a wrong letter prefix*, DON'T keep base-decoding — the encoding layers are done and
  the last step is a cipher on letters. Compute the per-letter shift against the expected flag
  prefix; a single constant shift = ROT-n.
- **Verification without a server:** re-encode the candidate through the exact inverse chain and
  require it to reproduce the original artifact byte-for-byte at every layer.

## Gotcha that cost time (tool failure, not technique failure)
Running the Base45 alphabet inside an inline `python -c "..."` on **PowerShell** silently corrupted
the alphabet: PowerShell mangled the literal **space** (index 36) and the `$` (needed escaping),
which shifted every special-char index and produced garbage bytes (`\xa2`, `\x8e`, …). The decode
looked "almost right" (`{ _ }` structure) but had non-ASCII bytes, which sent me chasing XOR/base85
dead-ends. **Fix / rule:** for any decoder whose alphabet contains spaces, `$`, quotes, or backticks,
put it in a **`.py` file** and run `python file.py` — never inline via `-c` on PowerShell. The file
version decoded cleanly on the first try.
