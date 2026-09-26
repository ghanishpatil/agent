#!/usr/bin/env python3
import struct, re
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
core=read(CORE)

# search entire core for 'flag' 'READY' and long printable runs on the stack
print("=== 'READY' occurrences (whole core) ===")
i=0
while True:
    j=core.find(b"READY",i)
    if j<0: break
    ctx=core[j:j+64]
    asc="".join(chr(x) if 32<=x<127 else "." for x in ctx)
    print(f"  off 0x{j:x}: {asc}")
    i=j+1

print("\n=== 'flag' / 'flag{' (whole core, case-insensitive) ===")
for kw in [b"flag{",b"FLAG{",b"flag",b"HTF{"]:
    i=0; c=0
    while c<8:
        j=core.lower().find(kw.lower(),i)
        if j<0: break
        ctx=core[max(0,j-4):j+50]
        asc="".join(chr(x) if 32<=x<127 else "." for x in ctx)
        print(f"  {kw.decode():6} off 0x{j:x}: {asc}")
        i=j+1; c+=1

# Long printable ASCII runs (>=10) in stack segment
print("\n=== printable runs >=10 in stack (off 0xdc000..0xfe000) ===")
stack=core[0xdc000:0xfe000]
STACK_VA=0x7ffc6d218000
for m in re.finditer(rb"[\x20-\x7e]{10,}", stack):
    s=m.group()
    # skip obvious env/paths already seen
    if b"/opt/codex" in s or b"proxy" in s.lower() or b"/workspace" in s or b"codex" in s.lower(): continue
    va=STACK_VA+m.start()
    print(f"  0x{va:x}: {s.decode()}")
