#!/usr/bin/env python3
"""Find code refs to key VAs, dump rodata.cst32, and disassemble crypto regions."""
import struct
from capstone import *

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"

def read(p):
    with open(p,"rb") as f:
        return f.read()

data=read(BIN)

# key VAs / offsets
TEXT_ADDR=0x4011c0; TEXT_OFF=0x11c0; TEXT_SIZE=0x80f10
RODATA_ADDR=0x483000; RODATA_OFF=0x83000; RODATA_SIZE=0x1c584

def off_to_va_text(o): return TEXT_ADDR+(o-TEXT_OFF)

# dump rodata.cst32
print("=== rodata.cst32 @0x49f5a0 (0x60 bytes) ===")
cst=data[0x9f5a0:0x9f5a0+0x60]
for i in range(0,0x60,16):
    print("  "+cst[i:i+16].hex())

# what's in binary at 0x48525f region (core had ciphertext) ?
print("\n=== binary .rodata @0x48523f (0x120) ===")
r=data[0x8723f:0x8723f+0x120]
for i in range(0,0x120,16):
    va=0x48523f+i
    print(f"  0x{va:x}: {r[i:i+16].hex()}")

# scan .text for LEA rip-relative refs to target VAs
targets={0x48523f:"[atlas/session/v3", 0x48525f:"ciphertext_blob", 0x49f5a0:"cst32"}
text=data[TEXT_OFF:TEXT_OFF+TEXT_SIZE]
md=Cs(CS_ARCH_X86,CS_MODE_64)
md.detail=True
print("\n=== code refs (lea/mov rip-relative) to targets ===")
for insn in md.disasm(text, TEXT_ADDR):
    if insn.mnemonic in ("lea","mov","add","cmp"):
        for op in insn.operands:
            if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                tgt=insn.address+insn.size+op.mem.disp
                if tgt in targets:
                    print(f"  0x{insn.address:x}: {insn.mnemonic} {insn.op_str}  -> {targets[tgt]}")
                # also near-range around ciphertext start
                elif 0x48523f<=tgt<0x48523f+0x20:
                    print(f"  0x{insn.address:x}: {insn.mnemonic} {insn.op_str}  -> near {hex(tgt)}")
