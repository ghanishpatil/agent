#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
core=read(CORE)
# stack seg: off 0xdc000 vaddr 0x7ffc6d218000 fsz 0x22000
STACK_OFF=0xdc000; STACK_VA=0x7ffc6d218000; STACK_SZ=0x22000
def va_off(va): return STACK_OFF+(va-STACK_VA)

# magic at file 0xfabb0 -> va
va_magic=STACK_VA+(0xfabb0-STACK_OFF)
print(f"[+] magic VA = 0x{va_magic:x}")
# header: magic(8) count(4) recsize(4) then records. But worker read 0x10 header into [rbp-0x1e0].
# dump 0x400 bytes from magic
b=core[0xfabb0:0xfabb0+0x600]
for i in range(0,len(b),16):
    chunk=b[i:i+16]
    asc="".join(chr(x) if 32<=x<127 else "." for x in chunk)
    print(f"  0x{va_magic+i:x}: {chunk.hex()}  {asc}")
