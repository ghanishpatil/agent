#!/usr/bin/env python3
"""Parse ELF core dump: NOTE segments (PRPSINFO/PRSTATUS/cmdline) + scan for flag/crypto."""
import struct, sys, re

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
BIN  = BASE + r"\atlas-sync"

def read(p):
    with open(p, "rb") as f:
        return f.read()

def parse_elf_phdrs(data):
    assert data[:4] == b"\x7fELF", "not ELF"
    ei_class = data[4]  # 2 = 64-bit
    ei_data  = data[5]  # 1 = LE
    assert ei_class == 2, "not ELF64"
    endian = "<" if ei_data == 1 else ">"
    e_type = struct.unpack_from(endian+"H", data, 16)[0]
    e_phoff = struct.unpack_from(endian+"Q", data, 32)[0]
    e_phentsize = struct.unpack_from(endian+"H", data, 54)[0]
    e_phnum = struct.unpack_from(endian+"H", data, 56)[0]
    phdrs = []
    for i in range(e_phnum):
        off = e_phoff + i*e_phentsize
        p_type, p_flags = struct.unpack_from(endian+"II", data, off)
        p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from(endian+"QQQQQQ", data, off+8)
        phdrs.append(dict(type=p_type, flags=p_flags, offset=p_offset, vaddr=p_vaddr,
                          filesz=p_filesz, memsz=p_memsz, align=p_align))
    return endian, e_type, phdrs

PT_LOAD = 1
PT_NOTE = 4

NT_PRSTATUS = 1
NT_PRFPREG = 2
NT_PRPSINFO = 3
NT_AUXV = 6
NT_FILE = 0x46494c45  # "FILE"

def parse_notes(data, endian, off, size):
    notes = []
    p = off
    end = off + size
    while p < end:
        namesz, descsz, ntype = struct.unpack_from(endian+"III", data, p)
        p += 12
        name = data[p:p+namesz]
        p += (namesz + 3) & ~3
        desc = data[p:p+descsz]
        p += (descsz + 3) & ~3
        notes.append((name.rstrip(b"\x00").decode("latin1"), ntype, desc))
    return notes

def main():
    data = read(CORE)
    print(f"[+] core size = {len(data)}")
    endian, e_type, phdrs = parse_elf_phdrs(data)
    print(f"[+] e_type={e_type} (4=CORE), phnum={len(phdrs)}")
    for ph in phdrs:
        t = {1:"LOAD",4:"NOTE"}.get(ph["type"], str(ph["type"]))
        print(f"    {t:5} off=0x{ph['offset']:x} vaddr=0x{ph['vaddr']:x} filesz=0x{ph['filesz']:x} memsz=0x{ph['memsz']:x}")

    # Parse NOTE segments
    for ph in phdrs:
        if ph["type"] == PT_NOTE:
            print(f"\n[+] NOTE segment at off 0x{ph['offset']:x} size 0x{ph['filesz']:x}")
            notes = parse_notes(data, endian, ph["offset"], ph["filesz"])
            for name, ntype, desc in notes:
                tn = {1:"PRSTATUS",2:"PRFPREG",3:"PRPSINFO",6:"AUXV",NT_FILE:"FILE"}.get(ntype, hex(ntype))
                print(f"    NOTE name={name!r} type={tn} desclen={len(desc)}")
                if ntype == NT_PRPSINFO:
                    # struct elf_prpsinfo: fname[16] at offset 40, psargs[80] at offset 56 (x86_64)
                    try:
                        fname = desc[40:56].split(b"\x00")[0].decode("latin1")
                        psargs = desc[56:136].split(b"\x00")[0].decode("latin1")
                        print(f"        fname   = {fname!r}")
                        print(f"        psargs  = {psargs!r}")
                    except Exception as e:
                        print(f"        prpsinfo parse err {e}")
                if ntype == NT_FILE:
                    # count, page_size, then count*(start,end,fileofs), then filenames
                    cnt, psz = struct.unpack_from(endian+"QQ", desc, 0)
                    p = 16 + cnt*24
                    names = desc[p:].split(b"\x00")
                    print(f"        mapped files count={cnt}:")
                    for nm in names[:cnt]:
                        if nm:
                            print(f"          {nm.decode('latin1')}")

if __name__ == "__main__":
    main()
