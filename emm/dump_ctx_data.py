#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
BIN  = BASE + r"\atlas-sync"
with open(CORE,"rb") as f: core=f.read()
with open(BIN,"rb") as f: bin=f.read()
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
def hd(va,ln,src=None):
    b=(src if src is not None else core_va(va,ln))
    for i in range(0,len(b),16):
        c=b[i:i+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in c)
        print(f"  0x{va+i:x}: {c.hex()}  {asc}")

# ptr stored at 0x4afb68 (r15 buffer) and 0x4afb60 (records ctx)
p_r15=struct.unpack("<Q",core_va(0x4afb68,8))[0]
p_ctx=struct.unpack("<Q",core_va(0x4afb60,8))[0]
print(f"r15 buffer ptr @0x4afb68 = 0x{p_r15:x}")
print(f"records ctx ptr @0x4afb60 = 0x{p_ctx:x}")
if p_r15:
    print("\n=== r15 buffer (context, first 0x60) ===")
    hd(p_r15,0x60)
print("\n=== .bss around 0x4afb40..0x4afc00 ===")
hd(0x4afb40,0xc0)
