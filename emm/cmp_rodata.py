#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"; CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
data=read(BIN); core=read(CORE)

def parse_phdrs(d):
    e_phoff=struct.unpack_from("<Q",d,32)[0]; e_phnum=struct.unpack_from("<H",d,56)[0]; e_phent=struct.unpack_from("<H",d,54)[0]
    out=[]
    for i in range(e_phnum):
        o=e_phoff+i*e_phent; t=struct.unpack_from("<I",d,o)[0]
        off,va,_,fsz,_,_=struct.unpack_from("<QQQQQQ",d,o+8); out.append((t,off,va,fsz))
    return out
cph=parse_phdrs(core)
def core_va(va,ln):
    for t,off,v,fsz in cph:
        if t==1 and v<=va<v+fsz:
            s=off+(va-v); return core[s:s+ln]
    return None

# binary rodata offset for VA 0x483000 = file 0x83000
print("=== BINARY @0x483000 (0x60) ===")
b=data[0x83000:0x83060]
print(b.hex())
print(repr(b))
print("\n=== CORE @0x483000 (0x60) ===")
c=core_va(0x483000,0x60)
print(c.hex())
print(repr(c))

# Also compare .data region 0x4ae0c0 (binary) vs core
print("\n=== BINARY .data @0x4ae0c0 (0x80) ===")
print(data[0xad0c0:0xad0c0+0x80].hex())
print("=== CORE .data @0x4ae0c0 (0x80) ===")
cc=core_va(0x4ae0c0,0x80)
print(cc.hex() if cc else "NOTMAPPED")

# search binary for 'atlas' 'frame accepted' etc
for needle in [b"frame accepted",b"atlas/session",b"signature verified",b"quarantine",b"flag{",b"session/v3",b"context metadata"]:
    i=data.find(needle)
    print(f"BIN find {needle!r}: {'0x%x'%i if i>=0 else 'NOTFOUND'}")
