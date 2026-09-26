import vm_model as VM
SBOX=VM.SBOX; p=0x01000193; MASK=0xffffffff
pinv=pow(p,-1,1<<32)
TARGET=0x86d03165
def rol3(v): v&=0xff; return ((v<<3)|(v>>5))&0xff
def fold(H,T,U,i):
    e=((H^T)*p)&MASK
    e=(e ^ (((U<<8)|i)&MASK))&MASK
    return (e*p)&MASK
def step(H,K,x0,x1,i):
    T=(SBOX[(x1^rol3(K))&0xff]^x0)&0xff
    U=(SBOX[(T^K^i)&0xff]^x1)&0xff
    return fold(H,T,U,i),(T^U)&0xff
def invlast(H16,K15,b30,i=30):
    T15=(SBOX[(0x7d^rol3(K15))&0xff]^b30)&0xff
    U15=(SBOX[(T15^K15^i)&0xff]^0x7d)&0xff
    a=(H16*pinv)&MASK
    a=(a ^ (((U15<<8)|i)&MASK))&MASK
    a=(a*pinv)&MASK
    return (T15 ^ a)&MASK

# fix bytes 0..26 readable; free b27,b28,b29,b30 ; b31='}'
prefix = b"IATCQ{darkc0ver_vm_rev!!AB_"   # need 27 bytes
prefix = prefix[:27]
assert len(prefix)==27, len(prefix)
# forward through pairs 0..12 (bytes 0..25) => H13,K13 ; then need byte26 (index26) for pair13 x0
H=0x811c9dc5; K=0x42
for it in range(13):  # pairs 0..12 -> bytes 0..25
    i=it*2
    H,K=step(H,K,prefix[i],prefix[i+1],i)
H13,K13=H,K
x26=prefix[26]
print("H13=%#x K13=%#x x26=%#x"%(H13,K13,x26),flush=True)

# FORWARD dict over (b27,b28,b29) -> (H15,K15)
print("building forward table (16.7M)...",flush=True)
D={}
for b27 in range(256):
    H14,K14=step(H13,K13,x26,b27,26)
    for b28 in range(256):
        for b29 in range(256):
            H15,K15=step(H14,K14,b28,b29,28)
            D[(H15<<8)|K15]=(b27,b28,b29)
print("forward entries:",len(D),flush=True)

# BACKWARD
print("backward search...",flush=True)
sol=None
for K15 in range(256):
    for b30 in range(256):
        reqH15=invlast(TARGET,K15,b30)
        key=(reqH15<<8)|K15
        v=D.get(key)
        if v is not None:
            b27,b28,b29=v
            sol=(b27,b28,b29,b30)
            print("SOLUTION pair:",sol,flush=True)
            break
    if sol: break

if sol:
    b27,b28,b29,b30=sol
    flag=bytearray(prefix)
    flag+=bytes([b27,b28,b29,b30,ord('}')])
    flag=bytes(flag[:32])
    print("FLAG bytes:",flag,flush=True)
    print("hex:",flag.hex(),flush=True)
    print("len",len(flag),flush=True)
    print("vm(flag)=%#x target=%#x %s"%(VM.vm(flag),TARGET,"MATCH" if VM.vm(flag)==TARGET else "FAIL"),flush=True)
    open("found_flag.bin","wb").write(flag)
else:
    print("no solution in this configuration",flush=True)
