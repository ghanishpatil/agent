#!/usr/bin/env python3
"""Analyze atlas-sync ELF: sections, symbols, strings, and interesting data."""
import struct, re

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"

def read(p):
    with open(p,"rb") as f:
        return f.read()

data=read(BIN)
print(f"[+] size={len(data)}")
assert data[:4]==b"\x7fELF"
ei_class=data[4]
print(f"[+] class={'64' if ei_class==2 else '32'}")
e_type=struct.unpack_from("<H",data,16)[0]
e_machine=struct.unpack_from("<H",data,18)[0]
e_entry=struct.unpack_from("<Q",data,24)[0]
e_shoff=struct.unpack_from("<Q",data,40)[0]
e_shentsize=struct.unpack_from("<H",data,58)[0]
e_shnum=struct.unpack_from("<H",data,60)[0]
e_shstrndx=struct.unpack_from("<H",data,62)[0]
print(f"[+] type={e_type} machine={e_machine} entry=0x{e_entry:x}")
print(f"[+] shoff=0x{e_shoff:x} shnum={e_shnum} shstrndx={e_shstrndx}")

# section headers
secs=[]
for i in range(e_shnum):
    off=e_shoff+i*e_shentsize
    sh_name,sh_type,sh_flags,sh_addr,sh_offset,sh_size,sh_link,sh_info,sh_addralign,sh_entsize=struct.unpack_from("<IIQQQQIIQQ",data,off)
    secs.append(dict(name=sh_name,type=sh_type,flags=sh_flags,addr=sh_addr,offset=sh_offset,size=sh_size,link=sh_link,info=sh_info,entsize=sh_entsize))

if e_shnum>0 and e_shstrndx<e_shnum:
    shstr=secs[e_shstrndx]
    shstrtab=data[shstr["offset"]:shstr["offset"]+shstr["size"]]
    def sname(n): return shstrtab[n:shstrtab.find(b"\x00",n)].decode("latin1")
    print("\n[+] sections:")
    for s in secs:
        print(f"    {sname(s['name']):20} type={s['type']:2} addr=0x{s['addr']:x} off=0x{s['offset']:x} size=0x{s['size']:x}")
else:
    print("[!] section headers stripped")
