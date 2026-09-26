#!/usr/bin/env python3
import struct,sys
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
with open(BIN,"rb") as f: data=f.read()
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
for va in [0x48310f, 0x483104, 0x48301b, 0x483010]:
    off=va2off(va)
    if off is None: print(hex(va),"unmapped"); continue
    end=data.find(b"\x00",off)
    print(f"0x{va:x}: {data[off:end]!r}")
# dump around 0x483100-0x483140
off=va2off(0x483100)
print("\nregion 0x483100:")
b=data[off:off+0x60]
for i in range(0,len(b),16):
    c=b[i:i+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in c)
    print(f"  0x{0x483100+i:x}: {c.hex()}  {asc}")
