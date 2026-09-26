#!/usr/bin/env python3
import struct, re
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
core=read(CORE)

# whole-file search regardless of segment
print("=== whole-core token search ===")
# long hex tokens
for m in re.finditer(rb"[0-9a-fA-F]{24,80}", core):
    s=m.group()
    # skip if inside obviously-code; print with file offset
    print(f"  hex @0x{m.start():x} len={len(s)}: {s.decode()}")
print("\n=== base64-ish tokens (len>=20) ===")
for m in re.finditer(rb"[A-Za-z0-9+/]{20,120}={0,2}", core):
    s=m.group()
    if len(set(s))<8: continue
    print(f"  b64 @0x{m.start():x} len={len(s)}: {s.decode()}")
