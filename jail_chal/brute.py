import re, os, traceback

pattern = re.compile(r'^(?:[^\[\]"\'0-9()]+|\[[^\[\]"\'0-9()]*\])*$')

class hint_A():
    ...
hint_B = "%jailincpython"

# make a local "flag" so we can detect a successful file read / code-exec
FLAG = "FLAG_LOCAL_SENTINEL_12345"
here = os.path.dirname(os.path.abspath(__file__))
flagpath = os.path.join(here, "flagfile")
open(flagpath, "w").write(FLAG)

def allowed(u):
    return (bool(pattern.fullmatch(u)) and u.count('.') <= 2 and u.isascii() and len(u) <= 800)

def run(u):
    if not allowed(u):
        return "FILTERED"
    try:
        return repr(eval(u, {'globals': {}, '__builtins__': {"hint_A":hint_A, "hint_B":hint_B}}, {}))
    except Exception as e:
        return "ERR %s: %s" % (type(e).__name__, e)

candidates = [
    # walrus / assignment probing
    "x := True",
    "[x := True]",
    "{x := True}",
    # comprehension iterate a method (expect not iterable)
    "[x for x in hint_A.__base__.__subclasses__]",
    "{x for x in hint_A.__mro__}",
    "[hint_A.__base__]",
    # unpack a method
    "[*hint_A.__base__.__subclasses__]",
    # dict unpack calling keys()
    "{**hint_A.__dict__}",
    "{**globals}",
    # can we index mro with True/False
    "hint_A.__mro__[True]",
    "hint_A.__mro__[False]",
    # subscription into type dict via built key? need string key without quotes
    # build 'system' etc via %c is separate; here just test getitem on type.__dict__
    "hint_A.__class__.__dict__",
    # str building via %c
    "hint_B[False]%-~-~False",   # "%c" %2 ? nonsense, just testing % parse
    # reaching builtins dict
    "[lambda:True][False].__builtins__",
    "[lambda:True][False].__globals__",
    # lambda default arg evaluated at def-time (no call inside)
    "[lambda x=hint_A.__base__.__subclasses__: x][False]",
    # matmul / operators on class
    "hint_A@hint_A",
    "hint_A|hint_B",
    "-hint_A",
    # format map getitem on eval globals
    "hint_B",
]

for c in candidates:
    print(repr(c), "=>", run(c))

# check if flagfile got read anywhere (it won't unless a payload read it)
