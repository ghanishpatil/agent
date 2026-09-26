# jailincpython — misc / medium / 500 pts (pwnsec{}) — PwnSec CTF 2026

Status: environment fully reversed + mapped; escape primitive appears absent under the
exposed namespace. Documented for the learning loop.

## The jail (main.py, /app/main.py on remote, Python 3.11+)

```python
pattern = re.compile(r'^(?:[^\[\]"\'0-9()]+|\[[^\[\]"\'0-9()]*\])*$')
class hint_A(): ...
hint_B = "%jailincpython"
user_input = input("~ ")
# reject unless: regex fullmatch AND count('.')<=2 AND isascii() AND len<=800
print(eval(user_input, {'globals': {}, '__builtins__': {"hint_A":hint_A,"hint_B":hint_B}}, {}))
```

Filter forbids, anywhere in input: `(` `)` `"` `'` digits `0-9`; `[` `]` only as balanced
`[...]` with none of those inside; at most 2 `.`; ascii; <=800 chars.

## Confirmed on the live service (a1376d496be7342c.chal.ctf.ae:443 TLS)
- eval globals = `{'globals': {}, '__builtins__': {'hint_A': <class __main__.hint_A>, 'hint_B': '%jailincpython'}}`
- eval builtins = only `hint_A`, `hint_B`. locals = `{}`.
- Tracebacks are echoed to the client (shows /app/main.py, Python 3.11+ caret markers).
- Parens ARE rejected (`hint_B.__len__()` -> "Nope!!"), matching the public source.
- Flag is NOT present anywhere in the reachable namespace.

## What IS possible (no parens)
- Integers without digits: `True`/`False` arithmetic (`True+True` = 2).
- Index with them: `hint_A.__mro__[True]` = object.
- Build arbitrary strings: protocol via `%c`/`%a` formatting + slicing `hint_B` / attr-name
  strings (e.g. `hint_B.__class__.__name__[False]` = 's').
- Reach `object`/`type` (`hint_A.__base__`, `hint_A.__class__`), their `__dict__`s.
- Reach eval-globals via `[lambda:True][False].__globals__` (but it's the restricted one).
- Walrus inside brackets: `[x := True]`. Comprehensions with `{...}`/`[...]`.
- Operators, `{**d}`, `[*it]`, set/dict construction.

## Why it seems unescapable (the wall)
To read `/flag` you must CALL a function (open/read, or reach os via
`object.__subclasses__()`). In a **single eval expression** a call requires either:
1. `()` — banned; or
2. a dunder triggered by an operator on an object whose dunder is dangerous/Python-level.

But every reachable object (class `hint_A`, `object`, `type`, `str`, `dict`, `list`, the
eval-globals dict) has only safe **C** dunders. You cannot create a custom-dunder object
because instantiation needs `()` and there is no `setattr`/assignment in eval (walrus binds
names only, never attributes). No reachable object is a **Python-level function**, so there
is no `__globals__` bridge to the real builtins/os. `__subclasses__` is reachable as a bound
method but cannot be invoked. Empirically verified with a 357-case fuzzer (hooking `open`):
**zero** file reads, no auto-call to anything dangerous.

Therefore: no code-exec, no file read, and the flag is not reachable as data.

## Open question / next step
For a "medium" that is solvable, one of these must be true:
- there is an obscure CPython auto-call primitive not covered here (version-specific), or
- the intended path is an info-leak I haven't found, or
- extra surface exists in the Dockerfile (flag baked into env/namespace, helper, exact
  Python version enabling a specific gadget).

To crack it fast I need: the **Dockerfile** (flag location + exact Python version + any
helper) or an official hint. With the exact version I can target version-specific gadgets.

## Lessons (learning loop)
- Rigorously enumerate the *call primitives*, not just the object graph: in pure `eval`
  with no `()` and no assignment, calling requires a dangerous/Python dunder on a reachable
  object — if none exists and you can't craft one, code-exec is genuinely blocked.
- Confirm the deployed filter == public source empirically (sent a paren payload -> "Nope!!").
- Echoed tracebacks are an info-leak channel worth remembering (here: leaked Python version
  + app path), even when they don't directly yield the flag.
- Build a small live client early (TLS+SNI here) to probe instead of guessing.
