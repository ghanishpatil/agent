#!/usr/bin/env python3
import os, re, codecs
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune"

def strings(d,m=4): return re.findall(rb"[\x20-\x7e]{%d,}"%m, d)

# Any {....} braces content anywhere; also rot13 of any word containing 'synt' or 'flag'
brace = re.compile(rb"\{[\x20-\x7e]{2,80}\}")
for dp,_,fs in os.walk(ROOT):
    for fn in fs:
        p=os.path.join(dp,fn); rel=os.path.relpath(p,ROOT)
        try: d=open(p,"rb").read()
        except: continue
        for m in brace.finditer(d):
            g=m.group()
            # ignore common junk
            if g in (b"{{215, 0}, {920, 893}}",): continue
            r=codecs.encode(g.decode("latin1"),"rot13")
            print(f"  {rel}: {g!r}  rot13->{r!r}")
print("---- rot13 of tokens containing synt/flag ----")
for dp,_,fs in os.walk(ROOT):
    for fn in fs:
        p=os.path.join(dp,fn); rel=os.path.relpath(p,ROOT)
        try: d=open(p,"rb").read()
        except: continue
        for s in strings(d,4):
            low=s.lower()
            if b"synt" in low or b"flag" in low:
                print(f"  {rel}: {s!r} rot13->{codecs.encode(s.decode('latin1'),'rot13')!r}")
