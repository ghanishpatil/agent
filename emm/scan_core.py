#!/usr/bin/env python3
"""Scan core LOAD segments for flag patterns, crypto keywords, base64, hex key material."""
import struct, re

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"

def read(p):
    with open(p,"rb") as f:
        return f.read()

def parse_phdrs(data):
    endian="<"
    e_phoff = struct.unpack_from(endian+"Q", data, 32)[0]
    e_phentsize = struct.unpack_from(endian+"H", data, 54)[0]
    e_phnum = struct.unpack_from(endian+"H", data, 56)[0]
    phdrs=[]
    for i in range(e_phnum):
        off=e_phoff+i*e_phentsize
        p_type,p_flags=struct.unpack_from(endian+"II",data,off)
        p_offset,p_vaddr,p_paddr,p_filesz,p_memsz,p_align=struct.unpack_from(endian+"QQQQQQ",data,off+8)
        phdrs.append(dict(type=p_type,offset=p_offset,vaddr=p_vaddr,filesz=p_filesz))
    return phdrs

def ascii_strings(buf, minlen=4):
    out=[]
    cur=bytearray()
    start=0
    for i,b in enumerate(buf):
        if 32<=b<127:
            if not cur: start=i
            cur.append(b)
        else:
            if len(cur)>=minlen:
                out.append((start,bytes(cur)))
            cur=bytearray()
    if len(cur)>=minlen:
        out.append((start,bytes(cur)))
    return out

def main():
    data=read(CORE)
    phdrs=parse_phdrs(data)
    loads=[ph for ph in phdrs if ph["type"]==1]

    # flag pattern
    print("=== flag{...} / HTF / HackTheFuture patterns ===")
    for ph in loads:
        seg=data[ph["offset"]:ph["offset"]+ph["filesz"]]
        for m in re.finditer(rb"(flag\{[^}]{0,120}\}|HTF\{[^}]{0,120}\}|FLAG\{[^}]{0,120}\})", seg):
            va=ph["vaddr"]+m.start()
            print(f"  @0x{va:x}: {m.group().decode('latin1')}")

    # crypto keywords
    print("\n=== crypto/interesting keywords ===")
    kws=[b"AES",b"aes",b"key",b"KEY",b"secret",b"SECRET",b"nonce",b"iv",b"IV",b"GCM",b"gcm",
         b"decrypt",b"encrypt",b"fragment",b"chacha",b"ChaCha",b"salsa",b"HMAC",b"sha256",
         b"case",b"authenticated",b"tag",b"cipher",b"malware",b"atlas",b"worker",b"context"]
    seen=set()
    for ph in loads:
        seg=data[ph["offset"]:ph["offset"]+ph["filesz"]]
        for s_off,s in ascii_strings(seg,5):
            for kw in kws:
                if kw in s:
                    va=ph["vaddr"]+s_off
                    key=(va,s)
                    if key in seen: continue
                    seen.add(key)
                    if len(s)<160:
                        print(f"  @0x{va:x}: {s.decode('latin1')}")
                    break

if __name__=="__main__":
    main()
