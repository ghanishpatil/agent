#!/usr/bin/env python3
import os, re
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune"
for rel in ["Phishtofortune/.DS_Store","Phishtofortune/xl/.DS_Store",
            "Phishtofortune/xl/worksheets/.DS_Store"]:
    p=os.path.join(ROOT,*rel.split("/"))
    d=open(p,"rb").read()
    print(f"\n===== {rel} ({len(d)}) full hexdump of non-standard regions =====")
    # DS_Store has header, then a big allocated tree. Dump everything, skip long zero runs
    i=0
    while i < len(d):
        ch=d[i:i+16]
        if ch==b"\x00"*16:
            i+=16; continue
        asc="".join(chr(x) if 32<=x<127 else "." for x in ch)
        print(f"  {i:5}: {ch.hex()}  {asc}")
        i+=16
