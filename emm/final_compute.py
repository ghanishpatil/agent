#!/usr/bin/env python3
import struct, hashlib, base64
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
core=open(CORE,"rb").read()
def cva(va,ln):
    ph=struct.unpack_from("<Q",core,32)[0]; n=struct.unpack_from("<H",core,56)[0]; ent=struct.unpack_from("<H",core,54)[0]
    for i in range(n):
        o=ph+i*ent; t=struct.unpack_from("<I",core,o)[0]
        off,v,pa,fsz=struct.unpack_from("<QQQQ",core,o+8)
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None
ctx=b"atlas/session/v3"
S=cva(0x3767ad0,0xb0)

def auth(a1,a2,ctr):
    return hashlib.sha256(a1+a2+ctr.to_bytes(8,"little")+ctx).digest()

# Various plausible authenticated-result computations for malicious session
sid=S[0x10:0x20]
a1_24=S[0x10:0x28]   # 24 bytes: id + timestamp
print("candidates (sha256 bound to context):")
for label,(a1,a2,ctr) in {
  "id24/id16/2":(S[0x10:0x28], sid, 2),
  "0x30..48/id/2":(S[0x30:0x48], sid, 2),
  "0x30..48/0x48..58/2":(S[0x30:0x48], S[0x48:0x58], 2),
}.items():
    print(f"  {label:22}: {auth(a1,a2,ctr).hex()}")

# Print all the strongest flag candidates for the user to try
print("\n==== FLAG CANDIDATES ====")
cands=[
  "flag{"+sid.hex()+"}",
  "flag{e2b93ce7be264fc612475208ab131dd0}",
]
for c in cands: print(c)
