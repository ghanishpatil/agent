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
def cva(va,ln):
    for t,off,v,fsz in cph:
        if t==1 and v<=va<v+fsz:
            s=off+(va-v); return core[s:s+ln]
    return None

# Find all frag buffers by magic 0x6c87fd21d450a39b across heap
FMAG=struct.pack("<Q",0x6c87fd21d450a39b)
# scan whole core
locs=[]
i=0
while True:
    j=core.find(FMAG,i)
    if j<0: break
    locs.append(j); i=j+1
print(f"[+] {len(locs)} frag magics")
# map file off -> va
def off2va(o):
    for t,foff,v,fsz in cph:
        if t==1 and foff<=o<foff+fsz:
            return v+(o-foff)
    return None
# dump first few frags fully
for j in locs[:8]:
    va=off2va(j)
    b=core[j:j+0x60]
    print(f"\n frag @va 0x{va:x} (off 0x{j:x}):")
    for k in range(0,0x60,16):
        ch=b[k:k+16]
        asc="".join(chr(x) if 32<=x<127 else "." for x in ch)
        print(f"   {ch.hex()}  {asc}")
