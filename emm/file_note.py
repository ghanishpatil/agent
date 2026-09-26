#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
with open(CORE,"rb") as f: core=f.read()
off=0x1000; sz=0x344; p=off; end=off+sz
while p<end-12:
    namesz,descsz,ntype=struct.unpack_from("<III",core,p); p+=12
    name=core[p:p+namesz].rstrip(b"\x00"); p+=(namesz+3)&~3
    desc=core[p:p+descsz]; dstart=p; p+=(descsz+3)&~3
    if ntype==0x46494c45:  # FILE
        count,pgsz=struct.unpack_from("<QQ",desc,0)
        print(f"FILE note: count={count} pagesize=0x{pgsz:x}")
        o=16
        entries=[]
        for i in range(count):
            start,end2,fileoff=struct.unpack_from("<QQQ",desc,o); o+=24
            entries.append((start,end2,fileoff))
        # filenames follow
        names=desc[o:].split(b"\x00")
        for i,(s,e,fo) in enumerate(entries):
            nm=names[i].decode('latin1','replace') if i<len(names) else '?'
            print(f"  0x{s:x}-0x{e:x} fileoff=0x{fo:x}  {nm}")
    elif ntype==3:
        # PRPSINFO: has fname (16) and psargs (80) near end
        # struct: state,sname,zomb,nice(1each)+pad, flags(8),uid,gid(4),pid,ppid,pgrp,sid(4), fname[16], psargs[80]
        fname=desc[40:56].split(b"\x00")[0]
        psargs=desc[56:136].split(b"\x00")[0]
        print(f"PRPSINFO fname={fname!r} args={psargs!r}")
