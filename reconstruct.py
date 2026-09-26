import struct
prof={
'002':{0:'c86d6068',1:'50460000',4:'02',5:'08',6:'02',7:'02',8:'f7535567',11:'cc583f4d',12:'0002',13:'1b37',14:'40c8cc59',16:'fb4eea48'},
'006':{0:'951fa507',1:'50460000',4:'02',5:'08',6:'02',7:'02',8:'f7535567',11:'cc583f4d',12:'0002',13:'1c37',14:'990bdb03',16:'fb4eea48'},
'008':{0:'68f089df',1:'50460000',4:'02',5:'08',6:'02',7:'02',8:'f7535567',11:'58804bc5',12:'0002',13:'ec3e',14:'990bdb03',16:'5e14b0ed'},
'003':{0:'55249ec5',1:'803e0000',4:'01',5:'07',6:'01',7:'01',8:'a68d20eb',11:'cc583f4d',12:'0102',13:'1b37',14:'24ebc118',16:'fb4eea48'},
'009':{0:'cb0cf9e7',1:'803e0000',4:'01',5:'07',6:'01',7:'01',8:'a68d20eb',11:'58804bc5',12:'0102',13:'ec3e',14:'fd28d642',16:'5e14b0ed'},
'010':{0:'560d9fde',1:'803e0000',4:'01',5:'07',6:'01',7:'01',8:'a68d20eb',11:'cc583f4d',12:'0102',13:'1c37',14:'fd28d642',16:'fb4eea48'},
}
A=['002','006','008']  # slot1=18000
B=['003','009','010']  # slot1=16000

# GF(256) shamir
def gfmul(a,b):
    p=0
    for _ in range(8):
        if b&1: p^=a
        hi=a&0x80; a=(a<<1)&0xff
        if hi: a^=0x1b
        b>>=1
    return p
def lagrange0(points):
    # points: list of (x, ybyte)
    secret=0
    for i,(xi,yi) in enumerate(points):
        num=1;den=1
        for j,(xj,yj) in enumerate(points):
            if i==j:continue
            num=gfmul(num,xj)
            den=gfmul(den,xi^xj)
        # inverse of den
        inv=1
        for _ in range(254): inv=gfmul(inv,den)
        secret^=gfmul(yi,gfmul(num,inv))
    return secret

def group_words(grp):
    # collect the varying data slots as candidate share values
    return grp

# XOR of slot14 across a group (7 bytes? no, 4 bytes)
for label,grp in [('A',A),('B',B)]:
    for slot in [8,11,13,14,16]:
        vals=[bytes.fromhex(prof[p][slot]) for p in grp]
        n=min(len(v) for v in vals)
        x=bytearray(n)
        for v in vals:
            for i in range(n): x[i]^=v[i]
        print(f'group{label} slot{slot} XOR = {bytes(x).hex()}')
    print()

# Try: within group, treat (slot0 as x? no). Use x=1,2,3 by order; y = each byte of slot14
print('--- Shamir per group on slot14 bytes (x=1,2,3) ---')
for label,grp in [('A',A),('B',B)]:
    words=[bytes.fromhex(prof[p][14]) for p in grp]
    secret=bytes(lagrange0([(i+1,w[k]) for i,w in enumerate(words)]) for k in range(4))
    print(f'group{label} slot14 shamir secret = {secret.hex()}')
