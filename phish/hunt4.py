#!/usr/bin/env python3
import os, re, codecs
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune"

def strings(d,m=4):
    return [(m0.start(), m0.group()) for m0 in re.finditer(rb"[\x20-\x7e]{%d,}"%m, d)]

for rel in ["Phishtofortune/xl/printerSettings/printerSettings1.bin",
            "Phishtofortune/xl/printerSettings/printerSettings2.bin",
            "Phishtofortune/.DS_Store",
            "Phishtofortune/xl/.DS_Store",
            "Phishtofortune/xl/worksheets/.DS_Store"]:
    p=os.path.join(ROOT, *rel.split("/"))
    if not os.path.exists(p):
        print(f"MISSING {rel}"); continue
    d=open(p,"rb").read()
    print(f"\n===== {rel} ({len(d)} bytes) =====")
    ss=strings(d,4)
    for off,s in ss:
        if len(s)>=4 and len(s)<120:
            print(f"  @{off}: {s.decode('latin1')}")
