#!/usr/bin/env python3
import os, re, codecs
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune"

def strings(d,m=4): return re.findall(rb"[\x20-\x7e]{%d,}"%m, d)

# words that look like meaningful english after rot13 (heuristic: contains vowels, common substrings)
common = ["the","you","found","flag","key","secret","attack","payload","lemon","duck","phish","fortune","hidden","lock","down","hello","this","was","here","gotcha","congrat","well","done"]
seen=set()
for dp,_,fs in os.walk(ROOT):
    for fn in fs:
        p=os.path.join(dp,fn); rel=os.path.relpath(p,ROOT)
        try: d=open(p,"rb").read()
        except: continue
        for s in strings(d,4):
            try: txt=s.decode("latin1")
            except: continue
            r=codecs.encode(txt,"rot13").lower()
            for w in common:
                if w in r and s not in seen:
                    seen.add(s)
                    print(f"  {rel}: {txt!r} -> rot13 {codecs.encode(txt,'rot13')!r}")
                    break
print("done rot scan")
