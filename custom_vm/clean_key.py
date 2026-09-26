import vm_model as VM
SBOX=VM.SBOX; p=0x01000193; MASK=0xffffffff
pinv=pow(p,-1,1<<32); TARGET=0x86d03165
def rol3(v): v&=0xff; return ((v<<3)|(v>>5))&0xff
def fold(H,T,U,i):
    e=((H^T)*p)&MASK; e=(e^(((U<<8)|i)&MASK))&MASK; return (e*p)&MASK
def step(H,K,x0,x1,i):
    T=(SBOX[(x1^rol3(K))&0xff]^x0)&0xff; U=(SBOX[(T^K^i)&0xff]^x1)&0xff
    return fold(H,T,U,i),(T^U)&0xff

# prefix bytes 0..25 (26 bytes), all safe/readable. pairs 0..12 complete.
prefix = b"IATCQ{cl0ck_vm_ghost_r3v3}"   # need 26 chars
prefix = (prefix + b"_"*26)[:26]
# recompute a clean 26-char readable prefix:
prefix = b"IATCQ{darkcovervmreverse01"[:26]
assert len(prefix)==26, len(prefix)
H=0x811c9dc5; K=0x42
for it in range(13):  # pairs 0..12 = bytes 0..25
    i=it*2; H,K=step(H,K,prefix[i],prefix[i+1],i)
H13,K13=H,K

PR=list(range(0x20,0x7f))
# FORWARD D14: pair13 (b26,b27) printable -> (H14,K14)
D14={}
for b26 in PR:
    for b27 in PR:
        H14,K14=step(H13,K13,b26,b27,26)
        D14.setdefault((H14,K14),(b26,b27))
# BACKWARD B15: invert iter15 (pair15 = b30, '}'=0x7d) for printable b30
B15={}
BR=0x7d
for K15 in range(256):
    r3=rol3(K15)
    for b30 in PR:
        T15=(SBOX[(BR^r3)&0xff]^b30)&0xff
        U15=(SBOX[(T15^K15^30)&0xff]^BR)&0xff
        a=(TARGET*pinv)&MASK; a=(a^(((U15<<8)|30)&MASK))&MASK; a=(a*pinv)&MASK
        reqH15=(T15^a)&MASK
        B15.setdefault((reqH15,K15),b30)
print("D14",len(D14),"B15",len(B15),flush=True)
# MIDDLE iter14: pair14 (b28,b29) printable, connect
sol=None
for (H14,K14),(b26,b27) in D14.items():
    for b28 in PR:
        for b29 in PR:
            H15,K15=step(H14,K14,b28,b29,28)
            b30=B15.get((H15,K15))
            if b30 is not None:
                sol=(b26,b27,b28,b29,b30); Hk=(H14,K14)
                break
        if sol: break
    if sol: break
if sol:
    b26,b27,b28,b29,b30=sol
    flag=bytes(prefix)+bytes([b28,b29,b30,0x7d])  # wait fix ordering
    # bytes: 0..25 prefix, 26=b26,27=b27,28=b28,29=b29,30=b30,31='}'
    flag=bytes(prefix)+bytes([b28,b29,b30])  # WRONG - fix below
    flag=bytes(list(prefix)+[b28,b29,b30,0x7d])
    # correct assembly:
    fl=bytearray(prefix)  # 26 bytes (0..25)
    fl.append(b26); fl.append(b27); fl.append(b28); fl.append(b29); fl.append(b30); fl.append(0x7d)
    fl=bytes(fl[:32])
    print("FLAG:",fl,flush=True)
    print("hex:",fl.hex(),flush=True)
    print("all printable:",all(32<=c<127 for c in fl),flush=True)
    print("vm=%#x target=%#x %s"%(VM.vm(fl),TARGET,"MATCH" if VM.vm(fl)==TARGET else "FAIL"),flush=True)
    open("clean_flag.bin","wb").write(fl)
else:
    print("no printable solution for this prefix; try another",flush=True)
