from pwn import *
from capstone import *
context.arch='amd64'
e=ELF('chal')
md=Cs(CS_ARCH_X86, CS_MODE_64)

def dis(name, n=0x120):
    addr=e.symbols[name]
    data=e.read(addr, n)
    print('==== %s @ %#x ===='%(name,addr))
    for i in md.disasm(data, addr):
        print("0x%x:\t%s\t%s"%(i.address, i.mnemonic, i.op_str))
        if i.mnemonic in ('ret','hlt'):
            break

dis('main')
print()
dis('arghhhh')
