#!/usr/bin/env python3
import struct
BASE = r"f:\mission-git-hackss\mission-git-hackss\emm\Encrypted Malware in Memory Dump"
CORE = BASE + r"\atlas-sync.core"
def read(p):
    with open(p,"rb") as f: return f.read()
core=read(CORE)
def parse_phdrs(d):
    e_phoff=struct.unpack_from("<Q",d,32)[0]; e_phnum=struct.unpack_from("<H",d,56)[0]; e_phent=struct.unpack_from("<H",d,54)[0]
    out=[]
    for i in range(e_phnum):
        o=e_phoff+i*e_phent; t=struct.unpack_from("<I",d,o)[0]
        off,va,_,fsz,_,_=struct.unpack_from("<QQQQQQ",d,o+8); out.append((t,off,va,fsz))
    return out
cph=parse_phdrs(core)
def core_va(va,ln):
    for t,off,v,fsz in cph:
        if t==1 and v<=va<v+fsz:
            s=off+(va-v); return core[s:s+ln]
    return None

# Dump stack window around the READY buffer to find frame locals (pointers)
# READY output at 0x7ffc6d236d10, buffer [rbp-0x80]. Explore 0x7ffc6d236a00..0x7ffc6d236e00
lo=0x7ffc6d236a00
b=core_va(lo,0x400)
print("=== stack frame candidates (qword ptrs into heap/anon) ===")
for i in range(0,0x400,8):
    v=struct.unpack_from("<Q",b,i)[0]
    va=lo+i
    tag=""
    if 0x3751000<=v<0x3773000: tag="  <-HEAP ptr"
    elif 0x7ff423e5d000<=v<0x7ff423e5f000: tag="  <-ANON ptr"
    elif 0x400000<=v<0x4b7000: tag="  <-IMG ptr"
    elif 0x7ffc6d218000<=v<0x7ffc6d23a000: tag="  <-STACK ptr"
    if tag:
        print(f"  [0x{va:x}] = 0x{v:x}{tag}")

# Also: interpret the region 0x7ffc6d236bb0 header + following as records
print("\n=== try: records at various heap addrs (0x9c stride, case byte +0x22) ===")
# We'll look for the mmap: scan all LOAD segs for 48*0x9c structured. Instead, check ptr [rbp-0x250].
# Guess rbp near 0x7ffc6d236d90 (READY buf [rbp-0x80]=0x7ffc6d236cb0 => rbp=0x7ffc6d236d30)
for rbp_guess in [0x7ffc6d236d30,0x7ffc6d236d90,0x7ffc6d236db0]:
    p250=core_va(rbp_guess-0x250,8)
    p250v=struct.unpack_from("<Q",p250,0)[0] if p250 else None
    p248=core_va(rbp_guess-0x248,8)
    p248v=struct.unpack_from("<Q",p248,0)[0] if p248 else None
    p260=core_va(rbp_guess-0x260,8)
    p260v=struct.unpack_from("<Q",p260,0)[0] if p260 else None
    print(f"  rbp~0x{rbp_guess:x}: [rbp-0x250]=0x{p250v:x} [rbp-0x248]=0x{p248v:x} [rbp-0x260]=0x{p260v:x}" if p250v else f"  rbp~0x{rbp_guess:x}: n/a")
