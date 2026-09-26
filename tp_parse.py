import os
img=os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')
d=open(img,'rb').read()

offs=[]; s=0
while True:
    i=d.find(b'R9CF',s)
    if i<0: break
    offs.append(i); s=i+1

# module code table from rodata (index->code)
MODCODES = ['o3','o4','o5','dx','da','ds','c7','c8','cf','cr','sn','g8','x3','mh','ml','xs','lc','zl','bz','xz']

def parse_record(o):
    ln = d[o+5] | (d[o+6]<<8)
    body = d[o:o+ln]
    # header: R9CF(4) b4(1) len(2) = 7 bytes
    p = 7
    entries=[]
    payload = body[:ln-2]
    while p < len(payload):
        tag = payload[p]; 
        if p+1 >= len(payload): break
        cnt = payload[p+1]
        seg = payload[p+2:p+2+cnt]
        entries.append((tag, cnt, seg))
        p += 2+cnt
    return ln, entries

for n,o in enumerate(offs[:12]):
    ln, entries = parse_record(o)
    print(f'=== rec {n:02d} (len={ln}) entries={len(entries)} ===')
    for tag,cnt,seg in entries:
        print(f'   tag={tag:#04x} cnt={cnt} seg={seg.hex()}')
    print()
