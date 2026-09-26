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
def core_va(va,ln):
    for t,off,v,fsz in cph:
        if t==1 and v<=va<v+fsz:
            s=off+(va-v); return core[s:s+ln]
    return None

STRUCT=0x3767ad0  # base (magic)
b=core_va(STRUCT,0xc0)
def u64(o): return struct.unpack_from("<Q",b,o)[0]
def u32(o): return struct.unpack_from("<I",b,o)[0]
print("magic       +0x00:", "%016x"%u64(0x00))
print("qword485470 +0x08: %08x %08x"%(u32(0x08),u32(0x0c)))
print("session id  +0x10:", b[0x10:0x20].hex())
print("raw[0x10]q  +0x20:", "%016x"%u64(0x20))
print("raw[0x18]q  +0x28:", "%016x"%u64(0x28))
print("raw[0x20]w  +0x30: %04x  raw[0x23]=%02x  const6=%02x"%(struct.unpack_from('<H',b,0x30)[0], b[0x32], b[0x33]))
print("MATERIAL    +0x34:", "%016x"%u64(0x34), "(seed)")
print("FINAL(3c)   +0x3c:", "%016x"%u64(0x3c), "(rol/xor result)")
print("raw[0x3c]q  +0x44:", "%016x"%u64(0x44))
print("raw[0x44]d  +0x4c: %08x"%u32(0x4c))
print("raw[0x48]w  +0x50: %04x"%struct.unpack_from('<H',b,0x50)[0])
print("crc(a4)     +0xa4: %08x"%u32(0xa4))
print("prng(a8)    +0xa8: %08x"%u32(0xa8))
print("\nfull struct bytes 0x00..0xac:")
for i in range(0,0xac,16):
    c=b[i:i+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in c)
    print(f"  +0x{i:02x}: {c.hex()}  {asc}")
# decode material/final as ascii
import binascii
for name,o in [("material",0x34),("final",0x3c)]:
    v=u64(o); by=v.to_bytes(8,"little")
    print(f"{name} LE ascii: {by}  BE ascii: {v.to_bytes(8,'big')}")
