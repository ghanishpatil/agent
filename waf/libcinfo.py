#!/usr/bin/env python3
from pwn import *
libc = ELF("/work/waf/libc.so.6", checksec=False)
print("=== symbols (offsets in libc) ===")
for s in ["system","__libc_start_main","__libc_start_call_main","printf","read","puts","setvbuf","environ"]:
    try: print(f"{s:26} {hex(libc.symbols[s])}")
    except Exception as e: print(s, "?", e)
for s in ["_IO_2_1_stdout_","_IO_2_1_stdin_","_IO_2_1_stderr_"]:
    try: print(f"{s:26} {hex(libc.symbols[s])}")
    except: pass
try: print("binsh                      ", hex(next(libc.search(b"/bin/sh\x00"))))
except Exception as e: print("binsh?", e)
# The local leak %5$p was libc_base + 0x21F380 (in the LOCAL ubuntu libc). The remote offset differs.
# We'll recompute the leak offset for THIS remote libc empirically after we know what %5$p points to.
# Guess: %5$p is a pointer set by setvbuf/stdout; check _IO_2_1_stdout_ and file jump tables.
print("=== glibc version string ===")
import subprocess
try:
    out=subprocess.check_output(["strings","/work/waf/libc.so.6"]).decode(errors="ignore")
    for line in out.splitlines():
        if "GNU C Library" in line or "release version" in line.lower():
            print(line.strip()[:120]); break
except Exception as e: print("ver?",e)
