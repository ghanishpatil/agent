#!/bin/bash
cd /work/waf/waf
python3 - <<'PY'
from pwn import *
context.binary=e=ELF("./chal",checksec=False)
print("plt0    =", hex(e.get_section_by_name(".plt").header.sh_addr))
print("read@plt=", hex(e.plt.read))
print("printf@plt=", hex(e.plt.printf))
print("puts@plt=", hex(e.plt.puts))
print("read GOT=", hex(e.got.read))
print(".bss    =", hex(e.bss()))
print("dynsym  =", hex(e.get_section_by_name(".dynsym").header.sh_addr))
print("dynstr  =", hex(e.get_section_by_name(".dynstr").header.sh_addr))
print("relaplt =", hex(e.get_section_by_name(".rela.plt").header.sh_addr))
# main read-into-rbp site: find address of 'call __gets' and the lea before it
print("main    =", hex(e.symbols.main))
print("gets    =", hex(e.symbols.__gets))
PY
echo "=== disasm main around the gets call + loop head ==="
objdump -d -M intel chal | sed -n '/40131c:/,/401373:/p'
