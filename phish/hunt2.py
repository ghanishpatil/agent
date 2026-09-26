#!/usr/bin/env python3
import os, re
ROOT = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune"
GIF = os.path.join(ROOT,"Phishtofortune","xl","media","image1.gif")
XLSM= os.path.join(ROOT,"Phishtofortune","Phishtofortune.xlsm")

# 1) GIF: check for trailing data after GIF trailer 0x3B
data=open(GIF,"rb").read()
print(f"GIF size={len(data)} header={data[:6]}")
# find last 0x3B (trailer). GIF ends with 0x3B; anything after is appended
last=data.rfind(b"\x3b")
print(f"last 0x3B at {last} (size-1={len(data)-1}); trailing bytes={len(data)-1-last}")
# show tail
print("GIF tail (last 64 bytes):", data[-64:])
# look for embedded zip/PK, PNG, flag
for sig,name in [(b"PK\x03\x04","ZIP"),(b"\x89PNG","PNG"),(b"Rar!","RAR"),(b"7z\xbc\xaf","7z"),(b"FLAG",""),(b"flag","")]:
    i=data.find(sig)
    if i>=0: print(f"  found {name or sig} at {i}")

# 2) any FLAG-ish in whole tree with wider charset & reversed
import codecs
def strings(d,m=4): return re.findall(rb"[\x20-\x7e]{%d,}"%m, d)
print("\n=== interesting strings across tree (contain { or flag/synt/key/secret) ===")
for dp,_,fs in os.walk(ROOT):
    for fn in fs:
        p=os.path.join(dp,fn); rel=os.path.relpath(p,ROOT)
        try: d=open(p,"rb").read()
        except: continue
        for s in strings(d,5):
            low=s.lower()
            if (b"{" in s and b"}" in s) or b"flag" in low or b"synt" in low or b"secret" in low or b"key" in low or b"pass" in low:
                if len(s)<200:
                    print(f"  {rel}: {s!r}")
