#!/usr/bin/env python3
import struct, hashlib
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
core=read(CORE)

# malicious session 16-byte id
sid = bytes.fromhex("e2b93ce7be264fc612475208ab131dd0")
# .bss key
key = bytes.fromhex("ced85adfd47e88a7de72f8a153d3ee7847ccf32e95b4d88745d75cd504943b5c")
ctx = b"atlas/session/v3"
node = b"ops-node-17"

print("sid       :", sid.hex())
print("sid ascii :", "".join(chr(b) if 32<=b<127 else '.' for b in sid))
print("key       :", key.hex())

# try XOR sid with first 16 of key
x = bytes(a^b for a,b in zip(sid,key))
print("sid^key   :", x.hex(), "".join(chr(b) if 32<=b<127 else '.' for b in x))

# SHA256(sid), SHA256(sid||ctx), SHA256(key||sid), etc -> see if hex prefix forms readable
for label,data in [
    ("sha(sid)", sid),
    ("sha(sid||ctx)", sid+ctx),
    ("sha(ctx||sid)", ctx+sid),
    ("sha(key||sid)", key+sid),
    ("sha(sid||key)", sid+key),
    ("sha(node||sid)", node+sid),
    ("sha(key||sid||ctx)", key+sid+ctx),
]:
    h=hashlib.sha256(data).hexdigest()
    print(f"{label:22} sha256={h}")

# The 65705 - what is it? maybe a truncated node id or the snprintf of a number
# "65705" could be part of something. print as int
print("65705 dec  =", 65705, "hex=", hex(65705))

# maybe the case result is key XOR sid-derived keystream giving flag{...}
# Let's just print candidate flag forms
print("\nflag candidates:")
print("flag{"+sid.hex()+"}")
print("flag{"+x.hex()+"}")
