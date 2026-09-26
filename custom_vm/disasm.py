from pwn import *
from capstone import *
context.arch='amd64'
p = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e = ELF(p, checksec=False)
t = e.get_section_by_name('.text')
code = t.data()
base = t.header.sh_addr
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail=True
out=[]
for ins in md.disasm(code, base):
    out.append(f"{ins.address:#06x}:  {ins.mnemonic:8} {ins.op_str}")
open(r"f:\mission-git-hackss\mission-git-hackss\custom_vm\text_disasm.txt","w").write("\n".join(out))
print("wrote", len(out), "instructions")

# also dump rodata region of interest as hex
r = e.get_section_by_name('.rodata')
rd = r.data(); rb = r.header.sh_addr
def hx(a0,a1):
    seg=rd[a0-rb:a1-rb]
    return seg
import binascii
print("rodata base", hex(rb), "size", hex(len(rd)))
