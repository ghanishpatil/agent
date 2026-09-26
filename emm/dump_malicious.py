#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
core=read(CORE)
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
def hd(va,ln):
    b=core_va(va,ln)
    for i in range(0,len(b),16):
        chunk=b[i:i+16]
        asc="".join(chr(x) if 32<=x<127 else "." for x in chunk)
        print(f"  0x{va+i:x}: {chunk.hex()}  {asc}")

# malicious session events: ctr 0x73..0x78 at 0x37553d0 .. 0x3755588+0x58
print("=== malicious session records (ctr 0x73-0x78) 0x37553d0..0x37555e0 ===")
hd(0x37553d0,0x260)

print("\n=== finalize output buffer region 0x7ffc6d236c80..0x7ffc6d236d40 ===")
hd(0x7ffc6d236c80,0xc0)
