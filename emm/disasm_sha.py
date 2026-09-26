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
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
def dis(start, maxlen=0x400):
    oo=start-TEXT_ADDR+TEXT_OFF
    code=data[oo:oo+maxlen]
    for insn in md.disasm(code,start):
        note=""
        for op in insn.operands:
            if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                tgt=insn.address+insn.size+op.mem.disp
                note=f'   ; ->0x{tgt:x}'
        if insn.mnemonic=="call": note+="  [CALL]"
        print(f"  0x{insn.address:x}: {insn.mnemonic} {insn.op_str}{note}")
        if insn.mnemonic=="ret": break

print("===== 0x402b20 (full to ret) =====")
dis(0x402b20, 0x600)
