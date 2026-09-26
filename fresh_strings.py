import re
d=open(r'f:\mission-git-hackss\mission-git-hackss\temporal_paradox\Temporal Paradox\gateway_snapshot.img','rb').read()
# find long printable strings with spaces (english-like), dedup
strings=re.findall(rb'[\x20-\x7e]{12,}',d)
seen=set()
for s in strings:
    # english-like: has spaces and letters, not just data
    if s in seen: continue
    seen.add(s)
    txt=s.decode()
    # skip decoys and known
    if 'agent-cache' in txt: continue
    if txt.startswith('HTF{r9_'): continue
    if 'CR9.' in txt and len(txt)<40: continue
    # keep ones with multiple spaces (sentences) or interesting keywords
    spaces=txt.count(' ')
    if spaces>=2 or any(k in txt.lower() for k in ['flag','key','decrypt','xor','aes','effective','egress','object','reconstruct','note','readme','how','step','combine','secret','pass']):
        print(txt[:150])
