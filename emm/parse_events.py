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

# events buffer 0x3752c40, size 0x2c38. Record stride: find by scanning for tag 0xe2197a4c5b30d8f1
buf=core_va(0x3752c40,0x2c38)
TAG=struct.pack("<Q",0xe2197a4c5b30d8f1)
offs=[i for i in range(0,len(buf)-8) if buf[i:i+8]==TAG]
print(f"[+] {len(offs)} event records; first stride={offs[1]-offs[0] if len(offs)>1 else '?'}")

def cstr(b):
    e=b.find(b"\x00"); 
    return b[:e if e>=0 else len(b)].decode("latin1","replace")

records=[]
for o in offs:
    rec=buf[o:o+0x50]
    code=struct.unpack_from("<I",rec,8)[0]
    ctr=struct.unpack_from("<Q",rec,0x10)[0]
    mat=rec[0x1c:0x28]      # 12 bytes? 
    ev=cstr(rec[0x28:0x50])
    records.append((0x3752c40+o,code,ctr,rec,ev))

for va,code,ctr,rec,ev in records:
    print(f"  @0x{va:x} code=0x{code:08x} ctr=0x{ctr:x}  ev={ev!r}")
    print(f"        raw10-28: {rec[0x10:0x28].hex()}")
