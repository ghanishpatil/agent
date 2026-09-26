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
MAGIC=struct.pack("<Q",0x8f0d71c24ab693e5)
i=0; sess=[]
while True:
    j=core.find(MAGIC,i)
    if j<0: break
    va=off2va(j)
    if va and va>0x3000000:
        b=core[j:j+0xac]
        sid=b[0x10:0x20]
        sel=b[0x32]     # raw[0x23]
        mat=struct.unpack_from("<Q",b,0x34)[0]
        sess.append((va,sid.hex(),sel,mat))
    i=j+1
print(f"sessions: {len(sess)}")
for va,sid,sel,mat in sess:
    # try ascii of sid
    sb=bytes.fromhex(sid)
    asc="".join(chr(x) if 32<=x<127 else "." for x in sb)
    print(f"  0x{va:x} sel(raw0x23)={sel:#x} mat={mat:016x} sid={sid}  '{asc}'")
