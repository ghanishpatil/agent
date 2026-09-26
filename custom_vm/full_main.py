from pwn import *
from unicorn import *
from unicorn.x86_const import *
context.arch='amd64'
P = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e=ELF(P,checksec=False); raw=open(P,'rb').read()

def run_main(argv1):
    mu=Uc(UC_ARCH_X86,UC_MODE_64); mu.mem_map(0x0,0x8000)
    for seg in e.segments:
        if seg.header.p_type=='PT_LOAD':
            mu.mem_write(seg.header.p_vaddr, raw[seg.header.p_offset:seg.header.p_offset+seg.header.p_filesz])
    STACK=0x300000; mu.mem_map(STACK-0x40000,0x80000)
    # set up argv: argc=2, argv=[prog, argv1]
    ARGV1=STACK-0x10000; mu.mem_write(ARGV1, argv1+b"\x00")
    PROG=STACK-0x10100; mu.mem_write(PROG, b"./hyperstate4\x00")
    ARGVEC=STACK-0x8000
    mu.mem_write(ARGVEC, p64(PROG)+p64(ARGV1)+p64(0))
    mu.reg_write(UC_X86_REG_RDI, 2)          # argc
    mu.reg_write(UC_X86_REG_RSI, ARGVEC)     # argv
    mu.reg_write(UC_X86_REG_RSP, STACK)
    mu.mem_write(STACK, p64(0xdead0000))     # return addr for main
    out={'lines':[]}
    # PLT stubs to hook: puts@0x1030, clock_gettime@0x1040, strlen@0x1050, printf@0x1060, ptrace@0x1070
    def hook(mu,addr,size,user):
        rsp=mu.reg_read(UC_X86_REG_RSP)
        def ret_with(val):
            r=u64(mu.mem_read(rsp,8)); mu.reg_write(UC_X86_REG_RSP,rsp+8); mu.reg_write(UC_X86_REG_RAX,val&0xffffffffffffffff); mu.reg_write(UC_X86_REG_RIP,r)
        if addr==0x1030:  # puts(rdi)
            s=mu.reg_read(UC_X86_REG_RDI); buf=b''; k=0
            while True:
                c=mu.mem_read(s+k,1)[0]
                if c==0 or k>200: break
                buf+=bytes([c]); k+=1
            out['lines'].append(buf.decode('latin1'))
            ret_with(0)
        elif addr==0x1040: # clock_gettime(clk, tp) -> write increasing time, return 0
            tp=mu.reg_read(UC_X86_REG_RSI)
            out['t']=out.get('t',0)+1
            mu.mem_write(tp, p64(out['t'])+p64(0))  # tv_sec grows slowly, tv_nsec 0
            ret_with(0)
        elif addr==0x1050: # strlen(rdi)
            s=mu.reg_read(UC_X86_REG_RDI); k=0
            while mu.mem_read(s+k,1)[0]!=0 and k<4096: k+=1
            ret_with(k)
        elif addr==0x1060: # printf(fmt,...)
            s=mu.reg_read(UC_X86_REG_RDI); buf=b''; k=0
            while True:
                c=mu.mem_read(s+k,1)[0]
                if c==0 or k>200: break
                buf+=bytes([c]); k+=1
            out['lines'].append("[printf] "+buf.decode('latin1'))
            ret_with(0)
        elif addr==0x1070: # ptrace(...) -> return 0 (not traced)
            ret_with(0)
    for a in (0x1030,0x1040,0x1050,0x1060,0x1070):
        mu.hook_add(UC_HOOK_CODE, hook, begin=a, end=a+1)
    try:
        mu.emu_start(0x10c0, 0xdead0000, timeout=10*1000000, count=5_000_000)
    except UcError as ex:
        out['lines'].append(f"[emu error {ex} @ {hex(mu.reg_read(UC_X86_REG_RIP))}]")
    return out['lines']

for key in [b"IATCQ{d4rk_c0v3r_vm_rev33}Kbh<V}", b"A"*32, b"IATCQ{darkc0ver_vm_rev!!AB_tJh7G"]:
    lines=run_main(key)
    print(repr(key), "->", lines)
