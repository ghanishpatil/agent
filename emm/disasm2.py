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
    off=0x83000+(va-0x483000); end=data.find(b"\x00",off)
    return data[off:end].decode("latin1","replace")
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True

# find endbr64 (f3 0f 1e fa) prologues between 0x401d00 and 0x402000 to locate function starts
region_start=0x401c00; region_end=0x402400
o=region_start-TEXT_ADDR+TEXT_OFF
blob=data[o:o+(region_end-region_start)]
print("=== endbr64 / push rbp prologues ===")
i=0
while i < len(blob)-4:
    if blob[i:i+4]==b"\xf3\x0f\x1e\xfa":
        print(f"  func @0x{region_start+i:x} (endbr64)")
    i+=1

# Disasm from each candidate; pick the one covering 0x401f77
for start in [0x401d90,0x401db0,0x401dd0,0x401df0,0x401e10]:
    pass

def dis(start,end):
    oo=start-TEXT_ADDR+TEXT_OFF
    code=data[oo:oo+(end-start)]
    for insn in md.disasm(code,start):
        note=""
        for op in insn.operands:
            if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                tgt=insn.address+insn.size+op.mem.disp
                if 0x483000<=tgt<0x49f584:
                    note=f'   ; ->"{rostr(tgt)[:44]}"'
                else:
                    note=f"   ; ->0x{tgt:x}"
        print(f"  0x{insn.address:x}: {insn.mnemonic} {insn.op_str}{note}")

# find the function start covering 0x401f77 by scanning endbr64 just before it
print("\n=== disasm the dispatcher function ===")
dis(0x401d90,0x402360)
