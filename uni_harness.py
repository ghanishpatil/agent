#!/usr/bin/env python3
from unicorn import *
from unicorn.x86_const import *
from elftools.elf.elffile import ELFFile
import struct

PATH=r"f:\mission-git-hackss\mission-git-hackss\tp_files\usr__local__sbin__r9sampler"
elf=ELFFile(open(PATH,"rb"))
segs=[]
for seg in elf.iter_segments():
    if seg['p_type']=='PT_LOAD':
        segs.append((seg['p_vaddr'],seg['p_offset'],seg['p_filesz'],seg['p_memsz'],seg.data()))

BASE=0x0
mu=Uc(UC_ARCH_X86,UC_MODE_64)
# map an aligned region covering image
lo=min(v for v,_,_,_,_ in segs)&~0xfff
hi=max(v+m for v,_,_,m,_ in segs)
size=((hi-lo+0xfff)&~0xfff)+0x1000
mu.mem_map(lo, size)
for v,off,fsz,msz,data in segs:
    mu.mem_write(v, data)
# stack
STACK=0x200000; mu.mem_map(STACK,0x100000); 
# scratch
SCR=0x400000; mu.mem_map(SCR,0x100000)

def call(addr, args=(), stack_setup=None):
    # System V: rdi,rsi,rdx,rcx,r8,r9
    regs=[UC_X86_REG_RDI,UC_X86_REG_RSI,UC_X86_REG_RDX,UC_X86_REG_RCX,UC_X86_REG_R8,UC_X86_REG_R9]
    sp=STACK+0x80000
    mu.reg_write(UC_X86_REG_RSP, sp)
    # return address sentinel
    RET=0x1  # unmapped -> we stop by count/hook instead
    for i,a in enumerate(args):
        mu.reg_write(regs[i], a & 0xffffffffffffffff)
    # push fake return addr to a stop marker
    STOP=lo+size-0x10
    mu.reg_write(UC_X86_REG_RSP, sp-8)
    mu.mem_write(sp-8, struct.pack("<Q", STOP))
    try:
        mu.emu_start(addr, STOP)
    except UcError as e:
        pc=mu.reg_read(UC_X86_REG_RIP)
        raise
    return mu.reg_read(UC_X86_REG_RAX) & 0xffffffffffffffff

# fs base for stack canary (fs:[0x28]) - set up GS/FS. Unicorn: set FS base via MSR
FSB=0x500000; mu.mem_map(FSB,0x1000)
mu.reg_write(UC_X86_REG_FS_BASE, FSB)
mu.mem_write(FSB+0x28, struct.pack("<Q", 0xdeadbeefcafef00d))

# --- test crc16 (0x1849): (rdi=buf, esi=n) ---
rec=bytes.fromhex("52394346016200002204f75355678401043a0200024901029004cc583f4d3c08e2aa95907ea02d1ad4021b37c002b2bd4601023101043804504600009d04c86d60686b01026d0440c8cc59d30101c104fb4eea48350102d20108d50102a90102e4dc")
mu.mem_write(SCR, rec)
r=call(0x1849,(SCR, len(rec)-2))
print(f"crc16 unicorn low16 = {r&0xffff:#06x}  embedded={(rec[-2]<<8)|rec[-1]:#06x}")

# --- guard helpers ---
print("f_1273(2,0x19,0x37,0x51,0) =", hex(call(0x1273,(2,0x19,0x37,0x51,0))&0xffffffff))
print("m_12ef(2,1,2,0x10) =", call(0x12ef,(2,1,2,0x10))&0xffffffff)
print("g_1898(0,4) =", call(0x1898,(0,4))&0xffffffff)

# emit8_1362(edi=9,esi=8,rdx=buf)
mu.mem_write(SCR+0x100, b"\x00"*16)
call(0x1362,(9,8,SCR+0x100))
print("emit8 =", mu.mem_read(SCR+0x100,8).hex())
# p_131d(rdi=buf,esi=4,edx=1)
print("p_131d(buf,4,1) =", call(0x131d,(SCR+0x100,4,1))&0xffffffff)
# h_12ab(edi=2,esi=0x51,rdx=&val=0x7f)
mu.mem_write(SCR+0x200, struct.pack("<I",0x7f))
print("h_12ab(2,0x51,&0x7f) =", call(0x12ab,(2,0x51,SCR+0x200))&0xffffffff, "newval=",mu.mem_read(SCR+0x200,4).hex())
