#!/usr/bin/env python3
import zlib, gzip, io
GIF = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"
d=open(GIF,"rb").read()
# try the two gzip candidate offsets
for off in [50140,55425]:
    print(f"\n=== gzip candidate @{off}: {d[off:off+16].hex()} ===")
    try:
        dec=gzip.decompress(d[off:])
        print("  gzip OK, len",len(dec), dec[:120])
    except Exception as e:
        print("  gzip fail:",e)
    # raw deflate after 2-byte magic?
    for skip in (0,2,10):
        try:
            dec=zlib.decompressobj(-15).decompress(d[off+skip:off+skip+40000])
            if len(dec)>4:
                pr="".join(chr(c) if 32<=c<127 else "." for c in dec[:120])
                print(f"  raw-deflate skip{skip}: len{len(dec)} {pr}")
        except Exception as e:
            pass

# also try zlib on whole tail from various offsets looking for printable
# and check the two BM offsets for a real BMP header
for off in [71150,144940]:
    hdr=d[off:off+14]
    print(f"\nBM @{off}: {hdr.hex()}  size field={int.from_bytes(hdr[2:6],'little')}")
