from capstone import *
from pwn import ELF
e = ELF("chal")
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True

def dis(name):
    addr = e.symbols[name]
    # find size: read until next symbol or a chunk
    code = e.read(addr, 0x200)
    print(f"===== {name} @ {hex(addr)} =====")
    for insn in md.disasm(code, addr):
        print(f"{insn.address:#x}: {insn.mnemonic}\t{insn.op_str}")
        if insn.mnemonic == 'ret' or (insn.mnemonic=='jmp' and name!='main'):
            # stop after first ret for readability of small funcs? keep going a bit
            pass

for n in ["main","__gets"]:
    dis(n)

# also dump .rodata around the strings
print("===== rodata =====")
ro = e.get_section_by_name('.rodata')
print(hex(ro.header.sh_addr))
data = ro.data()
import re
for m in re.finditer(rb"[ -~]{3,}", data):
    print(hex(ro.header.sh_addr + m.start()), m.group())
