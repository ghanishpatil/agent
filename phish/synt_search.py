#!/usr/bin/env python3
import os, re, codecs
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish"

# search ALL files (whole phish tree incl zip, extracted, macosx) for 'synt' or 'SYNT' occurrences
for dp,_,fs in os.walk(ROOT):
    if "\\phish\\" not in dp+"\\" and dp!=ROOT: pass
    for fn in fs:
        if fn.endswith(".py"): continue
        p=os.path.join(dp,fn)
        try: d=open(p,"rb").read()
        except: continue
        for kw in [b"synt",b"SYNT",b"Synt"]:
            i=0
            while True:
                j=d.find(kw,i)
                if j<0: break
                ctx=d[max(0,j-10):j+40]
                asc="".join(chr(x) if 32<=x<127 else "." for x in ctx)
                print(f"  {os.path.relpath(p,ROOT)} @{j}: ...{asc}...  -> rot13({kw.decode()})={codecs.encode(kw.decode(),'rot13')}")
                i=j+1
print("done")
