prof={
'002':{0:'c86d6068',8:'f7535567',11:'cc583f4d',13:'1b37',14:'40c8cc59',16:'fb4eea48',12:'0002',1:'50460000'},
'006':{0:'951fa507',8:'f7535567',11:'cc583f4d',13:'1c37',14:'990bdb03',16:'fb4eea48',12:'0002',1:'50460000'},
'008':{0:'68f089df',8:'f7535567',11:'58804bc5',13:'ec3e',14:'990bdb03',16:'5e14b0ed',12:'0002',1:'50460000'},
'003':{0:'55249ec5',8:'a68d20eb',11:'cc583f4d',13:'1b37',14:'24ebc118',16:'fb4eea48',12:'0102',1:'803e0000'},
'009':{0:'cb0cf9e7',8:'a68d20eb',11:'58804bc5',13:'ec3e',14:'fd28d642',16:'5e14b0ed',12:'0102',1:'803e0000'},
'010':{0:'560d9fde',8:'a68d20eb',11:'cc583f4d',13:'1c37',14:'fd28d642',16:'fb4eea48',12:'0102',1:'803e0000'},
}
allp=list(prof)

def blk(p, order):
    return b''.join(bytes.fromhex(prof[p][s]) for s in order)

def xorall(blocks):
    n=min(len(b) for b in blocks); o=bytearray(n)
    for b in blocks:
        for i in range(n): o[i]^=b[i]
    return bytes(o)

for order in [[8,11,13,14],[8,11,14,13],[8,11,14,16,13],[0,8,11,14],[8,11,16,13]]:
    blocks=[blk(p,order) for p in allp]
    if len(set(len(b) for b in blocks))==1 and len(blocks[0]) in (14,16,18):
        x=xorall(blocks)
        print(f'order {order} len{len(x)} XOR6 = {x.hex()}')

# GF256 shamir with x = profile order index 1..6 and y=each byte of the 14-byte block
def gfmul(a,b):
    p=0
    for _ in range(8):
        if b&1:p^=a
        h=a&0x80;a=(a<<1)&0xff
        if h:a^=0x1b
        b>>=1
    return p
def gfinv(a):
    r=1
    for _ in range(254): r=gfmul(r,a)
    return r
def lag0(pts):
    s=0
    for i,(xi,yi) in enumerate(pts):
        num=1;den=1
        for j,(xj,yj) in enumerate(pts):
            if i==j:continue
            num=gfmul(num,xj); den=gfmul(den,xi^xj)
        s^=gfmul(yi,gfmul(num,gfinv(den)))
    return s

order=[8,11,13,14]
blocks=[blk(p,order) for p in allp]
# x-coordinate candidates: 1..6, or low byte of slot0
for xmode in ['1..6','slot0lo','slot12']:
    if xmode=='1..6': xs=[1,2,3,4,5,6]
    elif xmode=='slot0lo': xs=[bytes.fromhex(prof[p][0])[-1] for p in allp]
    else: xs=[bytes.fromhex(prof[p][12])[-1] for p in allp]
    if len(set(xs))<len(xs): 
        print('xmode',xmode,'dup x, skip', xs); continue
    secret=bytes(lag0([(xs[i],blocks[i][k]) for i in range(6)]) for k in range(14))
    print(f'shamir x={xmode} secret={secret.hex()}')
