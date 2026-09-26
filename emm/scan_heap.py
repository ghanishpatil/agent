#!/usr/bin/env python3
import struct, re
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
def seg_of(off):
    for t,o,v,fsz in cph:
        if t==1 and o<=off<o+fsz: return v+(off-o)
    return None
# heap seg 0x3751000-0x3773000 => file off 0xb8000 .. 0xda000
HSTART=0xb8000; HEND=0xda000
heap=core[HSTART:HEND]
print("=== printable ascii strings len>=5 in heap ===")
for m in re.finditer(rb"[\x20-\x7e]{5,}", heap):
    s=m.group(); va=seg_of(HSTART+m.start())
    if b"flag" in s.lower() or b"{" in s or b"FCG" in s or b"ATLS" in s or b"atlas" in s or b"node" in s or b"case" in s.lower() or b"result" in s.lower():
        print(f"  VA 0x{va:x}: {s}")
print("\n=== search 'flag' whole core ===")
for m in re.finditer(rb"flag", core, re.I):
    va=seg_of(m.start())
    ctx=core[m.start():m.start()+40]
    print(f"  off 0x{m.start():x} VA {'0x%x'%va if va else '?'}: {ctx}")
print("\n=== search 'FCG' / 'FLAG' ===")
for pat in (b"FCG", b"CTF", b"flag{"):
    for m in re.finditer(re.escape(pat), core):
        va=seg_of(m.start())
        print(f"  {pat} off 0x{m.start():x} VA {'0x%x'%va if va else '?'}")
