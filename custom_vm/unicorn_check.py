from pwn import *
from unicorn import *
from unicorn.x86_const import *
context.arch='amd64'
P = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e = ELF(P, checksec=False)
raw = open(P,'rb').read()

BASE=0
# map whole file image by segments
mu=Uc(UC_ARCH_X86, UC_MODE_64)
# map 0x0..0x6000 covering code+rodata+data+bss
mu.mem_map(0x0, 0x8000)
# load file bytes at their file offsets == vaddr for this PIE (offsets match vaddr for loaded segs here)
# Map by program headers
for seg in e.segments:
    if seg.header.p_type=='PT_LOAD':
        va=seg.header.p_vaddr; fo=seg.header.p_offset; fsz=seg.header.p_filesz; msz=seg.header.p_memsz
        data=raw[fo:fo+fsz]
        mu.mem_write(va, data)

STACK=0x200000
mu.mem_map(STACK-0x10000, 0x20000)

def run_prepare():
    mu.reg_write(UC_X86_REG_RSP, STACK)
    mu.reg_write(UC_X86_REG_RIP, 0x12c0)
    # prepare returns via ret; set fake return addr
    mu.mem_write(STACK, p64(0xdead0000))
    try:
        mu.emu_start(0x12c0, 0xdead0000)
    except UcError as ex:
        print("prepare err", ex, hex(mu.reg_read(UC_X86_REG_RIP)))

def strlen_hook(mu, address, size, user):
    # hook the PLT strlen at 0x1050: implement strlen(rdi)->rax and ret
    if address==0x1050:
        s=mu.reg_read(UC_X86_REG_RDI)
        n=0
        while mu.mem_read(s+n,1)[0]!=0 and n<1024: n+=1
        mu.reg_write(UC_X86_REG_RAX,n)
        # pop return
        rsp=mu.reg_read(UC_X86_REG_RSP)
        ret=u64(mu.mem_read(rsp,8)); mu.reg_write(UC_X86_REG_RSP, rsp+8)
        mu.reg_write(UC_X86_REG_RIP, ret)

def run_verify(inp):
    # write input string into mapped stack area
    IADDR=STACK-0x8000
    mu.mem_write(IADDR, inp+b"\x00")
    mu.reg_write(UC_X86_REG_RSP, STACK-0x1000)
    mu.reg_write(UC_X86_REG_RDI, IADDR)
    mu.mem_write(STACK-0x1000, p64(0xdead0000))
    h=mu.hook_add(UC_HOOK_CODE, strlen_hook, begin=0x1050, end=0x1051)
    try:
        mu.emu_start(0x1460, 0xdead0000)
    except UcError as ex:
        print("verify err", ex, hex(mu.reg_read(UC_X86_REG_RIP)))
    mu.hook_del(h)
    return mu.reg_read(UC_X86_REG_RAX)&0xffffffff

run_prepare()
# dump decrypted program+sbox from globals to compare
prog = mu.mem_read(0x4060, 93)
sbox = mu.mem_read(0x40C0, 256)
import vm_model
print("prog match:", bytes(prog)==vm_model.PROG)
print("sbox match:", bytes(sbox)==vm_model.SBOX)

import vm_model as VM
captured={}
def hash_hook(mu, address, size, user):
    if address==0x1664:
        rsp=mu.reg_read(UC_X86_REG_RSP)
        H=u32(mu.mem_read(rsp+0x10,4))
        captured['H']=H
hh=mu.hook_add(UC_HOOK_CODE, hash_hook, begin=0x1664, end=0x1665)

for t in [b"A"*32, b"IATCQ{"+b"0"*25+b"}", bytes(range(32)), b"IATCQ{"+bytes(range(65,90))+b"}"]:
    captured.clear()
    r=run_verify(t)
    py=VM.vm(t)
    uni=captured.get('H')
    match = (uni==py)
    print(f"input {t[:12]!r}.. uni_ret={r:#x} uni_H={uni:#x} py_H={py:#x} MATCH={match}")
