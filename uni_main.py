#!/usr/bin/env python3
"""Emulate main() at 0x19d5 with libc stubs, feeding a chosen file buffer."""
from unicorn import *
from unicorn.x86_const import *
from elftools.elf.elffile import ELFFile
import struct, sys

PATH=r"f:\mission-git-hackss\mission-git-hackss\tp_files\usr__local__sbin__r9sampler"

class Emu:
    def __init__(self, filebuf):
        self.filebuf=filebuf
        elf=ELFFile(open(PATH,"rb"))
        self.segs=[(s['p_vaddr'],s.data(),s['p_memsz']) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
        self.mu=mu=Uc(UC_ARCH_X86,UC_MODE_64)
        lo=min(v for v,_,_ in self.segs)&~0xfff
        hi=max(v+m for v,_,m in self.segs)
        self.imglo=lo
        size=((hi-lo+0xfff)&~0xfff)
        mu.mem_map(lo,size)
        for v,d,m in self.segs: mu.mem_write(v,d)
        self.STACK=0x7000000; mu.mem_map(self.STACK,0x200000)
        self.HEAP=0x8000000; self.heap_end=self.HEAP; mu.mem_map(self.HEAP,0x400000)
        self.FSB=0x9000000; mu.mem_map(self.FSB,0x1000); mu.reg_write(UC_X86_REG_FS_BASE,self.FSB)
        mu.mem_write(self.FSB+0x28, struct.pack("<Q",0x1111222233334444))
        # GOT/PLT stub region: we hook the .plt.sec calls by intercepting execution addresses
        self.printf_out=[]
        self.filepos=0
        self.open_ok=True
        # resolve plt.sec stub addresses -> which libc fn. We map by reading relocations.
        self.plt=self._resolve_plt(elf)
        # hook code to intercept calls into plt.sec / plt.got
        mu.hook_add(UC_HOOK_CODE, self._hook_code)
        self.retval=None

    def _resolve_plt(self, elf):
        # .plt.sec entries at 0x10d0 stride 0x10 map to .rela.plt order
        # Build name list from rela.plt + dynsym
        rela=None
        for s in elf.iter_sections():
            if s.name=='.rela.plt': rela=s
        dynsym=elf.get_section_by_name('.dynsym')
        names=[]
        for r in rela.iter_relocations():
            sym=dynsym.get_symbol(r['r_info_sym'])
            names.append(sym.name)
        # .plt.sec starts at 0x10d0
        base=0x10d0
        m={}
        for i,nm in enumerate(names):
            m[base+i*0x10]=nm
        # also .plt.got at 0x10c0 (usually __cxa_finalize)
        return m

    def _malloc(self,n):
        p=self.heap_end; self.heap_end=(self.heap_end+n+0xf)&~0xf; return p
    def _hook_code(self, mu, addr, size, ud):
        nm=self.plt.get(addr)
        if nm is None: return
        # emulate libc call, then return to caller
        rdi=mu.reg_read(UC_X86_REG_RDI); rsi=mu.reg_read(UC_X86_REG_RSI)
        rdx=mu.reg_read(UC_X86_REG_RDX); rcx=mu.reg_read(UC_X86_REG_RCX)
        r8=mu.reg_read(UC_X86_REG_R8)
        ret=0
        if nm in ('fopen','fopen64'):
            ret=0xF11E0001 if self.open_ok else 0
        elif nm=='malloc':
            ret=self._malloc(rdi)
        elif nm in ('fread',):
            # fread(ptr=rdi,size=rsi,nmemb=rdx,stream=rcx)
            total=rsi*rdx
            data=self.filebuf[self.filepos:self.filepos+total]
            mu.mem_write(rdi, data)
            self.filepos+=len(data)
            ret=len(data)//rsi if rsi else 0
        elif nm in ('fclose','free'):
            ret=0
        elif nm=='memcmp':
            a=mu.mem_read(rdi,rdx); b=mu.mem_read(rsi,rdx)
            ret=0 if bytes(a)==bytes(b) else 1
        elif nm in ('printf','__printf_chk','fprintf','__fprintf_chk'):
            self.printf_out.append((nm,rdi,rsi,rdx,rcx,r8))
            ret=0
        elif nm=='__stack_chk_fail':
            ret=0
        else:
            ret=0
        mu.reg_write(UC_X86_REG_RAX, ret)
        # simulate 'ret': pop return address
        sp=mu.reg_read(UC_X86_REG_RSP)
        retaddr=struct.unpack("<Q", mu.mem_read(sp,8))[0]
        mu.reg_write(UC_X86_REG_RSP, sp+8)
        mu.reg_write(UC_X86_REG_RIP, retaddr)

    def run_main(self, argc=2):
        mu=self.mu
        # set argv: argv[0]=prog, argv[1]="file"
        argv=self.STACK+0x100000
        s0=argv+0x1000; s1=argv+0x1100
        mu.mem_write(s0,b"r9sampler\x00"); mu.mem_write(s1,b"lane\x00")
        mu.mem_write(argv, struct.pack("<QQ", s0, s1))
        sp=self.STACK+0x180000
        STOP=self.imglo  # 0 addr won't be used; use a sentinel in mapped area
        STOP=0x6fffff0
        mu.mem_map(0x6000000,0x1000)
        STOP=0x6000000
        mu.reg_write(UC_X86_REG_RSP, sp-8)
        mu.mem_write(sp-8, struct.pack("<Q",STOP))
        mu.reg_write(UC_X86_REG_RDI, argc)
        mu.reg_write(UC_X86_REG_RSI, argv)
        mu.reg_write(UC_X86_REG_RDX, 0)
        try:
            mu.emu_start(0x19d5, STOP)
        except UcError as e:
            print("UcError at RIP",hex(mu.reg_read(UC_X86_REG_RIP)), e)
        rax=mu.reg_read(UC_X86_REG_RAX)&0xffffffff
        return rax

    def read_bss_slots(self):
        sb=bytes(self.mu.mem_read(0x4060, 20*12))
        sc=bytes(self.mu.mem_read(0x4040, 20))
        return sb,sc

def decode_printf(emu):
    # find printf("accepted=%u guard=%02x\n", accepted, guard)
    out=[]
    for rec in emu.printf_out:
        nm,a,b,c,d,e=rec
        out.append((nm,a,b,c,d,e))
    return out

if __name__=="__main__":
    db=open(r"f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db","rb").read()
    emu=Emu(db)
    r=emu.run_main()
    print("main returned:", hex(r))
    for rec in emu.printf_out:
        print("printf-call:", rec[0], "args:", [hex(x) for x in rec[1:]])
