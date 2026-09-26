import os, re, glob
targets = [os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')]
targets += glob.glob('tp_files/*')

pat = re.compile(rb'HTF\{[^}]{0,60}\}')
seen={}
for t in targets:
    data=open(t,'rb').read()
    for m in pat.finditer(data):
        s=m.group().decode('latin1')
        seen.setdefault(s, []).append((os.path.basename(t), m.start()))

# categorize
r9=[s for s in seen if s.startswith('HTF{r9_')]
other=[s for s in seen if not s.startswith('HTF{r9_')]
print(f'total distinct HTF{{}} = {len(seen)}')
print(f'  r9_ decoys: {len(r9)}')
print(f'  NON-r9 / unusual: {len(other)}')
for s in other:
    print('   *', s, '->', seen[s][:3])
# show any r9_ that appear only ONCE (unique might = real) vs many
from collections import Counter
print('\nr9_ occurrence counts (looking for a unique one):')
cnt = {s: len(v) for s,v in seen.items() if s.startswith('HTF{r9_')}
for s,c in sorted(cnt.items(), key=lambda x:x[1])[:10]:
    print(f'   {c:3}x  {s}')
