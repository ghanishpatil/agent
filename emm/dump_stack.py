#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
with open(CORE,"rb") as f: core=f.read()
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
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None
def hd(va,ln):
    b=core_va(va,ln)
    if b is None: print("  NOTMAPPED",hex(va)); return
    for i in range(0,len(b),16):
        c=b[i:i+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in c)
        print(f"  0x{va+i:x}: {c.hex()}  {asc}")
print("=== worker stack frame 0x7ffc6d236b00 .. 0x7ffc6d236e00 ===")
hd(0x7ffc6d236b00,0x300)
