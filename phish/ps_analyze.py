#!/usr/bin/env python3
import re
P1=r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\printerSettings\printerSettings1.bin"
P2=r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\printerSettings\printerSettings2.bin"
d1=open(P1,"rb").read(); d2=open(P2,"rb").read()
print("len1",len(d1),"len2",len(d2),"identical:",d1==d2)
if d1!=d2:
    diffs=[i for i in range(min(len(d1),len(d2))) if d1[i]!=d2[i]]
    print("diff offsets:",diffs[:50])

# non-zero regions after offset 1100 (DEVMODE core ends around there)
print("\n=== non-zero bytes after offset 1100 ===")
for i in range(1100,len(d1),16):
    ch=d1[i:i+16]
    if any(b!=0 for b in ch):
        asc="".join(chr(x) if 32<=x<127 else "." for x in ch)
        print(f"  {i}: {ch.hex()}  {asc}")

# all utf-16le strings
print("\n=== utf-16le strings ===")
for m in re.finditer(rb"(?:[\x20-\x7e]\x00){3,}", d1):
    print("  ",m.group().decode("utf-16-le"))
