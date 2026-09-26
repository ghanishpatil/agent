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

def parse(rec):
    tl=(rec[6]<<8)|rec[5]
    crc_ok = crc16(rec,tl-2)==((rec[tl-2]<<8)|rec[tl-1])
    d={}
    esi=8
    while esi+2<=tl-2:
        code=rec[esi]; cnt=rec[esi+1]; payload=bytes(rec[esi+2:esi+2+cnt])
        idx=BYTE2IDX.get(code)
        if idx is not None: d[MODS[idx]]=payload
        esi=esi+2+cnt
    return crc_ok, d

recs=[]
for f in sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.r9cf')):
    rec=open(f,'rb').read()
    ok,d=parse(rec)
    recs.append((os.path.basename(f),ok,d))

# Print a table: for each module, show value per record
mods_order=MODS
print("record         crc  " + " ".join(f"{m:>8}" for m in ['o4','da','cf','mh','ds','c7','c8','x3','o3','g8','lc','ml']))
for nm,ok,d in recs:
    row=[]
    for m in ['o4','da','cf','mh','ds','c7','c8','x3','o3','g8','lc','ml']:
        row.append(d.get(m,b'').hex())
    print(f"{nm:14} {str(ok):5} " + " ".join(f"{v:>8}" for v in row))

print()
# Identify lane by o4/da: lane0 o4=803e0000 da=01 ; lane1 o4=50460000 da=02
print("Grouping by (o4,da):")
from collections import defaultdict
groups=defaultdict(list)
for nm,ok,d in recs:
    key=(d.get('o4',b'').hex(), d.get('da',b'').hex())
    groups[key].append((nm,ok,d))
for k,v in groups.items():
    print(f"  o4={k[0]} da={k[1]} : {[x[0] for x in v]}")

# For CRC-valid only
print("\nCRC-VALID records only:")
valid=[(nm,d) for nm,ok,d in recs if ok]
for nm,d in valid:
    print(f"  {nm}: o4={d.get('o4',b'').hex()} da={d.get('da',b'').hex()} cf={d.get('cf',b'').hex()} mh={d.get('mh',b'').hex()} g8={d.get('g8',b'').hex()} lc={d.get('lc',b'').hex()} ml={d.get('ml',b'').hex()} o3={d.get('o3',b'').hex()} c7={d.get('c7',b'').hex()} c8={d.get('c8',b'').hex()}")
