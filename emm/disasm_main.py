#!/usr/bin/env python3
import struct
from capstone import *
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
data=read(BIN); core=read(CORE)
TEXT_ADDR=0x4011c0; TEXT_OFF=0x11c0; TEXT_SIZE=0x80f10

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

print("=== core bytes at key VAs ===")
for va,ln in [(0x485207,0x60),(0x485220,0x20),(0x485240,0x20),(0x485260,0x100),
              (0x485360,0xB0)]:
    b=core_va(va,ln)
    print(f"  0x{va:x}: {b.hex() if b else 'NOTMAPPED'}")

# disasm the malware region
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
def dis(start,end):
    o=start-TEXT_ADDR+TEXT_OFF
    code=data[o:o+(end-start)]
    for insn in md.disasm(code,start):
        rip=""
        for op in insn.operands:
            if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                tgt=insn.address+insn.size+op.mem.disp
                rip=f"   ; ->0x{tgt:x}"
        print(f"  0x{insn.address:x}: {insn.mnemonic} {insn.op_str}{rip}")

print("\n=== disasm 0x402700 - 0x402e00 ===")
dis(0x402700,0x402e00)
