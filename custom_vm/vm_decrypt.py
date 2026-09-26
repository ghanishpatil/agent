from pwn import *
context.arch='amd64'
p = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e = ELF(p, checksec=False)

# source blob for decryption at vaddr 0x20c0, length 0x15d (349)
SRC = 0x20c0
LEN = 0x15d
src = e.read(SRC, LEN)

# LCG decrypt: seed=0xc0ffee42; each iter seed=seed*0x41c64e6d+0x3039; ks=(seed>>16)&0xff
seed = 0xc0ffee42
dec = bytearray()
for i in range(LEN):
    seed = (seed*0x41c64e6d + 0x3039) & 0xffffffff
    ks = (seed>>16)&0xff
    dec.append(src[i]^ks)
dec = bytes(dec)

sbox = dec[:256]
program = dec[256:]   # 93 bytes
print("program len:", len(program))
print("sbox first 16:", sbox[:16].hex())
print("sbox is permutation:", sorted(sbox)==list(range(256)))
print("program hex:", program.hex())

# jump table at 0x2020, 35 int32 offsets; target = 0x2020 + offset ; maps opcode-0xa1
JT = 0x2020
jt = e.read(JT, 35*4)
import struct
offs = struct.unpack("<35i", jt)
targets = [ (0x2020+o) for o in offs]
handler_names = {
 0x1580:"XORCMP(a,b): M[a]^=M[b]; flag=(oldM[a]==M[b])",
 0x15b0:"SBOX(a): M[a]=sbox[M[a]]",
 0x15d0:"SETI(a,b): M[a]=b",
 0x15f0:"MOV(a,b): M[a]=M[b]",
 0x1610:"LDIN(a,b): M[a]=IN[M[b]] if M[b]<32 else 0",
 0x14d0:"(invalid/return)",
}
print("\n=== jump table opcode(0xa1+idx) -> target ===")
for idx,t in enumerate(targets):
    op = 0xa1+idx
    nm = handler_names.get(t, hex(t))
    print(f"  op {op:#04x} idx{idx:2} -> {t:#06x}  {nm}")

# build opcode->handler map for a1..c3 range
op2handler={}
for idx,t in enumerate(targets):
    op2handler[0xa1+idx]=t
# high opcodes
HIGH={0xd4:"ADD(a,b): M[a]+=b",0xe5:"ROL(a): M[a]=rol8(M[a],3)",
      0xf6:"HASH(a,b): FNV fold M[a],M[b],M[1]",0xe9:"CHECK: res=(M[1]==0x20 && H==target)",
      0x17:"JNE(a): if flag==0: pc=a"}

print("\n=== DISASSEMBLY (3 bytes/instr) ===")
for pc in range(0,len(program),3):
    op=program[pc]; a=program[pc+1] if pc+1<len(program) else 0; b=program[pc+2] if pc+2<len(program) else 0
    if op in HIGH:
        desc=HIGH[op]
    elif op==0x17:
        desc="JNE"
    elif op in op2handler:
        t=op2handler[op]
        desc=handler_names.get(t,hex(t))
    else:
        desc="???"
    print(f"  {pc:3}: {op:#04x} {a:#04x} {b:#04x}   {desc}")
