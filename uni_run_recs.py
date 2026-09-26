#!/usr/bin/env python3
import uni_main as UM
import r9_emu as R

db=open(r"f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db","rb").read()
# extract records
recs=[]; i=0; k=0
while True:
    j=db.find(b"R9CF",i)
    if j<0: break
    k+=1; ln=db[j+5]|(db[j+6]<<8); rec=db[j:j+ln]
    c=R.crc16(rec,ln-2); emb=(rec[-2]<<8)|rec[-1]; ok=(c&0xffff)==emb
    recs.append((k,ok,rec)); i=j+4

def run(buf,label):
    emu=UM.Emu(buf)
    emu.run_main()
    pc=emu.printf_out
    if pc:
        nm,flag,fmt,rdx,rcx,r8=pc[0]
        print(f"{label}: accepted={rdx} guard={rcx&0xff:#04x}  (flag=HTF{{r9_{rcx&0xff:02x}}})")
    else:
        print(f"{label}: no printf")

# single valid record
for k,ok,rec in recs:
    run(rec, f"rec#{k} (crc_ok={ok})")

# lane groups
laneA=b"".join(rec for k,ok,rec in recs if k in (3,7,9))
laneB=b"".join(rec for k,ok,rec in recs if k in (4,10,11))
run(laneA, "LANE-A concat (#3,7,9)")
run(laneB, "LANE-B concat (#4,10,11)")
run(db[:0x10000], "DB first 64KB (what binary really reads on DB)")
