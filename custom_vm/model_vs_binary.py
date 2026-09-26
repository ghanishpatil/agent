from pwn import *
from unicorn import *
from unicorn.x86_const import *
import random
import vm_model as VM
context.arch='amd64'
P = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e=ELF(P,checksec=False); raw=open(P,'rb').read()
mu=Uc(UC_ARCH_X86,UC_MODE_64); mu.mem_map(0x0,0x8000)
for seg in e.segments:
    if seg.header.p_type=='PT_LOAD':
        mu.mem_write(seg.header.p_vaddr, raw[seg.header.p_offset:seg.header.p_offset+seg.header.p_filesz])
STACK=0x200000; mu.mem_map(STACK-0x10000,0x20000)
mu.reg_write(UC_X86_REG_RSP,STACK); mu.mem_write(STACK,p64(0xdead0000))
mu.emu_start(0x12c0,0xdead0000)  # prepare
def strlen_hook(mu,addr,size,u):
    if addr==0x1050:
        s=mu.reg_read(UC_X86_REG_RDI); n=0
        while mu.mem_read(s+n,1)[0]!=0 and n<4096: n+=1
        mu.reg_write(UC_X86_REG_RAX,n)
        rsp=mu.reg_read(UC_X86_REG_RSP); ret=u64(mu.mem_read(rsp,8)); mu.reg_write(UC_X86_REG_RSP,rsp+8); mu.reg_write(UC_X86_REG_RIP,ret)
# capture the binary's internal H at CHECK
cap={}
def hh(mu,addr,size,u):
    if addr==0x1664:
        rsp=mu.reg_read(UC_X86_REG_RSP); cap['H']=u32(mu.mem_read(rsp+0x10,4))
mu.hook_add(UC_HOOK_CODE,hh,begin=0x1664,end=0x1665)

def bin_verify(inp):
    IA=STACK-0x8000; mu.mem_write(IA,inp+b"\x00")
    mu.reg_write(UC_X86_REG_RSP,STACK-0x1000); mu.reg_write(UC_X86_REG_RDI,IA); mu.mem_write(STACK-0x1000,p64(0xdead0000))
    h=mu.hook_add(UC_HOOK_CODE,strlen_hook,begin=0x1050,end=0x1051)
    cap.clear()
    mu.emu_start(0x1460,0xdead0000); mu.hook_del(h)
    return mu.reg_read(UC_X86_REG_RAX)&0xffffffff, cap.get('H')

random.seed(1)
mismatch=0
for t in range(200):
    inp=bytes(random.randint(1,255) for _ in range(32))  # no null
    ret,binH = bin_verify(inp)
    pyH = VM.vm(inp)
    if binH != pyH:
        mismatch+=1
        if mismatch<=5:
            print("MISMATCH:", inp.hex(), "binH",hex(binH) if binH else None, "pyH",hex(pyH))
print(f"tested 200 random inputs; hash mismatches = {mismatch}")

# test my saved flag + a few model solutions
flag=open("found_flag.bin","rb").read()
ret,binH=bin_verify(flag)
print("saved flag:", flag, "bin_ret",ret,"binH",hex(binH))
