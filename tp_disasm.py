from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

f = open('tp_files/usr__local__sbin__r9sampler','rb')
elf = ELFFile(f)
text = elf.get_section_by_name('.text')
text_addr = text['sh_addr']
text_data = text.data()

# symbol table is stripped; disassemble whole .text
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = False
print(f'.text vaddr={text_addr:#x} size={len(text_data)}')

# Find functions by looking at call targets and function prologues
insns = list(md.disasm(text_data, text_addr))
for ins in insns:
    print(f'{ins.address:#06x}:  {ins.mnemonic:8s} {ins.op_str}')
