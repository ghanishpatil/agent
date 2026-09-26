from pwn import *
from capstone import *
context.arch='amd64'
e=ELF('chal')
md=Cs(CS_ARCH_X86, CS_MODE_64)

# full main
addr=e.symbols['main']
data=e.read(addr, 0x260)
print('==== main @ %#x ===='%addr)
for i in md.disasm(data, addr):
    print("0x%x:\t%s\t%s"%(i.address, i.mnemonic, i.op_str))
    if i.mnemonic=='ret':
        break

# sections
print('\n==== sections ====')
for s in e.sections:
    if s.name:
        print('%-20s addr=%#x size=%#x'%(s.name, s.header.sh_addr, s.header.sh_size))

# arghhhh size = section .bss? find symbol size
print('\n==== symbol sizes ====')
for sym in ['arghhhh','main']:
    for section in e.iter_symbols() if hasattr(e,'iter_symbols') else []:
        pass
