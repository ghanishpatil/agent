#!/usr/bin/env python3
import struct, sys
from capstone import *
from capstone.x86 import X86_OP_MEM, X86_REG_RIP, X86_OP_IMM

BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
BIN  = BASE + r"\atlas-sync"
with open(BIN,"rb") as f: data=f.read()

# VA -> file offset for loaded segments. .text loaded at 0x400000 base (off=VA-0x400000 for text/rodata)
def va2off(va):
    # sections mapping (addr, off, size)
    for addr, off, size in SECMAP:
        if addr <= va < addr+size:
            return off + (va-addr)
    return None

# build section map
e_shoff=struct.unpack_from("<Q",data,40)[0]
e_shentsize=struct.unpack_from("<H",data,58)[0]
e_shnum=struct.unpack_from("<H",data,60)[0]
SECMAP=[]
for i in range(e_shnum):
    o=e_shoff+i*e_shentsize
    _,_,_,sh_addr,sh_offset,sh_size,_,_,_,_=struct.unpack_from("<IIQQQQIIQQ",data,o)
    if sh_addr!=0 and sh_size!=0:
        SECMAP.append((sh_addr,sh_offset,sh_size))

def rostr(va):
    off=va2off(va)
    if off is None: return None
    end=data.find(b"\x00",off)
    return data[off:end].decode("latin1","replace")

md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=True
def dis(start,length,stop_at_ret=True):
    off=va2off(start)
    code=data[off:off+length]
    for insn in md.disasm(code,start):
        note=""
        for op in insn.operands:
            if op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP:
                tgt=insn.address+insn.size+op.mem.disp
                s=rostr(tgt) if 0x483000<=tgt<0x4a0000 else None
                if s is not None and all(32<=ord(c)<127 for c in s[:20]) and len(s)>1:
                    note=f'   ; ->0x{tgt:x} "{s[:48]}"'
                else:
                    note=f"   ; ->0x{tgt:x}"
        if insn.mnemonic=="call":
            for op in insn.operands:
                if op.type==X86_OP_IMM:
                    note+=f"  [CALL 0x{op.imm:x}]"
        print(f"  0x{insn.address:x}: {insn.bytes.hex():<20} {insn.mnemonic} {insn.op_str}{note}")
        if stop_at_ret and insn.mnemonic=="ret":
            break

if __name__=="__main__":
    start=int(sys.argv[1],16)
    length=int(sys.argv[2],16) if len(sys.argv)>2 else 0x400
    stop = not (len(sys.argv)>3 and sys.argv[3]=="noret")
    dis(start,length,stop)
