#!/usr/bin/env python3
import r9sampler_reimpl as S
import uni_main as UM

db=open(r"f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db","rb").read()
recs=[]; i=0; k=0
while True:
    j=db.find(b"R9CF",i)
    if j<0: break
    k+=1; ln=db[j+5]|(db[j+6]<<8); recs.append((k,db[j:j+ln])); i=j+4

def uni(buf):
    e=UM.Emu(buf); e.run_main()
    nm,flag,fmt,rdx,rcx,r8=e.printf_out[0]
    return rdx, rcx&0xff
def py(buf):
    a,g,_,_=S.r9sampler(buf); return a,g

tests={f"rec#{k}":r for k,r in recs}
tests["laneA(3,7,9)"]=b"".join(r for k,r in recs if k in(3,7,9))
tests["laneB(4,10,11)"]=b"".join(r for k,r in recs if k in(4,10,11))
tests["all12"]=b"".join(r for k,r in recs)
tests["empty"]=b""

print(f"{'input':16} {'unicorn(acc,guard)':22} {'python(acc,guard)':22} match")
allok=True
for name,buf in tests.items():
    ua=uni(buf); pa=py(buf); ok=ua==pa; allok&=ok
    print(f"{name:16} {str(ua):22} {str(pa):22} {ok}")
print("\nALL MATCH:", allok)
