import re, sys

pattern = re.compile(r'^(?:[^\[\]"\'0-9()]+|\[[^\[\]"\'0-9()]*\])*$')

class hint_A():
    ...

hint_B = "%jailincpython"

def allowed(user_input):
    return not (not bool(pattern.fullmatch(user_input))
        or user_input.count('.') > 2
        or not user_input.isascii()
        or len(user_input) > 800)

def run(user_input):
    if not allowed(user_input):
        return "NOPE (filter)"
    try:
        return eval(user_input, {'globals': {}, '__builtins__': {"hint_A":hint_A, "hint_B":hint_B}}, {})
    except Exception as e:
        return "ERR: %s: %s" % (type(e).__name__, e)

if __name__ == "__main__":
    tests = sys.argv[1:]
    if not tests:
        # quick self-probes
        tests = [
            "hint_A",
            "hint_B",
            "globals",
            "hint_A.__base__",
            "hint_A.__base__.__subclasses__",
            "hint_B[False]",
            "hint_B[True]",
            "True+True",
            "[f.__globals__ for f in {lambda:True}]",
            "hint_B.__class__",
        ]
    for t in tests:
        print("IN:", repr(t))
        print("  ALLOWED:", allowed(t), "DOTS:", t.count('.'))
        print("  ->", repr(run(t)))
