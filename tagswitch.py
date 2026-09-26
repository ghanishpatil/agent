import struct
from unicorn import *
from unicorn.x86_const import *
ELF=open(r'f:\mission-git-hackss\mission-git-hackss\out_r9sampler','rb').read()
e_phoff=struct.unpack('<Q',ELF[0x20:0x28])[0]; e_phentsize=struct.unpack('<H',ELF[0x36:0x38])[0]; e_phnum=struct.unpack('<H',ELF[0x38:0x3a])[0]
LOAD=[]
for i in range(e_phnum):
    o=e_phoff+i*e_phentsize
    if struct.unpack('<I',ELF[o:o+4])[0]==1:
        LOAD.append((struct.unpack('<Q',ELF[o+16:o+24])[0],struct.unpack('<Q',ELF[o+8:o+16])[0],struct.unpack('<Q',ELF[o+32:o+40])[0]))

def run_func(faddr, rdi, rsi=0, rdx=0):
    mu=Uc(UC_ARCH_X86,UC_MODE_64)
    mu.mem_map(0x0,0x8000)
    for va,off,fsz in LOAD: mu.mem_write(va,ELF[off:off+fsz])
    mu.mem_map(0x200000,0x100000); mu.reg_write(UC_X86_REG_RSP,0x200000+0x100000-0x1000)
    # writable scratch for the store tables (already in mapped .data/.bss region? map 0x3000-0x8000 covered)
    mu.reg_write(UC_X86_REG_RDI,rdi); mu.reg_write(UC_X86_REG_RSI,rsi); mu.reg_write(UC_X86_REG_RDX,rdx)
    mu.mem_write(0x7000,b'\xf4'); rsp=mu.reg_read(UC_X86_REG_RSP); mu.mem_write(rsp,struct.pack('<Q',0x7000))
    calls=[]
    def hook(mu,addr,size,u):
        if addr==0x1656:
            calls.append((mu.reg_read(UC_X86_REG_RDI),mu.reg_read(UC_X86_REG_RDX)))
            # emulate 0x1656 return quickly by just letting it run (it's fine)
    mu.hook_add(UC_HOOK_CODE,hook)
    try:
        mu.emu_start(faddr,0x7000)
    except UcError:
        pass
    return mu.reg_read(UC_X86_REG_RAX)&0xffffffff, calls

# For 0x16b1: it calls 0x1656(index, rsi_string, rdx_len). We want the index chosen per input byte.
print('input_byte -> slot_index (via 0x1656 first arg)')
mapping={}
for b in range(256):
    # set rsi to a valid readable buffer, rdx=0 so 0x1656 store loop is skipped
    rax,calls=run_func(0x16b1, b, rsi=0x2000, rdx=0)
    if calls:
        idx=calls[0][0]
        mapping[b]=idx
for b,idx in mapping.items():
    c=chr(b) if 32<=b<127 else '?'
    print(f'{b:#04x} {c!r} -> slot {idx}')
print('total mapped', len(mapping))
