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

# dump the small anon segment 0x7ff423e5d000 (0x2000)
print("=== anon 0x7ff423e5d000 (first 0x400) ===")
b=core_va(0x7ff423e5d000,0x2000)
if b:
    for i in range(0,0x400,16):
        chunk=b[i:i+16]
        if chunk==b"\x00"*16: continue
        asc="".join(chr(x) if 32<=x<127 else "." for x in chunk)
        print(f"  0x{0x7ff423e5d000+i:x}: {chunk.hex()}  {asc}")

# Records are 0x9c each. The record has case byte at +0x22. Let's scan whole core for
# plausible record arrays: look in heap+anon for structures. Actually the parsed copy
# used [rsi+0x30]=word[r13+0x20], [rsi+0x32]=byte[r13+0x22]. 
# Search stack for pointer near 'ATLSCFG3' region. Print stack tail (env/args already seen).
# Find magic in whole core
mg=struct.pack("<Q",0x33474643534c5441)
i=0
print("\n=== 'ATLSCFG3' magic occurrences ===")
while True:
    j=core.find(mg,i)
    if j<0: break
    print(f"  file off 0x{j:x}")
    i=j+1
