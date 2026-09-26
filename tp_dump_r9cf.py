import os, glob

M32=0xffffffff
MODS="o3 o4 o5 dx da ds c7 c8 cf cr sn g8 x3 mh ml xs lc zl bz xz".split()
BYTE2IDX={0x22:8,0x31:2,0x35:10,0x38:1,0x3a:12,0x3c:9,0x46:17,0x49:4,0x6b:6,
 0x6d:14,0x84:3,0x90:11,0x9d:0,0xa9:7,0xc0:18,0xc1:16,0xd2:5,0xd3:19,0xd4:13,0xd5:15}

def crc16(buf,n):
    c=0xffffffff
    for i in range(n):
        c=(c^((buf[i]<<8)&M32))&M32
        for _ in range(8):
            two=(c*2)&M32
            c=two if (c&0x8000)==0 else (two^0x1021)&M32
    return c&0xffff

def parse_record(rec):
    """Return dict of module_name -> payload bytes, and list of (code,idx,module,count,payload) in order."""
    tl=(rec[6]<<8)|rec[5]
    crc_ok = crc16(rec,tl-2)==((rec[tl-2]<<8)|rec[tl-1])
    entries=[]
    esi=8
    while esi+2<=tl-2:
        code=rec[esi]; cnt=rec[esi+1]
        payload=rec[esi+2:esi+2+cnt]
        idx=BYTE2IDX.get(code)
        mod=MODS[idx] if idx is not None else f"?{code:02x}"
        entries.append((code,idx,mod,cnt,bytes(payload)))
        esi=esi+2+cnt
    return tl, crc_ok, entries

def dump(name, rec):
    tl,crc_ok,entries=parse_record(rec)
    print(f"--- {name} len_declared={tl} actual={len(rec)} crc_ok={crc_ok} ---")
    for code,idx,mod,cnt,payload in entries:
        asc=''.join(chr(b) if 32<=b<127 else '.' for b in payload)
        print(f"   code={code:02x} idx={idx} mod={mod:>3} cnt={cnt} payload={payload.hex():<26} |{asc}|")

# blobs
print("========== BLOB FILES ==========")
recs={}
for f in sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.r9cf')):
    rec=open(f,'rb').read()
    nm=os.path.basename(f)
    recs[nm]=rec
    dump(nm, rec)

# carve from image ALL R9CF including any not in blobs
print("\n========== IMAGE CARVE ==========")
img=open(r'f:\mission-git-hackss\mission-git-hackss\temporal_paradox\Temporal Paradox\gateway_snapshot.img','rb').read()
i=0; found=[]
seen=set()
while True:
    i=img.find(b'R9CF', i)
    if i<0: break
    tl=(img[i+6]<<8)|img[i+5]
    if 10<tl<=256 and i+tl<=len(img):
        rec=img[i:i+tl]
        if crc16(rec,tl-2)==((rec[tl-2]<<8)|rec[tl-1]):
            h=rec.hex()
            if h not in seen:
                seen.add(h)
                found.append((i,rec))
    i+=1
print(f"unique valid R9CF in image: {len(found)}")
for off,rec in found:
    dump(f"img@{off:#x}", rec)

# Which blob hashes are NOT in image and vice versa
blobhashes={r.hex() for r in recs.values()}
imghashes={r.hex() for _,r in found}
print("\nblob-only:", len(blobhashes-imghashes), "img-only:", len(imghashes-blobhashes))
