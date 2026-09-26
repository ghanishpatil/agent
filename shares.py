import glob, os
# XOR all recovered record bodies together
blobs={}
for f in sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.r9cf')):
    name=os.path.basename(f).replace('.r9cf','')
    blobs[name]=open(f,'rb').read()

accepted=['r9-retired-002','r9-retired-003','r9-retired-006','r9-retired-008','r9-retired-009','r9-retired-010']

def xorall(datas):
    n=min(len(d) for d in datas)
    out=bytearray(n)
    for d in datas:
        for i in range(n):
            out[i]^=d[i]
    return bytes(out)

# XOR full 98-byte blobs of accepted
x=xorall([blobs[a] for a in accepted])
print('XOR accepted blobs (98B):', x.hex())
print('  printable:', ''.join(chr(c) if 32<=c<127 else '.' for c in x))

# XOR record bodies (skip 7-byte header, drop 2-byte crc)
bodies=[blobs[a][7:-2] for a in accepted]
xb=xorall(bodies)
print('XOR bodies:', xb.hex())

# The two groups A/B
A=['r9-retired-002','r9-retired-006','r9-retired-008']
B=['r9-retired-003','r9-retired-009','r9-retired-010']
print('XOR group A bodies:', xorall([blobs[a][7:-2] for a in A]).hex())
print('XOR group B bodies:', xorall([blobs[a][7:-2] for a in B]).hex())
