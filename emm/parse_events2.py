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

buf=core_va(0x3752c40,0x2c38)
BASEVA=0x3752c40
EVENTS=[b"frame accepted",b"signature mismatch",b"offline cache accepted",b"anonymous image fd",
        b"rx page executable",b"context metadata scrubbed",b"signature verified",b"maintenance image fd",
        b"jit worker mapping",b"session retired",b"quarantine enforced",b"execution denied"]
# find every event string occurrence, and read the 0x28 bytes before it (record header)
hits=[]
for ev in EVENTS:
    i=0
    while True:
        j=buf.find(ev,i)
        if j<0: break
        hits.append((j,ev.decode()))
        i=j+1
hits.sort()
print(f"[+] {len(hits)} event occurrences\n")
for j,ev in hits:
    hdr=buf[j-0x28:j]   # header preceding the event string
    code=struct.unpack_from("<I",hdr,0x20)[0] if len(hdr)>=0x24 else 0
    mat16=hdr[0x08:0x18]
    ctr=struct.unpack_from("<Q",hdr,0x0)[0]
    print(f"  @0x{BASEVA+j:x} ctr=0x{ctr:x} code=0x{code:08x} mat={mat16.hex()}  {ev}")
