#!/usr/bin/env python3
"""Dump specific VA regions from core, and full strings of app data segments."""
import struct

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"

def read(p):
    with open(p,"rb") as f:
        return f.read()

def parse_phdrs(data):
    e_phoff=struct.unpack_from("<Q",data,32)[0]
    e_phentsize=struct.unpack_from("<H",data,54)[0]
    e_phnum=struct.unpack_from("<H",data,56)[0]
    phdrs=[]
    for i in range(e_phnum):
        off=e_phoff+i*e_phentsize
        p_type,p_flags=struct.unpack_from("<II",data,off)
        p_offset,p_vaddr,_,p_filesz,p_memsz,_=struct.unpack_from("<QQQQQQ",data,off+8)
        phdrs.append(dict(type=p_type,offset=p_offset,vaddr=p_vaddr,filesz=p_filesz))
    return phdrs

def va_to_off(phdrs, va):
    for ph in phdrs:
        if ph["type"]==1 and ph["vaddr"]<=va<ph["vaddr"]+ph["filesz"]:
            return ph["offset"]+(va-ph["vaddr"])
    return None

def hexdump(data, off, length, base_va):
    for i in range(0, length, 16):
        chunk=data[off+i:off+i+16]
        hexs=" ".join(f"{b:02x}" for b in chunk)
        asc="".join(chr(b) if 32<=b<127 else "." for b in chunk)
        print(f"  0x{base_va+i:x}: {hexs:<48} {asc}")

def main():
    data=read(CORE)
    phdrs=parse_phdrs(data)

    # Regions of interest
    for va,ln in [(0x483000,0x200),(0x48523f,0x120),(0x4b0000,0x400),(0x4ae000,0x200)]:
        off=va_to_off(phdrs,va)
        print(f"\n=== VA 0x{va:x} (off 0x{off:x}) ===" if off else f"\n=== VA 0x{va:x} NOT MAPPED ===")
        if off:
            hexdump(data,off,ln,va)

if __name__=="__main__":
    main()
