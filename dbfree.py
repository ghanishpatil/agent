import re
db=open(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db','rb').read()
# find readable strings, look for algorithm hints / non-r9 flags / keywords
strings=re.findall(rb'[ -~]{6,}', db)
kws=[b'flag',b'guard',b'accept',b'effective',b'lane',b'cadence',b'generation',b'recover',b'xor',b'crc',b'hash',b'byte',b'nibble',b'HTF',b'r9_',b'egress',b'mirror',b'seq',b'device',b'gateway',b'quality',b'note',b'hint',b'answer',b'compute',b'derive']
seen=set()
for s in strings:
    sl=s.lower()
    if any(k in sl for k in kws):
        if s not in seen and not s.startswith(b'HTF{r9_'):
            seen.add(s)
print('interesting strings', len(seen))
for s in sorted(seen):
    print(s[:160])
