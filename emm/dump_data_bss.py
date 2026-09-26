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

def dump(va,ln,label):
    print(f"\n===== {label}: VA 0x{va:x} len 0x{ln:x} =====")
    b=core_va(va,ln)
    if b is None:
        print("NOTMAPPED"); return
    for i in range(0,len(b),16):
        chunk=b[i:i+16]
        if chunk==b"\x00"*16: 
            continue
        hexs=" ".join(f"{x:02x}" for x in chunk)
        asc="".join(chr(x) if 32<=x<127 else "." for x in chunk)
        print(f"  0x{va+i:x}: {hexs:<48} {asc}")

# .data 0x4ae0c0 .. 0x4afac8 ; .bss 0x4afae0 .. 0x4b6288
dump(0x4ae0c0,0x1a08,".data")
dump(0x4afae0,0x2000,".bss (first 0x2000)")
dump(0x4b1ae0,0x2000,".bss (mid)")
dump(0x4b3ae0,0x2800,".bss (rest)")
