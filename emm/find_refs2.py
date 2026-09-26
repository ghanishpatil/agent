#!/usr/bin/env python3
import struct
from capstone import *
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
CORE = BASE + r"\atlas-sync.core"

def read(p):
    with open(p,"rb") as f: return f.read()

data=read(BIN)
core=read(CORE)

TEXT_ADDR=0x4011c0; TEXT_OFF=0x11c0; TEXT_SIZE=0x80f10
text=data[TEXT_OFF:TEXT_OFF+TEXT_SIZE]

# core seg map
def parse_phdrs(d):
    e_phoff=struct.unpack_from("<Q",d,32)[0]; e_phnum=struct.unpack_from("<H",d,56)[0]; e_phent=struct.unpack_from("<H",d,54)[0]
    out=[]
    for i in range(e_phnum):
        o=e_phoff+i*e_phent
        t=struct.unpack_from("<I",d,o)[0]
        off,va,_,fsz,_,_=struct.unpack_from("<QQQQQQ",d,o+8)
        out.append((t,off,va,fsz))
    return out
cph=parse_phdrs(core)
def core_va(va,ln):
    for t,off,v,fsz in cph:
        if t==1 and v<=va<v+fsz:
            s=off+(va-v); return core[s:s+ln]
    return None

# scan text for rip refs into the malware runtime region 0x483000-0x484000 (context/cipher)
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
print("=== text rip-relative refs into 0x48500-0x4854000 (context/cipher area) ===")
hits=[]
for insn in md.disasm(text,TEXT_ADDR):
    for op in insn.operands:
        if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
            tgt=insn.address+insn.size+op.mem.disp
            if 0x485200<=tgt<=0x485400 or 0x49f5a0<=tgt<0x49f600:
                hits.append((insn.address,insn.mnemonic,insn.op_str,tgt))
for a,m,o,t in hits[:80]:
    print(f"  0x{a:x}: {m} {o}  -> 0x{t:x}")

print(f"\n[+] total hits={len(hits)}")
