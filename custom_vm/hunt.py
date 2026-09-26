from pwn import *
import vm_model as VM
context.arch='amd64'
P = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e=ELF(P,checksec=False)
raw=open(P,'rb').read()

AES_SBOX = bytes.fromhex(
"637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
"b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
"09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
"d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
"cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
"e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
"ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
"e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")

print("decrypted sbox == standard AES sbox:", VM.SBOX==AES_SBOX)
if VM.SBOX!=AES_SBOX:
    diffs=[(i,VM.SBOX[i],AES_SBOX[i]) for i in range(256) if VM.SBOX[i]!=AES_SBOX[i]]
    print("diffs:",diffs)

# dump rodata gaps
def dump(a0,a1,label):
    d=e.read(a0,a1-a0)
    print(f"[{label}] {a0:#x}-{a1:#x}: {d.hex()}")
    print("   ascii:", "".join(chr(x) if 32<=x<127 else '.' for x in d))
dump(0x2000,0x2020,"before jumptable")
dump(0x20ac,0x20c0,"after jumptable")
dump(0x4028,0x4038,".data")

# scan whole binary + decrypted for IATCQ or flag-ish
for tag,blob in [("raw",raw),("dec",VM.SBOX+VM.PROG)]:
    idx=blob.find(b"IATCQ")
    print(tag,"IATCQ at",idx)

# check DOF: can two format+printable inputs share target? try flipping b[30] and re-solving b[29] to keep hash
# quick: brute b[29],b[30] over printable for a fixed rest to see how many (b29,b30) keep some target reachable
# Instead: measure sensitivity - does each content byte affect final hash?
base=bytearray(b"IATCQ{"+b"A"*25+b"}")
h0=VM.vm(bytes(base))
print("base hash",hex(h0))
for pos in [6,15,20,30]:
    b2=bytearray(base); b2[pos]^=1
    print(f"flip byte {pos}: hash {hex(VM.vm(bytes(b2)))} (changed={VM.vm(bytes(b2))!=h0})")
