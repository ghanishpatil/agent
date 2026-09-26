#!/usr/bin/env python3
"""Hunt core writable segments for entropy blobs + dump bss/heap; find refs to status strings & bss."""
import struct, math
from capstone import *
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

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
def core_off(va):
    for t,off,v,fsz in cph:
        if t==1 and v<=va<v+fsz:
            return off+(va-v)
    return None

def entropy(b):
    if not b: return 0
    from collections import Counter
    c=Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

# writable/runtime segments to hunt (skip the code image ones 0x400000-0x4b6000 rodata/text)
# .data starts 0x4ae0c0, bss 0x4afae0 .. 0x4b6000; heap 0x3751000; stacks
segs_interest=[(0x4ae000,0x4b6000,"data/bss"),(0x3751000,0x3773000,"heap"),
               (0x7ffc6d218000,0x7ffc6d23a000,"stack"),(0x7ff423e5d000,0x7ff423e5f000,"anon")]
print("=== entropy scan (256-byte windows, high entropy) ===")
for lo,hi,name in segs_interest:
    off=core_off(lo)
    if off is None:
        print(f"  {name}: not mapped"); continue
    length=0
    for t,o,v,fsz in cph:
        if t==1 and v<=lo<v+fsz:
            length=min(hi-lo, v+fsz-lo)
    buf=core[off:off+length]
    for i in range(0,len(buf)-256,256):
        w=buf[i:i+256]
        if w.count(0)>240: continue
        e=entropy(w)
        if e>6.5:
            va=lo+i
            print(f"  {name} @0x{va:x} entropy={e:.2f}  {w[:32].hex()}")

# Also: find refs in text to .bss addresses (0x4afae0+) that might hold decrypted flag
