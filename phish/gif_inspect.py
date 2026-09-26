#!/usr/bin/env python3
from PIL import Image
import numpy as np, re
GIF = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"
im=Image.open(GIF).convert("RGB")
arr=np.array(im)
print("size",im.size,"colors used")
# downscale to see if text is visible; save a small thumbnail and describe
im.save(r"f:\mission-git-hackss\mission-git-hackss\phish\image_render.png")
# Also: scan whole gif file for embedded signatures at any offset
d=open(GIF,"rb").read()
sigs={b"PK\x03\x04":"zip",b"\x89PNG":"png",b"\xff\xd8\xff":"jpg",b"BM":"bmp",b"Rar!":"rar",
      b"7z\xbc\xaf\x27\x1c":"7z",b"%PDF":"pdf",b"ID3":"mp3",b"\x1f\x8b":"gzip",b"BZh":"bzip2",
      b"FLAG":"flag",b"flag":"flag"}
for sig,name in sigs.items():
    idx=0
    while True:
        i=d.find(sig,idx)
        if i<0: break
        # ignore the GIF's own header
        print(f"  sig {name} @ {i}")
        idx=i+1
        if idx>len(d): break
print("saved render to image_render.png")
