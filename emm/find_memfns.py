#!/usr/bin/env python3
import struct
from capstone import *
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
data=open(BIN,'rb').read()
# .text 0x4011c0 off 0x11c0 size 0x80f10
TA=0x4011c0; TO=0x11c0; TS=0x80f10
code=data[TO:TO+TS]
md=Cs(CS_ARCH_X86,CS_MODE_64)
# scan for 'vpbroadcastb' (memset) and 'vmovdqu' heavy funcs preceded by endbr64
# find endbr64 (f3 0f 1e fa) then next insn
i=0
memset_entries=[]; memcpy_entries=[]
while True:
    j=code.find(b"\xf3\x0f\x1e\xfa", i)
    if j<0: break
    va=TA+j
    # disasm the instruction after endbr64
    insns=list(md.disasm(code[j:j+16], va))
    if len(insns)>=2:
        m=insns[1].mnemonic
        if m=="vpbroadcastb":
            memset_entries.append(va)
        elif m in ("vmovdqu64","vmovdqu","movdqu") and "ymm" in insns[1].op_str+insns[0].op_str:
            memcpy_entries.append(va)
    i=j+1
print("memset entries (vpbroadcastb):", [hex(x) for x in memset_entries])
print("memcpy-ish entries:", [hex(x) for x in memcpy_entries][:20])
