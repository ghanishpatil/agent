import io, pickle, tempfile, os, traceback
from solve import build_payload, RestrictedUnpickler

tf = tempfile.NamedTemporaryFile(mode="w", suffix="ff", delete=False)
tf.write("pwnsec{LOCAL_TEST_OK}\n"); tf.close()
lp = build_payload(tf.name.replace("\\","/"))
print("path:", tf.name)
try:
    r = RestrictedUnpickler(io.BytesIO(lp)).load()
    print("load result:", repr(r))
except Exception:
    traceback.print_exc()

# also inspect what collections.__builtins__ is
import collections
print("type(collections.__builtins__):", type(collections.__builtins__))
print("has open:", ('open' in collections.__builtins__) if isinstance(collections.__builtins__, dict) else hasattr(collections.__builtins__, 'open'))
os.unlink(tf.name)
