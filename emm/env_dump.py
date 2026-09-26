#!/usr/bin/env python3
import struct, base64, re
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
core=read(CORE)

# The stack segment is at file 0xdc000 vaddr 0x7ffc6d218000 size 0x22000
stack=core[0xdc000:0xdc000+0x22000]
# dump all NUL-delimited strings with '=' (env vars) and long tokens
print("=== env-like strings in stack ===")
for tok in re.split(rb"\x00", stack):
    if 3<=len(tok)<=200 and b"=" in tok:
        try:
            s=tok.decode("latin1")
        except: continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", s):
            print("  "+s)

print("\n=== decode candidate base64 tokens ===")
for b in [b"Y2NhcmVudl82YTkyOTgzYjQyOTg4MTkxYmM4ZjY5MWExMDNlNDNmMg"]:
    try:
        pad=b+b"="*((4-len(b)%4)%4)
        print(f"  {b.decode()} -> {base64.b64decode(pad)!r}")
    except Exception as e:
        print("  err",e)

# look for flag-ish keywords anywhere
print("\n=== keyword scan whole core ===")
for kw in [b"flag",b"FLAG",b"case",b"CASE",b"result",b"RESULT",b"verdict",b"exfil",b"payload",b"deltaforge",b"DeltaForge",b"authenticated"]:
    idx=0
    cnt=0
    while True:
        i=core.find(kw,idx)
        if i<0: break
        ctx=core[max(0,i-8):i+40]
        asc="".join(chr(x) if 32<=x<127 else "." for x in ctx)
        print(f"  {kw.decode():14} @0x{i:x}: {asc}")
        idx=i+1; cnt+=1
        if cnt>6: break
