#!/usr/bin/env python3
import struct
from capstone import *
from capstone.x86 import X86_OP_MEM, X86_REG_RIP
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
def read(p):
    with open(p,"rb") as f: return f.read()
data=read(BIN)
TEXT_ADDR=0x4011c0; TEXT_OFF=0x11c0
def rostr(va):
    if 0x483000<=va<0x49f584:
        off=0x83000+(va-0x483000); end=data.find(b"\x00",off)
        return data[off:end].decode("latin1","replace")
    return None
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
def dis(start,end):
    oo=start-TEXT_ADDR+TEXT_OFF
    code=data[oo:oo+(end-start)]
    for insn in md.disasm(code,start):
        if insn.address>=end: break
        note=""
        for op in insn.operands:
            if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                tgt=insn.address+insn.size+op.mem.disp
                s=rostr(tgt)
                note=f'   ; ->0x{tgt:x}'+(f' "{s[:40]}"' if s else "")
        if insn.mnemonic=="call": note+="  [CALL]"
        print(f"  0x{insn.address:x}: {insn.mnemonic} {insn.op_str}{note}")
dis(0x40192c,0x401d01)
