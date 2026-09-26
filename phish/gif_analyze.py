#!/usr/bin/env python3
import struct, re, codecs
GIF = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\media\image1.gif"
d=open(GIF,"rb").read()
print(f"size={len(d)} header={d[:6]}")
w,h=struct.unpack_from("<HH",d,6)
flags=d[10]
gct = bool(flags&0x80)
gct_size = 2**((flags&7)+1)
print(f"w={w} h={h} gct={gct} gct_size={gct_size}")
pos=13
if gct: pos += 3*gct_size

comments=[]
app=[]
def read_subblocks(p):
    data=bytearray()
    while p<len(d):
        n=d[p]; p+=1
        if n==0: break
        data+=d[p:p+n]; p+=n
    return bytes(data), p

while pos < len(d):
    b=d[pos]
    if b==0x21:  # extension
        label=d[pos+1]; pos+=2
        blk,pos=read_subblocks(pos)
        if label==0xFE:
            comments.append(blk)
            print(f"[COMMENT ext] {blk[:200]!r}")
        elif label==0xFF:
            print(f"[APP ext] id={blk[:11]!r} rest={blk[11:80]!r}")
        elif label==0xF9:
            pass # graphic control
        elif label==0x01:
            print(f"[PLAINTEXT ext] {blk[:120]!r}")
        else:
            print(f"[ext 0x{label:02x}] {blk[:80]!r}")
    elif b==0x2C:  # image descriptor
        # skip: 9 bytes descriptor
        lct_flags=d[pos+9]
        p2=pos+10
        if lct_flags&0x80:
            p2+=3*(2**((lct_flags&7)+1))
        # LZW min code size
        p2+=1
        _,p2=read_subblocks(p2)
        pos=p2
    elif b==0x3B:
        print("[trailer]"); break
    else:
        pos+=1

# rot13/plain flag in comments
for c in comments:
    print("comment rot13:", codecs.encode(c.decode('latin1','replace'),'rot13')[:200])
