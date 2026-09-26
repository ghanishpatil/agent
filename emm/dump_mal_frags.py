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
def core_va(va,ln):
    for t,off,v,fsz in cph:
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None
MASK64=(1<<64)-1
material_seed=0xfdcb481154b4e179
frag10 = (material_seed ^ 0xa55a93c61742e8d1)&MASK64
print(f"material_seed = {material_seed:016x}")
print(f"expected frag+0x10 = {frag10:016x}  bytes(LE)={frag10.to_bytes(8,'little').hex()}")
target = frag10.to_bytes(8,"little")
# find frags whose +0x10 == target
MAGIC=struct.pack("<Q",0x6c87fd21d450a39b)
i=0; found=[]
while True:
    j=core.find(MAGIC,i)
    if j<0: break
    va=off2va(j)
    if va and va>0x3755000:
        b=core[j:j+0x58]
        if b[0x10:0x18]==target:
            found.append((va,b))
    i=j+1
print(f"\nmalicious fragments found: {len(found)}")
for va,b in found:
    print(f"\n-- frag @0x{va:x} --")
    for k in range(0,0x58,16):
        c=b[k:k+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in c)
        print(f"  +0x{k:02x}: {c.hex()}  {asc}")
