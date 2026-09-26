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
def hd(va,ln,skipzero=True):
    b=core_va(va,ln)
    if b is None:
        print(f"  0x{va:x} NOTMAPPED"); return
    for i in range(0,len(b),16):
        chunk=b[i:i+16]
        if skipzero and chunk==b"\x00"*16: continue
        asc="".join(chr(x) if 32<=x<127 else "." for x in chunk)
        print(f"  0x{va+i:x}: {chunk.hex()}  {asc}")

print("=== heap 0x3752930 (r15 buffer, len ~ (2*count+1)*8) 0x300 ===")
hd(0x3752930,0x300)
print("\n=== heap 0x3752c40 (events buffer [rbp-0x248], 0x2c38) first 0x400 ===")
hd(0x3752c40,0x400)
print("\n=== heap 0x376cb20 / 0x376cb30 0x80 ===")
hd(0x376cb20,0x100)
