from pwn import *
e=ELF('chal')
# rodata 0x402000 size 0xa6
data=e.read(0x402000, 0xa6)
off=0x402000
# print strings with addresses
cur=b''
start=off
for i,b in enumerate(data):
    if b==0:
        if cur:
            print(hex(start), repr(cur))
        cur=b''
        start=off+i+1
    else:
        cur+=bytes([b])
if cur:
    print(hex(start), repr(cur))

# resolve rip-relative string addresses used in main
print('\n---- resolve main string refs ----')
refs = {
 0x4011aa:0xe57, 0x4011c5:0xe4d, 0x4011e6:0xe2f, 0x4011fa:0xe3f,
 0x401218:0xe46, 0x40122c:0xe3d, 0x40124a:0xe14, 0x40125e:0xe31,
}
from capstone import *
md=Cs(CS_ARCH_X86,CS_MODE_64)
addr=e.symbols['main']
d=e.read(addr,0x260)
for i in md.disasm(d,addr):
    if i.mnemonic=='lea' and 'rip' in i.op_str:
        # next instr addr + disp
        try:
            disp=int(i.op_str.split('+')[1].strip().rstrip(']'),16)
        except:
            continue
        tgt=i.address+i.size+disp
        if 0x402000<=tgt<0x4020a6:
            s=e.read(tgt,64).split(b'\0')[0]
            print(hex(i.address),'->',hex(tgt),repr(s))
