import struct
from capstone import *

data=open(r'f:\mission-git-hackss\mission-git-hackss\out_r9sampler','rb').read()

# parse ELF64 headers
assert data[:4]==b'\x7fELF'
e_shoff=struct.unpack('<Q',data[0x28:0x30])[0]
e_shentsize=struct.unpack('<H',data[0x3a:0x3c])[0]
e_shnum=struct.unpack('<H',data[0x3c:0x3e])[0]
e_shstrndx=struct.unpack('<H',data[0x3e:0x40])[0]

secs=[]
for i in range(e_shnum):
    off=e_shoff+i*e_shentsize
    sh_name=struct.unpack('<I',data[off:off+4])[0]
    sh_type=struct.unpack('<I',data[off+4:off+8])[0]
    sh_addr=struct.unpack('<Q',data[off+16:off+24])[0]
    sh_offset=struct.unpack('<Q',data[off+24:off+32])[0]
    sh_size=struct.unpack('<Q',data[off+32:off+40])[0]
    secs.append((sh_name,sh_type,sh_addr,sh_offset,sh_size))

# shstrtab
strtab_off=secs[e_shstrndx][3]
def sname(n):
    e=data.index(b'\x00',strtab_off+n)
    return data[strtab_off+n:e].decode()

sections={}
for s in secs:
    nm=sname(s[0])
    sections[nm]=s

for nm in ['.text','.rodata','.data','.data.rel.ro']:
    if nm in sections:
        _,_,addr,off,size=sections[nm]
        print(f'{nm}: addr={hex(addr)} off={hex(off)} size={hex(size)}')

# disassemble .text
_,_,taddr,toff,tsize=sections['.text']
code=data[toff:toff+tsize]
md=Cs(CS_ARCH_X86, CS_MODE_64)
md.detail=True
lines=[]
for ins in md.disasm(code, taddr):
    lines.append(f'{ins.address:x}:\t{ins.mnemonic}\t{ins.op_str}')
open(r'f:\mission-git-hackss\mission-git-hackss\r9sampler_full.asm','w').write('\n'.join(lines))
print('instructions',len(lines))

# dump rodata
_,_,raddr,roff,rsize=sections['.rodata']
rod=data[roff:roff+rsize]
print('rodata hex:')
print(rod.hex())
