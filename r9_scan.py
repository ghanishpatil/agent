import os,re
img=open(os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img'),'rb').read()
# count HTF{r9_ decoys
decoys=re.findall(rb'HTF\{r9_[0-9a-fA-F_]{0,40}\}',img)
print('total HTF{r9_ occurrences in img:',len(decoys),'unique:',len(set(decoys)))
# sample a few decoys
for d in list(set(decoys))[:15]:
    print('  decoy:',d.decode('latin1'))
# check hex-length distribution of decoys
from collections import Counter
lens=Counter(len(d)-len(b'HTF{r9_}') for d in set(decoys))
print('decoy inner-length hist:',dict(lens))
# Any 28-hex-char ones?
h28=[d for d in set(decoys) if re.fullmatch(rb'HTF\{r9_[0-9a-f]{28}\}',d)]
print('28-hex-lowercase decoys:',len(h28))
# search for my candidate raw byte blobs
cands={
 'rec8_cf_g8_mh_ml':bytes.fromhex('f753556758804bc5ec3e990bdb03'),
 'rec9_cf_g8_mh_ml':bytes.fromhex('a68d20eb58804bc5ec3efd28d642'),
 'cr':bytes.fromhex('e2aa95907ea02d1a'),
}
for n,b in cands.items():
    print(f'blob {n} ({b.hex()}) appears {img.count(b)} times in img')
