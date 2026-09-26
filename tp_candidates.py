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
    d={}; order=[]
    esi=8
    while esi+2<=tl-2:
        code=rec[esi]; cnt=rec[esi+1]; payload=bytes(rec[esi+2:esi+2+cnt])
        idx=BYTE2IDX.get(code)
        if idx is not None:
            d[MODS[idx]]=payload; order.append(MODS[idx])
        esi=esi+2+cnt
    return crc_ok, d, order

recs={}
for f in sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.r9cf')):
    rec=open(f,'rb').read()
    ok,d,order=parse(rec)
    recs[os.path.basename(f)]=(ok,d,order)

# newest gen = mh==ec3e, crc valid
lane0 = recs['r9-retired-009.r9cf'][1]  # da=01
lane1 = recs['r9-retired-008.r9cf'][1]  # da=02
print("lane0 (009):", {k:v.hex() for k,v in lane0.items()})
print("lane1 (008):", {k:v.hex() for k,v in lane1.items()})
print()

# Carriers that carry entropy (4-byte or 2-byte payloads that vary)
carriers = ['o3','o4','cf','cr','g8','ml','lc','mh']
print("Per-carrier lane0 vs lane1 (newest gen):")
for c in carriers:
    print(f"  {c}: lane0={lane0.get(c,b'').hex():<18} lane1={lane1.get(c,b'').hex()}")
print()

def show(label, b):
    try:
        s=b.decode('ascii')
        printable = all(32<=x<127 for x in b)
    except:
        s=None; printable=False
    print(f"  {label}: {b.hex()}  ascii={'|'+''.join(chr(x) if 32<=x<127 else '.' for x in b)+'|'}")

# Candidate assembly strategies
print("=== Candidates ===")
# The known-wrong: cf|g8|mh|ml of lane0
wrong = lane0['cf']+lane0['g8']+lane0['mh']+lane0['ml']
print("KNOWN WRONG (009 cf|g8|mh|ml):", 'HTF{r9_'+wrong.hex()+'}')
print()

# candidate: interleave lanes. cf carries lane identity. Try lane0 then lane1 for each carrier
for combo in [
    ('cf g8 mh ml both', lambda: lane0['cf']+lane1['cf']+lane0['g8']+lane1['g8']+lane0['mh']+lane1['mh']+lane0['ml']+lane1['ml']),
    ('lane0 all-carrier o3o4cfcrg8mllc', lambda: b''.join(lane0[c] for c in ['o3','o4','cf','cr','g8','ml','lc'])),
    ('lane1 all-carrier', lambda: b''.join(lane1[c] for c in ['o3','o4','cf','cr','g8','ml','lc'])),
    ('cr both', lambda: lane0['cr']+lane1['cr']),
]:
    name,fn=combo
    try:
        b=fn()
        print(f"{name}: HTF{{r9_{b.hex()}}}  (len {len(b)})")
    except Exception as e:
        print(name,"err",e)
