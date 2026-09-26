#!/usr/bin/env python3
import re
GIF = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"
XLSM= r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\Phishtofortune.xlsm"

def strings(path, minlen=6):
    d=open(path,"rb").read()
    out=[]
    for m in re.finditer(rb"[\x20-\x7e]{%d,}"%minlen, d):
        out.append((m.start(), m.group()))
    return out, d

for name,path in [("GIF",GIF),("XLSM",XLSM)]:
    ss,d=strings(path,7)
    print(f"\n===== {name} strings (len>=7), filtered for 'interesting' =====")
    for off,s in ss:
        txt=s.decode("latin1")
        # skip pure hex/base64 junk and known xml
        if re.fullmatch(r"[A-Za-z0-9+/=]{7,}", txt) and len(set(txt))<6: continue
        # show anything with letters that looks wordlike or has punctuation typical of flags
        if re.search(r"[A-Za-z]{4,}", txt) and not txt.startswith("http://schemas"):
            # limit noise: show if contains _ { } or capital patterns or looks like a sentence
            if any(c in txt for c in "_{}!") or " " in txt or re.search(r"[A-Z][a-z]{3,}", txt):
                print(f"  @{off}: {txt[:100]}")
