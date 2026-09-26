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
# map binary (fresh, so bss is zero and .data pristine)
for t,off,va,fsz,msz in phdrs(binf):
    if t==1 and msz>0: ensure(va,msz); uc.mem_write(va,binf[off:off+fsz])
# overlay only the resolved GOT and .got.plt from core so PLT stubs jump to real funcs
for va,ln in [(0x4adf48,0x90),(0x4adfe8,0xd0)]:
    d=core_va(va,ln)
    if d: uc.mem_write(va,d)

STK=0x7fff00000000; uc.mem_map(STK,0x200000,UC_PROT_ALL); mapped.append((STK,STK+0x200000))
# heap bump allocator
HEAP=0x50000000; uc.mem_map(HEAP,0x400000,UC_PROT_ALL); mapped.append((HEAP,HEAP+0x400000))
heap_ptr=[HEAP]
def alloc(sz):
    p=heap_ptr[0]; sz=(sz+0xf)&~0xf; heap_ptr[0]+=sz+0x10; return p

# TLS / fs base for canary
FS=0x60000000; ensure(FS,0x1000); 
uc.reg_write(UC_X86_REG_FS_BASE,FS); uc.mem_write(FS+0x28,struct.pack("<Q",0x1234567890abcdef))

# crafted input: reconstructed malicious raw record (from reconstruct_raw output) as 1-session frame
# Rebuild raw record here:
S=core_va(0x3767ad0,0xac)
MASK64=(1<<64)-1
sid16=S[0x10:0x20]; sid_hi=struct.unpack_from("<Q",S,0x20)[0]
raw=bytearray(0x9c)
raw[0:0x10]=sid16; raw[0x10:0x18]=S[0x20:0x28]; raw[0x18:0x20]=S[0x28:0x30]
raw[0x20:0x22]=S[0x30:0x32]; raw[0x23]=S[0x32]; raw[0x22]=2
frag_vas=[0x3767c60,0x3767d90,0x3767ed0,0x3768020,0x3768180,0x37682f0]
frags=[core_va(v,0x40) for v in frag_vas]
for event in range(6):
    f=frags[event]; kA=(0xa7+event*0x11)&0xff; sb=sid16[(event*5)&0xf]
    for rdx in range(4):
        pos=0x24+event*4+rdx
        if pos<0x9c: raw[pos]=(f[0x20+rdx]^sb^kA^((sid_hi>>(rdx*8))&0xff))&0xff
raw[0x3c:0x44]=S[0x44:0x4c]; raw[0x44:0x48]=S[0x4c:0x50]; raw[0x48:0x4a]=S[0x50:0x52]
raw[0x4c:0x8c]=S[0x54:0x94]; raw[0x8c:0x9c]=S[0x94:0xa4]

header=struct.pack("<QII",0x33474643534c5441,1,0x9c)  # magic, count=1, recsize=0x9c
INPUT = header + bytes(raw)
inpos=[0]

outbuf=bytearray()

# Hooked function addresses
READ_FULL=0x4029a0   # read_full(buf,len) from stdin
WRITE=0x414cc0       # write(fd,buf,len)
OPEN=0x414c90        # open(path,flags,mode) -> we return fd 3
READ1=0x414bf0       # read(fd,buf,len)
CLOSE=0x414b40
MALLOC=0x40c2f0      # malloc(size) [rdi=size]
CALLOC=0x415640      # ?(edi,esi,...) allocates count*recsize? returns ptr
MEMSET=0x415610
SETUP=0x415880

hooks={}
def do_ret(rax):
    # pop return addr, set rip
    rsp=uc.reg_read(UC_X86_REG_RSP)
    ret=struct.unpack("<Q",uc.mem_read(rsp,8))[0]
    uc.reg_write(UC_X86_REG_RSP,rsp+8)
    uc.reg_write(UC_X86_REG_RIP,ret)
    uc.reg_write(UC_X86_REG_RAX,rax&MASK64)

trace=[]
def hook_code(uc,address,size,user):
    if address==0x4029e0:
        # emit(ctx,src,code,ecx,r8,evstr)
        code=uc.reg_read(UC_X86_REG_RDX)&0xffffffff
        evp=uc.reg_read(UC_X86_REG_R9)
        try: ev=bytes(uc.mem_read(evp,32)).split(b"\x00")[0].decode('latin1')
        except: ev="?"
        trace.append(("emit code=0x%x"%code, ev))
    if address==0x4021f6:
        trace.append(("FINALIZE reached",""))
    if address==0x40225a:  # sha call in finalize: capture args
        a1=uc.reg_read(UC_X86_REG_RDI); a2=uc.reg_read(UC_X86_REG_RSI)
        dx=uc.reg_read(UC_X86_REG_RDX); cx=uc.reg_read(UC_X86_REG_RCX)
        try:
            b1=bytes(uc.mem_read(a1,24)); b2=bytes(uc.mem_read(a2,16))
            trace.append(("SHA-call arg1=%s arg2=%s ctr=0x%x out=0x%x"%(b1.hex(),b2.hex(),dx,cx),""))
        except Exception as e: trace.append(("SHA-call read err",str(e)))
    if address==0x40225f:  # after sha returns: capture digest at 0x4afb40
        try:
            dig=bytes(uc.mem_read(0x4afb40,32))
            trace.append(("SHA-digest=%s"%dig.hex(),""))
        except: pass
    if address==0x402265:  # after serialize
        pass
    if address==0x415f50:  # snprintf(buf,size,fmt,...)
        buf=uc.reg_read(UC_X86_REG_RDI); fmtp=uc.reg_read(UC_X86_REG_RCX)
        r8=uc.reg_read(UC_X86_REG_R8); r9=uc.reg_read(UC_X86_REG_R9)
        try:
            fmt=bytes(uc.mem_read(fmtp,32)).split(b"\x00")[0]
            arg=bytes(uc.mem_read(r9,48)).split(b"\x00")[0]
            trace.append(("snprintf fmt=%r r9arg=%r"%(fmt,arg),""))
        except Exception as e: trace.append(("snprintf err",str(e)))
    if address==ret_addr:
        trace.append(("HIT ret_addr, RAX=0x%x"%uc.reg_read(UC_X86_REG_RAX),""))
    if address in (0x4020e0,0x402066,0x402196,0x401fe6,0x401f62):
        trace.append(("case-branch 0x%x"%address,""))
    if address==0x401f33:
        trace.append(("after emit1 r12b=0x%x"%(uc.reg_read(UC_X86_REG_R12)&0xff),""))
    if 0x401f2e<=address<=0x4021f6 and address in (0x402053,0x40204e,0x40202b,0x40200b):
        trace.append(("in-case2-emit @0x%x"%address,""))
    if address==0x401f29:
        sel=uc.reg_read(UC_X86_REG_R13)
        try: b=uc.mem_read(sel+0x22,1)[0]
        except: b=-1
        trace.append(("dispatch selector=0x%x"%b,""))
    if address==READ_FULL:
        buf=uc.reg_read(UC_X86_REG_RDI); n=uc.reg_read(UC_X86_REG_RSI)
        chunk=INPUT[inpos[0]:inpos[0]+n]
        if len(chunk)<n:
            do_ret(0xffffffffffffffff); return
        uc.mem_write(buf,chunk); inpos[0]+=n
        do_ret(0); return
    if address==READ1:
        # read(fd,buf,len) from stdin; used inside read_full but we hook read_full instead. For /proc read return "12345"
        buf=uc.reg_read(UC_X86_REG_RSI); n=uc.reg_read(UC_X86_REG_RDX)
        s=b"12345"; uc.mem_write(buf,s[:n]); do_ret(min(len(s),n)); return
    if address==WRITE:
        fd=uc.reg_read(UC_X86_REG_RDI); buf=uc.reg_read(UC_X86_REG_RSI); n=uc.reg_read(UC_X86_REG_RDX)
        data=bytes(uc.mem_read(buf,n)); outbuf.extend(data)
        do_ret(n); return
    if address==OPEN:
        do_ret(3); return
    if address==CLOSE:
        do_ret(0); return
    if address==MALLOC:
        sz=uc.reg_read(UC_X86_REG_RDI); p=alloc(sz if sz else 16)
        do_ret(p); return
    if address==CALLOC:
        # signature unknown; from 0x40184b: rdi=?,rsi=r12(size),... returns ptr. Just alloc rsi bytes zeroed.
        sz=uc.reg_read(UC_X86_REG_RSI); p=alloc(sz if sz else 16)
        uc.mem_write(p,b"\x00"*((sz+0xf)&~0xf)); do_ret(p); return
    if address==MEMSET:
        # 0x415610(rdi=buf,rsi=size,rdx=fill?) - actually memmove/memset. From 0x401864 edx=0x10. skip: treat as memset(rdi,0,rsi)
        buf=uc.reg_read(UC_X86_REG_RDI); n=uc.reg_read(UC_X86_REG_RSI)
        if n<0x100000: uc.mem_write(buf,b"\x00"*n)
        do_ret(buf); return
    if address==SETUP:
        do_ret(0); return
    if address==0x4010d0:   # strncpy(dst,src,n)
        dst=uc.reg_read(UC_X86_REG_RDI); src=uc.reg_read(UC_X86_REG_RSI); n=uc.reg_read(UC_X86_REG_RDX)
        s=bytes(uc.mem_read(src,n)); z=s.find(b"\x00")
        if z<0: out=s
        else: out=s[:z]+b"\x00"*(n-z)
        uc.mem_write(dst,out[:n]); do_ret(dst); return
    if address in (0x414b30,0x412880):   # strlen(s)
        s=uc.reg_read(UC_X86_REG_RDI); i=0
        while uc.mem_read(s+i,1)[0]!=0 and i<65536: i+=1
        do_ret(i); return
    if address==0x415730:   # explicit_bzero/free-ish (finalize) -> nop
        do_ret(0); return
    if address in (0x401050,0x401110):   # memcpy/memmove/memset PLT
        dst=uc.reg_read(UC_X86_REG_RDI); a2=uc.reg_read(UC_X86_REG_RSI); n=uc.reg_read(UC_X86_REG_RDX)
        if n and n<0x1000000:
            ensure(dst,n)
            if a2>0x10000:  # memcpy(dst,src,n)
                ensure(a2,n); uc.mem_write(dst, bytes(uc.mem_read(a2,n)))
            else:           # memset(dst,val,n)
                uc.mem_write(dst, bytes([a2&0xff])*n)
        do_ret(dst); return
    if address in (0x4117e0,0x411840,0x411a20,0x411a80,0x412180,0x432040):   # __memset_* variants (dst,val,len)
        dst=uc.reg_read(UC_X86_REG_RDI); val=uc.reg_read(UC_X86_REG_RSI)&0xff; n=uc.reg_read(UC_X86_REG_RDX)
        if n<0x1000000:
            ensure(dst,n); uc.mem_write(dst,bytes([val])*n)
        do_ret(dst); return

uc.hook_add(UC_HOOK_CODE, hook_code)

def hook_mem(uc,access,address,size,value,user):
    # map missing page on demand
    ensure(address, size if size else 8)
    return True
uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, hook_mem)

# run worker 0x401780
ret_addr=0x11111110; ensure(ret_addr,0x10); uc.mem_write(ret_addr,b"\xf4")
rsp=STK+0x100000; rsp-=8; uc.mem_write(rsp,struct.pack("<Q",ret_addr))
uc.reg_write(UC_X86_REG_RSP,rsp)
uc.reg_write(UC_X86_REG_RIP,0x401780)
faults=[]
try:
    uc.emu_start(0x401780, ret_addr, 30_000_000, 0)
except UcError as e:
    print("UcError:", e, "RIP=0x%x"%uc.reg_read(UC_X86_REG_RIP))
print("RAX(ret)=0x%x"%uc.reg_read(UC_X86_REG_RAX))
print("OUTPUT (%d bytes):"%len(outbuf), bytes(outbuf))
def asc(b): return "".join(chr(x) if 32<=x<127 else "." for x in b)
print("OUTPUT ascii:", asc(bytes(outbuf)))
print("\n=== TRACE ===")
for t in trace: print("  ",t)
