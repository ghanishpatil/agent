#!/usr/bin/env python3
from PIL import Image, ImageSequence
import numpy as np
GIF = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"
im = Image.open(GIF)
print("format",im.format,"mode",im.mode,"size",im.size)
frames=list(ImageSequence.Iterator(im))
print("n_frames",len(frames))

def bits_to_bytes(bits):
    out=bytearray()
    for i in range(0,len(bits)-7,8):
        v=0
        for j in range(8): v=(v<<1)|bits[i+j]
        out.append(v)
    return bytes(out)

for fi,fr in enumerate(frames[:3]):
    arr=np.array(fr)  # indexed values (mode P)
    print(f"\nframe {fi}: shape={arr.shape} dtype={arr.dtype} unique={len(np.unique(arr))}")
    flat=arr.flatten()
    # LSB of index values, both bit orders
    lsb=(flat&1).tolist()
    for order,seq in [("msb",lsb),("lsb-first",lsb)]:
        b=bits_to_bytes(seq)
        txt="".join(chr(c) if 32<=c<127 else "." for c in b[:120])
        if "flag" in txt.lower() or "FLAG" in txt or "{" in txt:
            print(f"  LSB {order}: {txt}")
    # first 200 index values printable?
    s="".join(chr(c) if 32<=c<127 else "." for c in flat[:200])
    # palette
    pal=fr.getpalette()
    if pal:
        pb=bytes(pal)
        # print any ascii in palette
        pt="".join(chr(c) if 32<=c<127 else "." for c in pb)
        if "flag" in pt.lower(): print("  palette ascii has flag:", pt)

# Also: raw index-value ASCII (top-left rows) — sometimes text drawn as pixel indices
arr=np.array(frames[0]).flatten()
raw="".join(chr(c) if 32<=c<127 else "" for c in arr[:5000])
if "flag" in raw.lower():
    i=raw.lower().find("flag"); print("RAW INDEX ASCII flag:", raw[i:i+80])
print("done")
