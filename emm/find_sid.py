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
        off,va,_,fsz,mz,_=struct.unpack_from("<QQQQQQ",d,o+8); out.append((t,off,va,fsz,mz))
    return out
cph=parse_phdrs(core)
def off2va(off):
    for t,o,v,fsz,mz in cph:
        if t==1 and o<=off<o+fsz: return v+(off-o)
    return None
SID=bytes.fromhex("e2b93ce7be264fc612475208ab131dd0")
print("=== all occurrences of malicious session id (16 bytes) ===")
i=0
while True:
    j=core.find(SID,i)
    if j<0: break
    va=off2va(j)
    print(f"  fileoff=0x{j:x}  VA={'0x%x'%va if va else '?'}")
    i=j+1
# also 8-byte prefix
print("\n=== segments list ===")
for t,o,v,fsz,mz in cph:
    if t==1:
        print(f"  VA 0x{v:x} - 0x{v+mz:x}  filesz=0x{fsz:x} off=0x{o:x}")
