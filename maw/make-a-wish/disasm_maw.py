from pwn import *
from capstone import *
e=ELF('chal')
md=Cs(CS_ARCH_X86, CS_MODE_64)
md.detail=False

# figure out function extents from symtab
syms=[]
for s in e.iter_symbols() if hasattr(e,'iter_symbols') else []:
    pass

funcs=['main','menu','create','delete','split','total','sub_401296']
addrs=sorted(set(e.symbols[f] for f in funcs))
def nextaddr(a):
    for x in addrs:
        if x>a: return x
    return a+0x150

for f in funcs:
    a=e.symbols[f]
    end=nextaddr(a)
    n=min(end-a, 0x300)
    data=e.read(a,n)
    print('\n==== %s @ %#x (len %#x) ===='%(f,a,n))
    for i in md.disasm(data,a):
        print("0x%x:\t%s\t%s"%(i.address,i.mnemonic,i.op_str))
