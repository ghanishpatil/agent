#!/usr/bin/env python3
import struct, re
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
data=open(BIN,'rb').read()
e_shoff=struct.unpack_from("<Q",data,40)[0]; e_shent=struct.unpack_from("<H",data,58)[0]; e_shnum=struct.unpack_from("<H",data,60)[0]
# rodata 0x483000 off 0x83000 size 0x1c584
ro_off=0x83000; ro_size=0x1c584; ro_va=0x483000
ro=data[ro_off:ro_off+ro_size]
print("=== interesting rodata strings ===")
for m in re.finditer(rb"[\x20-\x7e]{4,}", ro):
    s=m.group()
    low=s.lower()
    if any(k in low for k in [b"flag",b"atlas",b"session",b"case",b"result",b"verdict",b"malic",b"anon",b"image",b"page",b"exec",b"cache",b"signature",b"context",b"scrub",b"node",b"quarant",b"deny",b"deni",b"complete",b"worker",b"ready",b"config"]):
        print(f"  0x{ro_va+m.start():x}: {s.decode('latin1')}")
