import re, os
d=r'f:\mission-git-hackss\mission-git-hackss\blobs'
for n in sorted(os.listdir(d)):
    if not n.endswith('.residue'): continue
    res=open(os.path.join(d,n),'rb').read()
    # residue tail
    tail=res[-80:]
    ss=re.findall(rb'[ -~]{4,}',res)
    print(n, 'len',len(res))
    print('  tail:',tail.hex())
    for s in ss:
        if not s.startswith(b'HTF{r9_'):
            print('   str:',s)
