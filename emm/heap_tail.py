#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
core=open(CORE,'rb').read()
def core_va(va,ln):
    ph=struct.unpack_from("<Q",core,32)[0]; n=struct.unpack_from("<H",core,56)[0]; ent=struct.unpack_from("<H",core,54)[0]
    for i in range(n):
        o=ph+i*ent; t=struct.unpack_from("<I",core,o)[0]
        off,v,pa,fsz=struct.unpack_from("<QQQQ",core,o+8)
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None
# last fragment ~0x376ccf0+... ; heap ends 0x3773000. dump 0x376d000-0x3773000
def hd(va,ln):
    b=core_va(va,ln)
    if b is None: print("  none",hex(va)); return
    prev=None; rep=False
    for i in range(0,len(b),16):
        c=b[i:i+16]
        if c==prev:
            if not rep: print("  *"); rep=True
            continue
        rep=False; prev=c
        asc="".join(chr(x) if 32<=x<127 else "." for x in c)
        print(f"  0x{va+i:x}: {c.hex()}  {asc}")
print("=== heap tail 0x376d000 - 0x3773000 ===")
hd(0x376d000,0x6000)
