#!/usr/bin/env python3
import struct, hashlib
from unicorn import *
from unicorn.x86_const import *
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"; BIN = BASE + r"\atlas-sync"
core=open(CORE,'rb').read(); binf=open(BIN,'rb').read()
def phdrs(d):
    ph=struct.unpack_from("<Q",d,32)[0]; n=struct.unpack_from("<H",d,56)[0]; ent=struct.unpack_from("<H",d,54)[0]
    out=[]
    for i in range(n):
        o=ph+i*ent; t=struct.unpack_from("<I",d,o)[0]
        off,va,pa,fsz,msz,al=struct.unpack_from("<QQQQQQ",d,o+8); out.append((t,off,va,fsz,msz))
    return out
def core_va(va,ln):
    for t,off,v,fsz,msz in phdrs(core):
        if t==1 and v<=va<v+fsz: return core[off+(va-v):off+(va-v)+ln]
    return None
S=core_va(0x3767ad0,0xac)

# --- unicorn setup ---
uc=Uc(UC_ARCH_X86,UC_MODE_64); mapped=[]
PAGE=0x1000
def ad(x): return x&~(PAGE-1)
def au(x): return (x+PAGE-1)&~(PAGE-1)
def ensure(va,size):
    cur=ad(va); e=au(va+size)
    while cur<e:
        if not any(ms<=cur<me for ms,me in mapped):
            uc.mem_map(cur,PAGE,UC_PROT_ALL); mapped.append((cur,cur+PAGE))
        cur+=PAGE
for t,off,va,fsz,msz in phdrs(binf):
    if t==1 and msz>0: ensure(va,msz); uc.mem_write(va,binf[off:off+fsz])
for t,off,va,fsz,msz in phdrs(core):
    if t==1 and fsz>0: ensure(va,fsz); uc.mem_write(va,core[off:off+fsz])
STK=0x200000000; uc.mem_map(STK,0x100000,UC_PROT_ALL); mapped.append((STK,STK+0x100000))
def call(fn,args):
    rsp=STK+0x80000; ret=0x1FFFFFF00; ensure(ret,0x10); uc.mem_write(ret,b"\xf4")
    rsp-=8; uc.mem_write(rsp,struct.pack("<Q",ret)); uc.reg_write(UC_X86_REG_RSP,rsp)
    for r,v in zip([UC_X86_REG_RDI,UC_X86_REG_RSI,UC_X86_REG_RDX,UC_X86_REG_RCX,UC_X86_REG_R8,UC_X86_REG_R9],args): uc.reg_write(r,v)
    ensure(0x7000000,0x1000)
    try: uc.reg_write(UC_X86_REG_FS_BASE,0x7000000)
    except: pass
    try: uc.emu_start(fn,ret,3_000_000,0)
    except UcError as e: pass
    return uc.reg_read(UC_X86_REG_RAX)

# serialize malicious struct S: put S bytes into memory, call 0x403140(rdi=Sbuf, rsi=msgbuf)
SB=STK+0x2000; MB=STK+0x2100
ensure(SB,0xac); uc.mem_write(SB,S)
ensure(MB,0x40); uc.mem_write(MB,b"\x00"*0x40)
call(0x403140,[SB,MB])
msg=bytes(uc.mem_read(MB,0x22))
def asc(b): return "".join(chr(x) if 32<=x<127 else "." for x in b)
print("serialized 0x22 msg:", msg.hex())
print("  ascii:", asc(msg))

# authenticated result: sha finalize-style with arg2=sessionid, arg1= msg[0:24]? try several
sid=S[0x10:0x20]
ctx=b"atlas/session/v3"
def sha_construct(a1,a2,counter):
    return hashlib.sha256(a1+a2+counter.to_bytes(8,'little')+ctx).digest()
print("\ncandidate authenticated results:")
cands={
 "sha(msg24||sid||0)": sha_construct(msg[0:24],sid,0),
 "sha(msg[0:24]||msg[?]||2)": sha_construct(msg[0:24],sid,2),
 "sha(S[0x10:0x28]||sid||6)": sha_construct(S[0x10:0x28],sid,6),
 "sha(zeros||zeros||0)_bss": sha_construct(b"\x00"*24,b"\x00"*16,0),
}
for k,v in cands.items():
    print(f"  {k}: {v.hex()}  ascii={asc(v)}")
