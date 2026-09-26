#!/usr/bin/env python3
import struct, hashlib
from unicorn import *
from unicorn.x86_const import *
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
BIN  = BASE + r"\atlas-sync"
with open(CORE,"rb") as f: core=f.read()
with open(BIN,"rb") as f: binf=f.read()
def phdrs(d):
    e_phoff=struct.unpack_from("<Q",d,32)[0]; e_phnum=struct.unpack_from("<H",d,56)[0]; e_phent=struct.unpack_from("<H",d,54)[0]
    out=[]
    for i in range(e_phnum):
        o=e_phoff+i*e_phent
        t,fl=struct.unpack_from("<II",d,o)
        off,va,pa,fsz,msz,al=struct.unpack_from("<QQQQQQ",d,o+8)
        out.append((t,off,va,fsz,msz,fl))
    return out
core_ph=phdrs(core); bin_ph=phdrs(binf)
PAGE=0x1000
def align_down(x): return x & ~(PAGE-1)
def align_up(x): return (x+PAGE-1)&~(PAGE-1)

uc=Uc(UC_ARCH_X86,UC_MODE_64)
mapped=[]
def ensure(va,size):
    a=align_down(va); e=align_up(va+size)
    for (ms,me) in mapped:
        if a>=ms and e<=me: return
    # map region not overlapping
    cur=a
    while cur<e:
        ok=any(ms<=cur<me for ms,me in mapped)
        if not ok:
            uc.mem_map(cur,PAGE,UC_PROT_ALL)
            mapped.append((cur,cur+PAGE))
        cur+=PAGE
def wr(va,data):
    ensure(va,len(data))
    uc.mem_write(va,data)

# map binary LOAD segments (code/rodata/data)
for t,off,va,fsz,msz,fl in bin_ph:
    if t==1 and msz>0:
        ensure(va,msz)
        uc.mem_write(va, binf[off:off+fsz])
# overlay core LOAD segments (runtime memory: heap, bss, stack)
for t,off,va,fsz,msz,fl in core_ph:
    if t==1 and fsz>0:
        ensure(va,fsz)
        uc.mem_write(va, core[off:off+fsz])

# fresh stack
STK=0x200000000
uc.mem_map(STK, 0x100000, UC_PROT_ALL); mapped.append((STK,STK+0x100000))
def call(fn, args, retbufs=None, timeout=5_000_000):
    rsp=STK+0x80000
    ret=0x1FFFFFFF0  # fake ret addr, map it
    ensure(ret,0x10); uc.mem_write(ret, b"\xf4")  # hlt
    rsp-=8; uc.mem_write(rsp, struct.pack("<Q",ret))
    uc.reg_write(UC_X86_REG_RSP, rsp)
    regs=[UC_X86_REG_RDI,UC_X86_REG_RSI,UC_X86_REG_RDX,UC_X86_REG_RCX,UC_X86_REG_R8,UC_X86_REG_R9]
    for r,v in zip(regs,args): uc.reg_write(r,v)
    # set fs base for stack canary (fs:[0x28]); map a TLS block
    try:
        uc.reg_write(UC_X86_REG_FS_BASE, 0x7000000)
    except: pass
    ensure(0x7000000,0x1000); uc.mem_write(0x7000000+0x28, struct.pack("<Q",0xdeadbeefcafef00d))
    try:
        uc.emu_start(fn, ret, timeout, 0)
    except UcError as e:
        print("UcError:", e, "RIP=0x%x"%uc.reg_read(UC_X86_REG_RIP))
    return uc.reg_read(UC_X86_REG_RAX)

# --- validate SHA construction 0x402b20 ---
# signature sha(rdi=out32, rsi=arg2_16, rdx=counter, rcx=out_ptr) ; hashes arg1(24)||arg2(16)||counter8||"atlas/session/v3"
# WAIT: from disasm, rdi is arg1(24 bytes hashed), rsi=arg2(16), rdx=counter, rcx=out(32).
# Let's set arg1 buffer, arg2 buffer, counter, out.
A1=STK+0x1000; A2=STK+0x1100; OUT=STK+0x1200
arg1=bytes(range(24)); arg2=bytes([0xaa]*16); counter=0
wr(A1,arg1); wr(A2,arg2); wr(OUT,b"\x00"*32)
call(0x402b20, [A1, A2, counter, OUT])
emu_out=bytes(uc.mem_read(OUT,32))
py=hashlib.sha256(arg1+arg2+counter.to_bytes(8,"little")+b"atlas/session/v3").digest()
print("emu sha :",emu_out.hex())
print("py  sha :",py.hex())
print("MATCH" if emu_out==py else "MISMATCH")
