import re, builtins, itertools, os

pattern = re.compile(r'^(?:[^\[\]"\'0-9()]+|\[[^\[\]"\'0-9()]*\])*$')
class hint_A():
    ...
hint_B = "%jailincpython"

# hook open to detect any file access from within eval
_reads = []
_orig_open = builtins.open
def _hooked_open(*a, **k):
    _reads.append(a[0] if a else None)
    return _orig_open(*a, **k)

def allowed(u):
    return (bool(pattern.fullmatch(u)) and u.count('.') <= 2 and u.isascii() and len(u) <= 800)

REST_BUILTINS = {"hint_A": hint_A, "hint_B": hint_B}

def run(u):
    if not allowed(u):
        return None, "FILTERED"
    try:
        r = eval(u, {'globals': {}, '__builtins__': REST_BUILTINS}, {})
        return r, None
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)

roots = [
    "hint_A", "hint_B", "globals", "[]", "[True]", "{True}", "True", "None",
    "hint_A.__base__", "hint_A.__class__", "hint_A.__mro__", "hint_A.__dict__",
    "hint_A.__base__.__subclasses__", "hint_B.__class__", "hint_B.__doc__",
    "[lambda:True][False].__globals__", "[lambda:True][False].__builtins__",
]
# wrappers that might trigger an auto-call
wrap = [
    "{{**{r}}}", "[*{r}]", "{{*{r}}}", "{{x for x in {r}}}", "[x for x in {r}]",
    "{r}%True", "{r}%hint_A", "hint_B%{r}", "{r}|hint_A", "{r}@hint_A",
    "~{r}", "-{r}", "+{r}", "{r}[True]", "{r}[False]", "{r}[hint_A]",
    "hint_A in {r}", "{r}<hint_A", "not {r}", "{r}+hint_B",
    "[y for x in {r} for y in x]",
]

builtins.open = _hooked_open
hits = []
seen = 0
try:
    for r in roots:
        for w in wrap:
            expr = w.format(r=r)
            _reads.clear()
            res, err = run(expr)
            seen += 1
            interesting = False
            if _reads:
                interesting = True
            if isinstance(res, (list, set, tuple)) and len(res) > 5:
                interesting = True
            if interesting:
                hits.append((expr, type(res).__name__ if res is not None else err,
                             list(_reads), (len(res) if hasattr(res,'__len__') else None)))
finally:
    builtins.open = _orig_open

print("tested:", seen)
print("file reads triggered anywhere:", any(h[2] for h in hits))
for expr, kind, reads, ln in hits[:40]:
    print("HIT:", repr(expr), "->", kind, "reads=", reads, "len=", ln)
if not hits:
    print("No interesting hits (no file reads, no large collections).")
