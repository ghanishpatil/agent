#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
with open(CORE,"rb") as f: core=f.read()
e_phoff=struct.unpack_from("<Q",core,32)[0]; e_phnum=struct.unpack_from("<H",core,56)[0]; e_phent=struct.unpack_from("<H",core,54)[0]
notes=[]
for i in range(e_phnum):
    o=e_phoff+i*e_phent; t=struct.unpack_from("<I",core,o)[0]
    off,va,pa,fsz=struct.unpack_from("<QQQQ",core,o+8)
    if t==4:  # PT_NOTE
        notes.append((off,fsz))
def parse_notes(off,sz):
    p=off; end=off+sz
    while p<end-12:
        namesz,descsz,ntype=struct.unpack_from("<III",core,p); p+=12
        name=core[p:p+namesz]; p+=(namesz+3)&~3
        desc=core[p:p+descsz]; p+=(descsz+3)&~3
        yield name.rstrip(b"\x00"),ntype,desc
for off,sz in notes:
    for name,ntype,desc in parse_notes(off,sz):
        if ntype==1:  # NT_PRSTATUS
            # user_regs_struct is at desc offset 112 (0x70) for x86-64 elf_prstatus
            regoff=112
            names=["r15","r14","r13","r12","rbp","rbx","r11","r10","r9","r8","rax","rcx","rdx","rsi","rdi","orig_rax","rip","cs","eflags","rsp","ss","fs_base","gs_base","ds","es","fs","gs"]
            vals=struct.unpack_from("<27Q",desc,regoff)
            R=dict(zip(names,vals))
            print("=== NT_PRSTATUS ===")
            for k in ["rip","rsp","rbp","rdi","rsi","rdx","rcx","r8","r9","rax","rbx","r12","r13","r14","r15","fs_base"]:
                print(f"  {k}=0x{R[k]:x}")
            break
