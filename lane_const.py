#!/usr/bin/env python3
import r9_emu as R
mods=R.mods; B2I=R.BYTE2IDX
db=open(r"f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db","rb").read()
def entries(rec):
    tl=len(rec); o=8; out={}
    while o+2<=tl-2:
        code=rec[o]; cnt=rec[o+1]; pl=bytes(rec[o+2:o+2+cnt]); idx=B2I.get(code)
        out[mods[idx] if idx is not None else hex(code)]=pl; o+=2+cnt
    return out
recs=[]; i=0; k=0
while True:
    j=db.find(b"R9CF",i)
    if j<0: break
    k+=1; ln=db[j+5]|(db[j+6]<<8); rec=db[j:j+ln]
    c=R.crc16(rec,ln-2); emb=(rec[-2]<<8)|rec[-1]
    if (c&0xffff)==emb: recs.append((k,entries(rec)))
    i=j+4
laneA=[e for k,e in recs if k in (3,7,9)]
laneB=[e for k,e in recs if k in (4,10,11)]
for name,grp in (("LANE-A(#3,7,9)",laneA),("LANE-B(#4,10,11)",laneB)):
    print("==",name)
    for m in mods:
        vals=sorted(set(e.get(m,b"").hex() for e in grp))
        tag="CONST" if len(vals)==1 else "vary "
        print(f"  {m:>3}: {tag} {vals}")
