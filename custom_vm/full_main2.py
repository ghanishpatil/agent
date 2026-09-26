from pwn import *
from unicorn import *
from unicorn.x86_const import *
context.arch='amd64'
P = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e=ELF(P,checksec=False); raw=open(P,'rb').read()

def run_main(argv1, trace=False):
    mu=Uc(UC_ARCH_X86,UC_MODE_64); mu.mem_map(0x0,0x10000)
    for seg in e.segments:
        if seg.header.p_type=='PT_LOAD':
            mu.mem_write(seg.header.p_vaddr, raw[seg.header.p_offset:seg.header.p_offset+seg.header.p_filesz])
    STACK=0x800000; mu.mem_map(STACK-0x100000,0x200000)
    ARGV1=STACK-0x20000; mu.mem_write(ARGV1, argv1+b"\x00")
    PROG=STACK-0x20100; mu.mem_write(PROG, b"./h\x00")
    ARGVEC=STACK-0x10000; mu.mem_write(ARGVEC, p64(PROG)+p64(ARGV1)+p64(0))
    mu.reg_write(UC_X86_REG_RDI, 2)
    mu.reg_write(UC_X86_REG_RSI, ARGVEC)
    RSP=STACK-0x40000; mu.reg_write(UC_X86_REG_RSP, RSP)
    mu.mem_write(RSP, p64(0xdead0000))
    out={'lines':[]}
    def rd_str(a):
        b=b''; k=0
        while k<300:
            c=mu.mem_read(a+k,1)[0]
            if c==0: break
            b+=bytes([c]); k+=1
        return b
    def hook(mu,addr,size,user):
        rsp=mu.reg_read(UC_X86_REG_RSP)
        def ret(v):
            r=u64(mu.mem_read(rsp,8)); mu.reg_write(UC_X86_REG_RSP,rsp+8)
            mu.reg_write(UC_X86_REG_RAX,v&0xffffffffffffffff); mu.reg_write(UC_X86_REG_RIP,r)
        if addr==0x1030:   # puts
            out['lines'].append("puts:"+rd_str(mu.reg_read(UC_X86_REG_RDI)).decode('latin1')); ret(1)
        elif addr==0x1040: # clock_gettime(clk, tp): same time -> elapsed 0
            tp=mu.reg_read(UC_X86_REG_RSI); mu.mem_write(tp, p64(1000)+p64(0)); ret(0)
        elif addr==0x1050: # strlen
            s=mu.reg_read(UC_X86_REG_RDI); k=0
            while mu.mem_read(s+k,1)[0]!=0 and k<4096: k+=1
            ret(k)
        elif addr==0x1060: # printf
            out['lines'].append("printf:"+rd_str(mu.reg_read(UC_X86_REG_RDI)).decode('latin1')); ret(0)
        elif addr==0x1070: # ptrace -> 0
            ret(0)
    for a in (0x1030,0x1040,0x1050,0x1060,0x1070):
        mu.hook_add(UC_HOOK_CODE, hook, begin=a, end=a+1)
    if trace:
        def th(mu,addr,size,u):
            if addr<0x1200: out['lines'].append(f"@{addr:#x}")
        mu.hook_add(UC_HOOK_CODE, th, begin=0x10c0, end=0x11b0)
    try:
        mu.emu_start(0x10c0, 0xdead0000, count=20_000_000)
    except UcError as ex:
        out['lines'].append(f"[err {ex} @ {mu.reg_read(UC_X86_REG_RIP):#x}]")
    return out['lines']

for key in [b"IATCQ{d4rk_c0v3r_vm_rev33}Kbh<V}", b"A"*32]:
    print(repr(key),"->",run_main(key))
