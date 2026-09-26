#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
with open(BIN,"rb") as f: data=f.read()
# section map
e_shoff=struct.unpack_from("<Q",data,40)[0]; e_shentsize=struct.unpack_from("<H",data,58)[0]; e_shnum=struct.unpack_from("<H",data,60)[0]
SEC=[]
for i in range(e_shnum):
    o=e_shoff+i*e_shentsize
    _,_,_,a,off,sz,_,_,_,_=struct.unpack_from("<IIQQQQIIQQ",data,o)
    if a and sz: SEC.append((a,off,sz))
def va2off(va):
    for a,off,sz in SEC:
        if a<=va<a+sz: return off+(va-a)
    return None
def dump(va,ln,label):
    print(f"\n=== {label} 0x{va:x} len 0x{ln:x} ===")
    off=va2off(va); b=data[off:off+ln]
    for i in range(0,len(b),16):
        c=b[i:i+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in c)
        print(f"  0x{va+i:x}: {c.hex()}  {asc}")
dump(0x485200,0x300,"rodata IV/K/consts")
