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
def off2va(off):
    for t,o,v,fsz in cph:
        if t==1 and o<=off<o+fsz: return v+(off-o)
    return None
MAGIC=struct.pack("<Q",0x6c87fd21d450a39b)
frags=[]
i=0
while True:
    j=core.find(MAGIC,i)
    if j<0: break
    va=off2va(j)
    if va and va>0x3755000:  # only heap frags, skip code
        b=core[j:j+0x40]
        v08=struct.unpack_from("<Q",b,8)[0]
        v10=b[0x10:0x18].hex()
        cnt=b[0x38]
        frags.append((va,v08,v10,cnt,b))
    i=j+1
print(f"heap frags: {len(frags)}")
# group by v10 (shared per session)
from collections import OrderedDict
groups=OrderedDict()
for va,v08,v10,cnt,b in frags:
    groups.setdefault(v10,[]).append((va,cnt,b))
print(f"distinct +0x10 groups: {len(groups)}")
for v10,items in groups.items():
    cnts=[hex(c) for _,c,_ in items]
    print(f"\n+0x10={v10}  n={len(items)} counters={cnts} firstVA=0x{items[0][0]:x}")
