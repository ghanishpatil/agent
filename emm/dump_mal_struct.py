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

# event buffer base 0x3752c40, records 0x58 each. Malicious ctr 0x73..0x78 at 0x37553d0
BASEVA=0x3752c40
buf=core_va(BASEVA,0x2c38)
# Find the "frame accepted" of malicious by session id
SID=bytes.fromhex("e2b93ce7be264fc612475208ab131dd0")
# each record 0x58; the record layout (relative to record start = event string start?)
# From hexdump: at 0x37553d0 the event string starts; the record extends to 0x3755428.
# Let's treat record start where event string is, size 0x58, and parse the TRAILING fields
# Actually the emit writes: rec+0x38 counter8, rec+0x40 r8(8), rec+0x48 src[0x10:0x20](16), rec+0x58 code...
# But the visible layout shows string at start. Let's just dump raw 0x58 blocks for ctr 0x73..0x78.
recs = {
 0x73:0x37553d0, 0x74:0x3755428, 0x75:0x3755480,
 0x76:0x37554d8, 0x77:0x3755530, 0x78:0x3755588,
}
for ctr,va in recs.items():
    b=core_va(va,0x58)
    print(f"\n=== ctr 0x{ctr:x} @0x{va:x} ===")
    for i in range(0,0x58,16):
        chunk=b[i:i+16]
        asc="".join(chr(x) if 32<=x<127 else "." for x in chunk)
        print(f"  +0x{i:02x}: {chunk.hex()}  {asc}")
    # parse the two u64 fields near +0x30 and +0x38, 16 bytes at +0x40
    # from hexdump alignment: at va+0x30 there is [tsval][ctr8][mat8][sid16][code][len]
