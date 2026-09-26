#!/usr/bin/env python3
"""Find all rip-relative xrefs in .text to a set of target VAs (data/bss/rodata)."""
import struct
from capstone import *
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
def read(p):
    with open(p,"rb") as f: return f.read()
data=read(BIN)
TEXT_ADDR=0x4011c0; TEXT_OFF=0x11c0; TEXT_SIZE=0x80f10
text=data[TEXT_OFF:TEXT_OFF+TEXT_SIZE]

# status strings (rodata) VAs
status={
 0x483016:"atlas-sync",0x483021:"frame accepted",0x483030:"signature mismatch",
 0x483043:"offline cache accepted",0x48305a:"anonymous image fd",0x48306d:"rx page executable",
 0x48307a:"context metadata scrubbed",0x483094:"signature verified",0x4830a7:"maintenance image fd",
 0x4830bc:"jit worker mapping",0x4830cf:"session retired",0x4830df:"quarantine enforced",
 0x4830f3:"execution denied",
}
bss={0x4afb40:"bss_blob32",0x4b0450:"bss_0x4b0450",0x4b4870:"bss_0x4b4870",
     0x485240:"atlas/session/v3",0x485220:"sha256_iv",0x485260:"sha256_K"}
targets={**status,**bss}

md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
refs={}
for insn in md.disasm(text,TEXT_ADDR):
    for op in insn.operands:
        if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
            tgt=insn.address+insn.size+op.mem.disp
            if tgt in targets:
                refs.setdefault(tgt,[]).append((insn.address,insn.mnemonic,insn.op_str))

for tgt in sorted(refs):
    print(f"\n=== refs to 0x{tgt:x} ({targets[tgt]}) ===")
    for a,m,o in refs[tgt]:
        print(f"  0x{a:x}: {m} {o}")

# also list all string VAs referenced near the status block to find the dispatcher fn
