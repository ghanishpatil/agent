import struct, re
exec(open(r'f:\mission-git-hackss\mission-git-hackss\ext4parse.py').read().split('parse_dir(2')[0])

# journal is inode 8
raw=read_inode(8)
size=inode_size_bytes(raw)
print('journal size', size)
jdata=read_file(8)
print('journal bytes', len(jdata))
open(r'f:\mission-git-hackss\mission-git-hackss\journal.bin','wb').write(jdata)

# search journal for flags and interesting text
flags=re.findall(rb'HTF\{[^}]{0,120}\}', jdata)
from collections import Counter
print('flags in journal total', len(flags), 'unique', len(set(flags)))
for f in set(flags):
    if not f.startswith(b'HTF{r9_'):
        print('NON-R9 in journal:', f)

# look for interesting keywords in journal
for kw in [b'rollout',b'lane',b'slot',b'module',b'flag',b'HTF',b'guard',b'accept',b'generation',b'cadence',b'.cal',b'legacy']:
    idxs=[m.start() for m in re.finditer(re.escape(kw), jdata)]
    print(kw, 'count', len(idxs))
