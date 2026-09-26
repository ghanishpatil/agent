#!/usr/bin/env python3
from PIL import Image
import numpy as np, re
GIF = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"

im=Image.open(GIF)
idx=np.array(im)  # palette indices
print("index array shape",idx.shape,"unique",sorted(np.unique(idx))[:20],"...count",len(np.unique(idx)))

def bits2bytes(bits, msb=True):
    out=bytearray()
    for i in range(0,len(bits)//8*8,8):
        v=0
        for j in range(8):
            v=(v<<1)|bits[i+j] if msb else (v|(bits[i+j]<<j))
        out.append(v)
    return bytes(out)

flat=idx.flatten()
# check for a region where indices encode ASCII directly (e.g. flag drawn as index values)
# scan for 'flag'/'FLAG' as raw index bytes
raw=flat.astype(np.uint8).tobytes()
for kw in [b"flag",b"FLAG",b"{",b"CTF"]:
    i=raw.find(kw)
    if i>=0:
        print(f"raw index find {kw}: @{i} -> {raw[i:i+40]}")

# LSB of indices, row-major, both bit orders, look for printable run
lsb=(flat&1)
for msb in (True,False):
    b=bits2bytes(lsb.tolist(),msb)
    txt="".join(chr(c) if 32<=c<127 else "." for c in b[:200])
    if "flag" in txt.lower() or "FLAG" in txt or "CTF" in txt:
        print(f"LSB msb={msb}: {txt}")

# Now RGB LSB
rgb=np.array(im.convert("RGB"))
for ch in range(3):
    plane=rgb[:,:,ch].flatten()&1
    for msb in (True,False):
        b=bits2bytes(plane.tolist(),msb)
        txt="".join(chr(c) if 32<=c<127 else "." for c in b[:300])
        if "flag" in txt.lower() or "FLAG" in txt or "CTF{" in txt:
            print(f"RGB ch{ch} LSB msb={msb}: {txt[:120]}")

# palette full ascii
pal=bytes(im.getpalette() or b"")
pt="".join(chr(c) if 32<=c<127 else "." for c in pal)
print("palette ascii sample:", pt[:200])
print("done")
