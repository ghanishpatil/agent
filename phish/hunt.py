#!/usr/bin/env python3
import os, re, codecs, base64
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune"

def ascii_strings(data, minlen=4):
    return re.findall(rb"[\x20-\x7e]{%d,}" % minlen, data)

def rot13(s): return codecs.encode(s, "rot13")

flag_pats = [re.compile(rb"FLAG\{[^}]{1,120}\}", re.I),
             re.compile(rb"synt\{", re.I)]

for dirpath,_,files in os.walk(ROOT):
    for fn in files:
        p=os.path.join(dirpath,fn)
        try:
            data=open(p,"rb").read()
        except: continue
        rel=os.path.relpath(p,ROOT)
        # direct flag search
        for pat in flag_pats:
            for m in pat.finditer(data):
                print(f"[FLAG?] {rel}: {m.group()!r}")
        # search strings, then rot13 each, look for flag{
        for s in ascii_strings(data,4):
            try: r=rot13(s)
            except: continue
            if b"flag{" in r.lower() or b"FLAG{" in r:
                print(f"[ROT13] {rel}: {s!r} -> {r!r}")
        # base64 decode candidates containing 'flag'
        for m in re.finditer(rb"[A-Za-z0-9+/]{16,}={0,2}", data):
            tok=m.group()
            try:
                dec=base64.b64decode(tok+b"="*((4-len(tok)%4)%4))
                if b"flag{" in dec.lower() or b"FLAG{" in dec:
                    print(f"[B64] {rel}: {tok[:40]!r} -> {dec[:80]!r}")
            except: pass
print("done")
