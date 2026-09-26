import os, glob, struct

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
    d={}; order=[]
    esi=8
    while esi+2<=tl-2:
        code=rec[esi]; cnt=rec[esi+1]; payload=bytes(rec[esi+2:esi+2+cnt])
        idx=BYTE2IDX.get(code)
        if idx is not None: d[MODS[idx]]=payload; order.append((MODS[idx],code))
        esi=esi+2+cnt
    return crc_ok, d, order

recs={}
for f in sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.r9cf')):
    rec=open(f,'rb').read()
    recs[os.path.basename(f)]=parse(rec)

lane0=recs['r9-retired-009.r9cf'][1]
lane1=recs['r9-retired-008.r9cf'][1]

# The 4-byte carriers might be XORed lane0 ^ lane1 to reveal something (shared XOR)
print("=== XOR lane0 ^ lane1 per differing carrier ===")
for c in ['o3','o4','cf','ml']:
    a=lane0[c]; b=lane1[c]
    x=bytes(i^j for i,j in zip(a,b))
    print(f"  {c}: {a.hex()} ^ {b.hex()} = {x.hex()}  ascii={''.join(chr(v) if 32<=v<127 else '.' for v in x)}")

# o4 as int
print("\no4 lane0 LE:", struct.unpack('<I',lane0['o4'])[0], "BE:", struct.unpack('>I',lane0['o4'])[0])
print("o4 lane1 LE:", struct.unpack('<I',lane1['o4'])[0], "BE:", struct.unpack('>I',lane1['o4'])[0])

# cr is 8 bytes identical both lanes; g8,lc identical. These "shared" ones might be the actual flag body
# Try: the SHARED carriers (identical across lanes) = the real message; lane-specific = decoy
print("\n=== SHARED carriers (identical lane0==lane1) ===")
shared={}
for c in lane0:
    if c in lane1 and lane0[c]==lane1[c] and len(lane0[c])>=2:
        shared[c]=lane0[c]
for c,v in shared.items():
    print(f"  {c}: {v.hex()} ascii={''.join(chr(x) if 32<=x<127 else '.' for x in v)}")

# cr = e2aa95907ea02d1a. Try xor with things, or as flag hex
print("\ncr bytes:", lane0['cr'].hex())
# Maybe cr XOR g8 XOR lc?
print("cr:", lane0['cr'].hex())
print("g8+lc:", (lane0['g8']+lane0['lc']).hex())
# The candidate flag maybe: cr(8) + g8(4) = 12 bytes hex = 24 hex chars
print("\ncandidate cr|g8|lc:", 'HTF{r9_'+(lane0['cr']+lane0['g8']+lane0['lc']).hex()+'}')
