import re
img=open(r'f:\mission-git-hackss\mission-git-hackss\temporal_paradox\Temporal Paradox\gateway_snapshot.img','rb').read()

# 1) all HTF{...} and classify
flags=re.findall(rb'HTF\{[^}]{0,60}\}',img)
nonr9=[f for f in set(flags) if not f.startswith(b'HTF{r9_')]
print('total HTF{ matches',len(flags),'unique',len(set(flags)),'NON-r9 unique:',nonr9)

# 2) UTF-16LE 'HTF{'
u16=img.find('HTF{'.encode('utf-16-le'))
print('utf16 HTF{ at',u16)

# 3) any 'HTF' with byte gaps (H.T.F.{)
m=re.findall(rb'H.?T.?F.?\{', img)
print('spaced HTF variants:', set(m))

# 4) reversed
if b'}9r{FTH' in img or b'{FTH' in img: print('reversed present')
rev=img[::-1]
r=re.findall(rb'\}[^{]{0,60}_9r_?\{FTH', rev)
print('reversed flag search:', r[:3])

# 5) base64 of 'HTF{' = 'SFRGe'
print('b64 HTF{ (SFRGe):', img.find(b'SFRGe'))

# 6) Check the SQLite db free/unallocated for any non-r9 HTF
db=open(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db','rb').read()
dbflags=set(re.findall(rb'HTF\{[^}]{0,60}\}',db))
print('db non-r9:', [f for f in dbflags if not f.startswith(b'HTF{r9_')])

# 7) list the distinct decoy count and check for a UNIQUE one appearing only ONCE (real flags often planted once vs decoys many times)
from collections import Counter
c=Counter(flags)
once=[f for f,n in c.items() if n==1]
print('flags appearing exactly once:',len(once))
for f in once[:40]: print('  once:',f)
