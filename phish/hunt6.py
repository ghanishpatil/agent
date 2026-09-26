#!/usr/bin/env python3
import struct
P1 = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\printerSettings\printerSettings1.bin"
GIF= r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"

d=open(P1,"rb").read()
print("=== printerSettings1 hexdump around 200-280 ===")
for i in range(192,288,16):
    ch=d[i:i+16]; asc="".join(chr(x) if 32<=x<127 else "." for x in ch)
    print(f"  {i}: {ch.hex()}  {asc}")

# GIF palette LSB
g=open(GIF,"rb").read()
pal=g[13:13+768]  # 256*3
bits=[]
for byte in pal:
    bits.append(byte&1)
# pack bits into bytes (msb first and lsb first)
def frombits(bits, msb=True):
    out=bytearray()
    for i in range(0,len(bits)-7,8):
        v=0
        for j in range(8):
            b=bits[i+j]
            if msb: v=(v<<1)|b
            else: v |= b<<j
        out.append(v)
    return bytes(out)
for msb in (True,False):
    s=frombits(bits,msb)
    printable="".join(chr(c) if 32<=c<127 else "." for c in s)
    print(f"\npalette LSB (msb={msb}): {printable}")
