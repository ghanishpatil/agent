import glob, os, struct

key=bytes.fromhex('e2aa95907ea02d1a')

def rc4(key,data):
    S=list(range(256)); j=0
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])&0xff; S[i],S[j]=S[j],S[i]
    i=j=0; out=bytearray()
    for b in data:
        i=(i+1)&0xff; j=(j+S[i])&0xff; S[i],S[j]=S[j],S[i]
        out.append(b^S[(S[i]+S[j])&0xff])
    return bytes(out)

def find(data,label):
    if b'HTF' in data or b'htf' in data:
        idx=data.find(b'HTF')
        print(f'  !!! {label} HTF at {idx}: {data[idx:idx+40]}')
        return True
    return False

# also try keys: slot8 words, slot18, build hash
keys={
 'slot9':bytes.fromhex('e2aa95907ea02d1a'),
 'slot9rev':bytes.fromhex('e2aa95907ea02d1a')[::-1],
 'build':bytes.fromhex('6c52b90c2f26da3a6a55'),
}

for f in sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.residue')):
    res=open(f,'rb').read()
    name=os.path.basename(f)
    for kn,k in keys.items():
        d=rc4(k,res)
        if find(d,f'{name} RC4 {kn}'): pass
        # xor keystream (repeat key)
        x=bytes(res[i]^k[i%len(k)] for i in range(len(res)))
        if find(x,f'{name} XOR {kn}'): pass
    # also blob
print('done residue scan')

# try blob bodies too
for f in sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.r9cf')):
    b=open(f,'rb').read()
    name=os.path.basename(f)
    for kn,k in keys.items():
        d=rc4(k,b)
        find(d,f'{name} RC4 {kn}')
        d2=rc4(k,b[7:-2])
        find(d2,f'{name} body RC4 {kn}')
print('done blob scan')
