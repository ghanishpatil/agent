import struct, re, os
db=open(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db','rb').read()

def read_varint(b,o):
    res=0
    for i in range(9):
        c=b[o+i]
        if i==8: return (res<<8)|c, o+9
        res=(res<<7)|(c&0x7f)
        if not (c&0x80): return res,o+i+1
    return res,o+9
def serial_len(t):
    if t in (0,8,9): return 0
    if 1<=t<=4: return t
    if t==5: return 6
    if t in (6,7): return 8
    if t>=12: return (t-12)//2 if t%2==0 else (t-13)//2
    return 0

os.makedirs(r'f:\mission-git-hackss\mission-git-hackss\blobs',exist_ok=True)
rows={}
for m in re.finditer(rb'r9-retired-(\d{3})',db):
    labelpos=m.start(); labeltext=m.group(); L=len(labeltext)
    for hdr_start in range(labelpos-1,max(0,labelpos-40),-1):
        hlen,p=read_varint(db,hdr_start)
        if hlen<3 or hlen>12: continue
        types=[]; q=p; 
        try:
            while q<hdr_start+hlen:
                t,q=read_varint(db,q); types.append(t)
        except: continue
        if q!=hdr_start+hlen or len(types)!=4: continue
        body=hdr_start+hlen; slen0=serial_len(types[0])
        if body+slen0!=labelpos: continue
        if types[1]!=13+2*L: continue
        if types[2]<12 or types[2]%2 or types[3]<12 or types[3]%2: continue
        bl=serial_len(types[2]); rl=serial_len(types[3])
        blob=db[labelpos+L:labelpos+L+bl]
        residue=db[labelpos+L+bl:labelpos+L+bl+rl]
        rows[labeltext.decode()]=(blob,residue)
        break

for lab in sorted(rows):
    blob,res=rows[lab]
    n=lab.split('-')[-1]
    open(fr'f:\mission-git-hackss\mission-git-hackss\blobs\{lab}.r9cf','wb').write(blob)
    open(fr'f:\mission-git-hackss\mission-git-hackss\blobs\{lab}.residue','wb').write(res)
    print(lab,'blob',len(blob),'res',len(res),'blobhdr',blob[:8].hex())
print('done', len(rows))
