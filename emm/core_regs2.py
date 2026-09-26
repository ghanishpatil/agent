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
    print(f"note name={name!r} type={ntype} descsz={descsz}")
    if ntype==1:
        names=["r15","r14","r13","r12","rbp","rbx","r11","r10","r9","r8","rax","rcx","rdx","rsi","rdi","orig_rax","rip","cs","eflags","rsp","ss","fs_base","gs_base","ds","es","fs","gs"]
        vals=struct.unpack_from("<27Q",core,dstart+112)
        R=dict(zip(names,vals))
        for k in ["rip","rsp","rbp","rdi","rsi","rdx","rcx","r8","r9","rax","rbx","r12","r13","r14","r15","fs_base"]:
            print(f"    {k}=0x{R[k]:x}")
