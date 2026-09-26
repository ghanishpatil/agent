#!/usr/bin/env python3
import os, struct, re
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune"

# .DS_Store records: filenames are stored as UTF-16-BE length-prefixed.
# Simple approach: scan for UTF-16BE strings (records store name then structure id like 'Iloc','bwsp' etc)
def utf16be_strings(d, minlen=1):
    out=[]
    i=0
    n=len(d)
    while i < n-1:
        # try to read a length-prefixed utf16be name: 4-byte length (count of chars) then chars
        # heuristic: find runs of (00 XX) printable
        j=i
        chars=bytearray()
        while j < n-1 and d[j]==0 and 0x20<=d[j+1]<0x7f:
            chars.append(d[j+1]); j+=2
        if len(chars)>=minlen:
            out.append((i,bytes(chars).decode('latin1')))
            i=j
        else:
            i+=1
    return out

for rel in ["Phishtofortune/xl/.DS_Store","Phishtofortune/.DS_Store","Phishtofortune/xl/worksheets/.DS_Store"]:
    p=os.path.join(ROOT,*rel.split("/"))
    d=open(p,"rb").read()
    print(f"\n===== {rel} UTF-16BE names =====")
    seen=set()
    for off,s in utf16be_strings(d,2):
        if s in seen: continue
        seen.add(s)
        print(f"  @{off}: {s!r}")
