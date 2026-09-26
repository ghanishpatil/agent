#!/usr/bin/env python3
import struct, hashlib
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
core=open(CORE,"rb").read()
def cva(va,ln):
    ph=struct.unpack_from("<Q",core,32)[0]; n=struct.unpack_from("<H",core,56)[0]; ent=struct.unpack_from("<H",core,54)[0]
    for i in range(n):
        o=ph+i*ent; t=struct.unpack_from("<I",core,o)[0]
        off,v,pa,fsz=struct.unpack_from("<QQQQ",core,o+8)
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None

# dump struct at 0x3767ad0
print("=== struct @0x3767ad0 (0xb0) ===")
S=cva(0x3767ad0,0xb0)
if S:
    for i in range(0,0xb0,16):
        ch=S[i:i+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in ch)
        print(f"  +0x{i:02x}: {ch.hex()}  {asc}")
else:
    print("  NOTMAPPED")

# The malicious session id
sid=bytes.fromhex("e2b93ce7be264fc612475208ab131dd0")

# Search whole core for any frag whose data, when interpreted, contains 'flag' after xor with session id repeat
def try_ascii(b):
    return all(9<=x<127 for x in b) and any(0x20<=x<127 for x in b)

# Collect all frag buffers (marker 9ba350d421fd876c), take 0x18 bytes after marker+8
FMAG=struct.pack("<Q",0x6c87fd21d450a39b)
locs=[]; i=0
while True:
    j=core.find(FMAG,i)
    if j<0: break
    locs.append(j); i=j+1

# For each frag, xor its 0x30 data bytes (after marker) with repeating sid and with key, look for 'flag'
key=bytes.fromhex("ced85adfd47e88a7de72f8a153d3ee7847ccf32e95b4d88745d75cd504943b5c")
found=0
for j in locs:
    data=core[j+8:j+8+0x40]
    for mask,name in [(sid,"sid"),(key,"key")]:
        x=bytes(data[k]^mask[k%len(mask)] for k in range(len(data)))
        if b"flag" in x.lower() or b"flag{" in x.lower():
            print(f"  FLAG-ish frag@0x{j:x} xor {name}: {x}")
            found+=1
print(f"[+] xor-scan found={found}")

# Also brute single-byte xor over every frag looking for 'flag{'
found2=0
for j in locs:
    data=core[j+8:j+8+0x40]
    for kb in range(256):
        x=bytes(c^kb for c in data)
        if b"flag{" in x:
            print(f"  frag@0x{j:x} xor 0x{kb:02x}: {x}")
            found2+=1
print(f"[+] single-byte-xor found={found2}")
