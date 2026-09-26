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
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None
MASK64=(1<<64)-1
STRUCT=0x3767ad0
S=core_va(STRUCT,0xac)
sid16=S[0x10:0x20]          # raw[0:16]
sid_hi=struct.unpack_from("<Q",S,0x20)[0]   # raw[0x10] qword = S+0x20
# reconstruct raw record 0x9c bytes
raw=bytearray(0x9c)
# raw[0:0x10] = sid16 (S+0x10..0x20)
raw[0:0x10]=sid16
# raw[0x10:0x18] = S+0x20 qword ; raw[0x18:0x20] = S+0x28 qword
raw[0x10:0x18]=S[0x20:0x28]
raw[0x18:0x20]=S[0x28:0x30]
# raw[0x20:0x22]=S+0x30 word ; raw[0x22]=case selector? S+0x32=raw[0x23]; raw[0x22]=? 
# From S-build: S+0x30=raw[0x20] word (0x4019be movzx word[r13+0x20]); S+0x32=raw[0x23] (0x4019cb byte[r13+0x23])
raw[0x20:0x22]=S[0x30:0x32]
raw[0x23]=S[0x32]
# raw[0x22] = case selector, read at 0x401f29 byte[r13+0x22]; we know it's 2 for malicious
raw[0x22]=2
# malicious fragments (6), ordered by event 0..5. Load them.
frag_vas=[0x3767c60,0x3767d90,0x3767ed0,0x3768020,0x3768180,0x37682f0]
frags=[core_va(v,0x40) for v in frag_vas]
# recover raw[0x24 + event*4 + rdx]
for event in range(6):
    f=frags[event]
    kA=(0xa7 + event*0x11)&0xff
    sidbyte=sid16[(event*5)&0xf]
    for rdx in range(4):
        val=f[0x20+rdx] ^ sidbyte ^ kA ^ ((sid_hi>>(rdx*8))&0xff)
        pos=0x24 + event*4 + rdx
        if pos<0x9c: raw[pos]=val&0xff
# raw[0x3c:0x9c] from struct: S+0x44=raw[0x3c] qword ... S+0x54..0x94 = raw[0x4c..0x8c]; S+0x94..0xa4=raw[0x8c..0x9c]
raw[0x3c:0x44]=S[0x44:0x4c]      # raw[0x3c:0x44]
raw[0x44:0x48]=S[0x4c:0x50]      # raw[0x44] dword
raw[0x48:0x4a]=S[0x50:0x52]      # raw[0x48] word
raw[0x4c:0x8c]=S[0x54:0x94]      # rep movsd 0x10 dwords
raw[0x8c:0x9c]=S[0x94:0xa4]      # movdqu
print("Reconstructed raw malicious record (0x9c bytes):")
for i in range(0,0x9c,16):
    c=bytes(raw[i:i+16]); asc="".join(chr(x) if 32<=x<127 else "." for x in c)
    print(f"  +0x{i:02x}: {c.hex()}  {asc}")
print("\nASCII of whole record:", "".join(chr(x) if 32<=x<127 else "." for x in raw))
