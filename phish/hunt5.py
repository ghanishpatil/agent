#!/usr/bin/env python3
import re, base64, binascii, codecs
XLSM = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\Phishtofortune.xlsm"
GIF  = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"

xd=open(XLSM,"rb").read()
# ZIP EOCD: find end of central directory, check for trailing bytes after it
eocd=xd.rfind(b"PK\x05\x06")
if eocd>=0:
    # EOCD is 22 bytes + comment length
    clen=int.from_bytes(xd[eocd+20:eocd+22],"little")
    end=eocd+22+clen
    print(f"EOCD at {eocd}, comment len={clen}, file size={len(xd)}, trailing after EOCD+comment={len(xd)-end}")
    if len(xd)-end>0:
        print("TRAILING:", xd[end:end+200])
    if clen>0:
        print("ZIP COMMENT:", xd[eocd+22:eocd+22+clen])

def transforms(tok):
    res={}
    try: res["rev"]=tok[::-1]
    except: pass
    try: res["rot13"]=codecs.encode(tok.decode('latin1'),'rot13').encode()
    except: pass
    try: res["hex"]=binascii.unhexlify(tok) if re.fullmatch(rb"[0-9a-fA-F]+",tok) and len(tok)%2==0 else None
    except: pass
    try: res["b32"]=base64.b32decode(tok+b"="*((8-len(tok)%8)%8)) if re.fullmatch(rb"[A-Z2-7]+",tok) else None
    except: pass
    return res

def scan(name, d):
    # apply transforms on every ascii run, look for FLAG{/flag{
    for m in re.finditer(rb"[\x20-\x7e]{6,}", d):
        tok=m.group()
        low=tok.lower()
        if b"flag{" in low: print(f"[{name} DIRECT] @{m.start()}: {tok!r}")
        for k,v in transforms(tok).items():
            if v and (b"flag{" in v.lower() or b"FLAG{" in v):
                print(f"[{name} {k}] {tok[:40]!r} -> {v[:80]!r}")

scan("xlsm", xd)
scan("gif", open(GIF,"rb").read())
print("done")
