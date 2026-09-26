#!/bin/bash
cd /work/waf
L=libc.so.6
chmod +x $L 2>/dev/null
echo "=== version ==="
strings $L | grep -iE "glibc 2\.[0-9]+" | head -3
echo "=== key symbols (offsets) ==="
python3 - <<'PY'
from pwn import *
libc=ELF("/work/waf/libc.so.6",checksec=False)
for s in ["system","__libc_start_main","__libc_start_call_main","_IO_2_1_stdout_","_IO_2_1_stdin_","printf","read"]:
    try: print(f"{s:24} {hex(libc.symbols[s])}")
    except Exception as e: print(s,"?",e)
# /bin/sh
try: print("binsh                   ", hex(next(libc.search(b"/bin/sh"))))
except Exception as e: print("binsh?",e)
# what is at 0x21F380 in THIS libc? (local leak offset may differ; we will recompute on remote)
PY
echo "=== one_gadget ==="
one_gadget /work/waf/libc.so.6 2>/dev/null | head -40
