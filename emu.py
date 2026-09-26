import struct, sys
from unicorn import *
from unicorn.x86_const import *

ELF=open(r'f:\mission-git-hackss\mission-git-hackss\out_r9sampler','rb').read()

# ---- parse program headers to load ----
e_phoff=struct.unpack('<Q',ELF[0x20:0x28])[0]
e_phentsize=struct.unpack('<H',ELF[0x36:0x38])[0]
e_phnum=struct.unpack('<H',ELF[0x38:0x3a])[0]
e_entry=struct.unpack('<Q',ELF[0x18:0x20])[0]

LOAD=[]
for i in range(e_phnum):
    o=e_phoff+i*e_phentsize
    p_type=struct.unpack('<I',ELF[o:o+4])[0]
    p_offset=struct.unpack('<Q',ELF[o+8:o+16])[0]
    p_vaddr=struct.unpack('<Q',ELF[o+16:o+24])[0]
    p_filesz=struct.unpack('<Q',ELF[o+32:o+40])[0]
    p_memsz=struct.unpack('<Q',ELF[o+40:o+48])[0]
    if p_type==1:
        LOAD.append((p_vaddr,p_offset,p_filesz,p_memsz))

# ---- parse sections for symbol addresses via dynamic relocations (PLT) ----
e_shoff=struct.unpack('<Q',ELF[0x28:0x30])[0]
e_shentsize=struct.unpack('<H',ELF[0x3a:0x3c])[0]
e_shnum=struct.unpack('<H',ELF[0x3c:0x3e])[0]
e_shstrndx=struct.unpack('<H',ELF[0x3e:0x40])[0]
secs=[]
for i in range(e_shnum):
    off=e_shoff+i*e_shentsize
    secs.append(dict(name=struct.unpack('<I',ELF[off:off+4])[0],
                     type=struct.unpack('<I',ELF[off+4:off+8])[0],
                     addr=struct.unpack('<Q',ELF[off+16:off+24])[0],
                     offset=struct.unpack('<Q',ELF[off+24:off+32])[0],
                     size=struct.unpack('<Q',ELF[off+32:off+40])[0],
                     link=struct.unpack('<I',ELF[off+40:off+44])[0],
                     entsize=struct.unpack('<Q',ELF[off+56:off+64])[0]))
strtab_off=secs[e_shstrndx]['offset']
def sname(n):
    e=ELF.index(b'\x00',strtab_off+n); return ELF[strtab_off+n:e].decode()
S={sname(s['name']):s for s in secs}

# dynsym + dynstr
dynsym=S['.dynsym']; dynstr=S['.dynstr']
def dynsym_name(idx):
    o=dynsym['offset']+idx*24
    st_name=struct.unpack('<I',ELF[o:o+4])[0]
    e=ELF.index(b'\x00',dynstr['offset']+st_name)
    return ELF[dynstr['offset']+st_name:e].decode()

# rela.plt: maps GOT entry -> symbol. The plt.sec stubs jump via GOT.
rela_plt=S.get('.rela.plt')
plt_map={}  # got addr -> symname
if rela_plt:
    for i in range(rela_plt['size']//24):
        o=rela_plt['offset']+i*24
        r_offset=struct.unpack('<Q',ELF[o:o+8])[0]
        r_info=struct.unpack('<Q',ELF[o+8:o+16])[0]
        sym=r_info>>32
        plt_map[r_offset]=dynsym_name(sym)

# also rela.dyn for GLOB_DAT etc
rela_dyn=S.get('.rela.dyn')
if rela_dyn:
    for i in range(rela_dyn['size']//24):
        o=rela_dyn['offset']+i*24
        r_offset=struct.unpack('<Q',ELF[o:o+8])[0]
        r_info=struct.unpack('<Q',ELF[o+8:o+16])[0]
        sym=r_info>>32
        if sym:
            plt_map.setdefault(r_offset, dynsym_name(sym))

print('PLT/GOT symbol map:', {hex(k):v for k,v in plt_map.items()}, file=sys.stderr)

BASE=0x0
mu=Uc(UC_ARCH_X86, UC_MODE_64)
# map image region
MAP_LO=0x0; MAP_HI=0x8000
mu.mem_map(0x0, 0x8000)
# write file contents at their vaddr (offset==vaddr in this PIE at base 0)
for p_vaddr,p_offset,p_filesz,p_memsz in LOAD:
    mu.mem_write(p_vaddr, ELF[p_offset:p_offset+p_filesz])

# stack
STACK=0x200000; STACK_SZ=0x100000
mu.mem_map(STACK, STACK_SZ)
mu.reg_write(UC_X86_REG_RSP, STACK+STACK_SZ-0x1000)

# heap
HEAP=0x400000; HEAP_SZ=0x200000
mu.mem_map(HEAP, HEAP_SZ)
heap_ptr=[HEAP+0x1000]
def do_malloc(n):
    p=heap_ptr[0]; heap_ptr[0]=(heap_ptr[0]+n+15)&~15; return p

# "fake libc" area for return trampolines - we intercept PLT stubs
# We hook code execution at PLT stub addresses; the GOT contains r_offset addresses (in .got).
# Approach: hook each instruction; when RIP is inside .plt.sec, decode which function via GOT target.

# Build map: plt.sec stub addr -> symbol. plt.sec stubs do: endbr64; bnd jmp [rip+X] -> GOT
pltsec=S.get('.plt.sec')
plt_stub_sym={}
if pltsec:
    from capstone import *
    md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
    a=pltsec['addr']; code=ELF[pltsec['offset']:pltsec['offset']+pltsec['size']]
    for ins in md.disasm(code,a):
        if 'jmp' in ins.mnemonic and 'rip' in ins.op_str:
            disp=ins.operands[0].mem.disp
            got=ins.address+ins.size+disp
            if got in plt_map:
                stub_start=ins.address - 4  # endbr64 is 4 bytes before
                plt_stub_sym[stub_start]=plt_map[got]
print('PLT stub -> sym:', {hex(k):v for k,v in plt_stub_sym.items()}, file=sys.stderr)

# Files provided
CALFILE=sys.argv[1] if len(sys.argv)>1 else r'f:\mission-git-hackss\mission-git-hackss\out_lane_1.cal'
filedata=open(CALFILE,'rb').read()
open_files={}
fd_counter=[1000]

output=[]

def ret_with(mu, val):
    mu.reg_write(UC_X86_REG_RAX, val & 0xffffffffffffffff)
    # pop return address
    rsp=mu.reg_read(UC_X86_REG_RSP)
    retaddr=struct.unpack('<Q',mu.mem_read(rsp,8))[0]
    mu.reg_write(UC_X86_REG_RSP, rsp+8)
    mu.reg_write(UC_X86_REG_RIP, retaddr)

def read_cstr(mu,addr):
    out=b''
    while True:
        c=mu.mem_read(addr,1)
        if c==b'\x00': break
        out+=c; addr+=1
    return out

def handle_plt(mu, sym):
    rdi=mu.reg_read(UC_X86_REG_RDI); rsi=mu.reg_read(UC_X86_REG_RSI)
    rdx=mu.reg_read(UC_X86_REG_RDX); rcx=mu.reg_read(UC_X86_REG_RCX)
    r8=mu.reg_read(UC_X86_REG_R8)
    if sym.startswith('fopen'):
        h=do_malloc(8)
        open_files[h]=[filedata,0]
        ret_with(mu,h)
    elif sym.startswith('malloc'):
        ret_with(mu, do_malloc(rdi))
    elif sym.startswith('fread'):
        # fread(ptr, size, nmemb, stream)
        ptr=rdi; size=rsi; nmemb=rdx; stream=rcx
        f=open_files.get(stream)
        if f is None:
            ret_with(mu,0); return
        want=size*nmemb; buf=f[0][f[1]:f[1]+want]; f[1]+=len(buf)
        mu.mem_write(ptr, buf)
        ret_with(mu, len(buf)//size if size else 0)
    elif sym.startswith('fclose'):
        ret_with(mu,0)
    elif sym.startswith('fwrite'):
        ptr=rdi; size=rsi; nmemb=rdx
        data=mu.mem_read(ptr,size*nmemb)
        output.append(bytes(data))
        ret_with(mu, nmemb)
    elif sym.startswith('free'):
        ret_with(mu,0)
    elif sym.startswith('memcmp'):
        a=mu.mem_read(rdi,rdx); b=mu.mem_read(rsi,rdx)
        r=0
        for x,y in zip(a,b):
            if x!=y: r=(1 if x>y else -1); break
        ret_with(mu,r)
    elif '__printf_chk' in sym:
        # rdi=flag, rsi=fmt, then varargs rdx,rcx,r8,r9
        fmt=read_cstr(mu,rsi).decode('latin1')
        # emulate %u %02x etc using rdx,rcx,r8
        args=[rdx,rcx,r8]
        # crude formatting
        out=fmt
        try:
            out=fmt % tuple((a & 0xffffffff) for a in args[:fmt.count('%')])
        except Exception:
            pass
        output.append(out.encode('latin1'))
        ret_with(mu, len(out))
    elif '__stack_chk_fail' in sym:
        mu.emu_stop()
    else:
        # unknown - just return 0
        ret_with(mu, 0)

def hook_code(mu, address, size, user):
    if address in plt_stub_sym:
        handle_plt(mu, plt_stub_sym[address])

mu.hook_add(UC_HOOK_CODE, hook_code)

# set up argc=2, argv on stack: [argv0, calpath, NULL]
argv0=STACK+STACK_SZ-0x200
calpath=STACK+STACK_SZ-0x180
mu.mem_write(argv0, b'r9sampler\x00')
mu.mem_write(calpath, b'/tmp/x.cal\x00')
argv_arr=STACK+STACK_SZ-0x100
mu.mem_write(argv_arr, struct.pack('<QQQ', argv0, calpath, 0))
mu.reg_write(UC_X86_REG_RDI, 2)
mu.reg_write(UC_X86_REG_RSI, argv_arr)

# fs base for stack canary
GS=0x900000
mu.mem_map(GS,0x1000)
mu.mem_write(GS+0x28, struct.pack('<Q', 0xdeadbeefcafebabe))
try:
    mu.reg_write(UC_X86_REG_FS_BASE, GS)
except Exception:
    pass

# push a fake return address so main can 'ret'
END=0x7000
mu.mem_write(END, b'\xf4')  # hlt
rsp=mu.reg_read(UC_X86_REG_RSP)
mu.mem_write(rsp, struct.pack('<Q', END))

MAIN=0x19d5
try:
    mu.emu_start(MAIN, END)
except UcError as e:
    print('UC error:', e, 'RIP', hex(mu.reg_read(UC_X86_REG_RIP)), file=sys.stderr)

print('OUTPUT:', b''.join(output))
print('RAX:', hex(mu.reg_read(UC_X86_REG_RAX)))

