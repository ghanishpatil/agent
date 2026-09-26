import pickletools, io

raw = open('out.pkl.part','rb').read()
print("file size:", len(raw))
print("first 32 bytes:", raw[:32].hex())
print()
# Dump the pickle opcodes until it (likely) truncates
buf = io.StringIO()
try:
    pickletools.dis(raw, annotate=1, out=buf)
    print(buf.getvalue())
except Exception as e:
    print(buf.getvalue())
    print("\n[dis stopped]:", type(e).__name__, e)
