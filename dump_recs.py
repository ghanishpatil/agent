#!/usr/bin/env python3
import r9_emu as R
mods=R.mods; B2I=R.BYTE2IDX
db=open(r"f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db","rb").read()
def entries(rec):
    tl=len(rec); o=8; out=[]
    while o+2<=tl-2:
        code=rec[o]; cnt=rec[o+1]; pl=rec[o+2:o+2+cnt]
        out.append((code,cnt,bytes(pl))); o+=2+cnt
    return out
i=0;k=0
recs=[]
while True:
    j=db.find(b'R9CF',i)
    if j<0: break
    k+=1; ln=db[j+5]|(db[j+6]<<8); rec=db[j:j+ln]
    c=R.crc16(rec,ln-2); emb=(rec[-2]<<8)|rec[-1]; ok=(c&0xffff)==emb
    recs.append((k,j,ln,ok,rec)); i=j+4
for (k,j,ln,ok,rec) in recs:
    if not ok: continue
    es=entries(rec)
    print(f"\n#{k} (byte4={rec[4]:#x}) entries (in file order):")
    for code,cnt,pl in es:
        idx=B2I.get(code)
        mm=mods[idx] if idx is not None else '??'
        print(f"   {code:#04x}={mm:>3} cnt={cnt} payload={pl.hex()}")
