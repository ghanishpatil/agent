import vm_model as VM
SBOX=VM.SBOX; p=0x01000193; MASK=0xffffffff
pinv=pow(p,-1,1<<32); TARGET=0x86d03165
def rol3(v): v&=0xff; return ((v<<3)|(v>>5))&0xff
def fold(H,T,U,i):
    e=((H^T)*p)&MASK; e=(e^(((U<<8)|i)&MASK))&MASK; return (e*p)&MASK
def step(H,K,x0,x1,i):
    T=(SBOX[(x1^rol3(K))&0xff]^x0)&0xff; U=(SBOX[(T^K^i)&0xff]^x1)&0xff
    return fold(H,T,U,i),(T^U)&0xff

prefix = b"IATCQ{darkc0ver_vm_rev!!AB_"[:27]   # bytes 0..26
H=0x811c9dc5; K=0x42
for it in range(13):
    i=it*2; H,K=step(H,K,prefix[i],prefix[i+1],i)
H13,K13=H,K; x26=prefix[26]

# FORWARD over (b27,b28,b29) -> (H15,K15), store multiple in dict of lists (keep first)
print("forward build...",flush=True)
D={}
for b27 in range(256):
    H14,K14=step(H13,K13,x26,b27,26)
    for b28 in range(256):
        for b29 in range(256):
            H15,K15=step(H14,K14,b28,b29,28)
            key=(H15<<8)|K15
            if key not in D: D[key]=(b27,b28,b29)
print("forward keys:",len(D),flush=True)

# BACKWARD: free b30,b31. invert iter15 (i=30) with pair(b30,b31):
# H16 = ((H15^T15)*p ^ ((U15<<8)|30))*p ; K15 used as key-in for iter15
# T15 = sbox[b31 ^ rol3(K15)] ^ b30 ; U15 = sbox[T15^K15^30]^b31
# reqH15 = T15 ^ ((TARGET*pinv ^ ((U15<<8)|30))*pinv)
print("backward search...",flush=True)
sols=[]
for K15 in range(256):
    r3=rol3(K15)
    for b31 in range(256):
        for b30 in range(256):
            T15=(SBOX[(b31^r3)&0xff]^b30)&0xff
            U15=(SBOX[(T15^K15^30)&0xff]^b31)&0xff
            a=(TARGET*pinv)&MASK; a=(a^(((U15<<8)|30)&MASK))&MASK; a=(a*pinv)&MASK
            reqH15=(T15^a)&MASK
            v=D.get((reqH15<<8)|K15)
            if v is not None:
                b27,b28,b29=v
                sols.append((b27,b28,b29,b30,b31))
    if len(sols)>2000: break
print("num solutions:",len(sols),flush=True)

def score(t):
    b27,b28,b29,b30,b31=t
    tail=[b27,b28,b29,b30,b31]
    pr=sum(1 for c in tail if 32<=c<127)
    endbrace = 1 if b31==0x7d else 0
    return endbrace*10 + pr
sols.sort(key=score, reverse=True)
for t in sols[:5]:
    b27,b28,b29,b30,b31=t
    flag=bytes(prefix)+bytes([b27,b28,b29,b30,b31])
    ok=VM.vm(flag)==TARGET
    print("cand hex:",flag.hex(),"ascii:","".join(chr(c) if 32<=c<127 else '.' for c in flag),"vm_ok",ok,flush=True)

# pick best and save
b27,b28,b29,b30,b31=sols[0]
flag=bytes(prefix)+bytes([b27,b28,b29,b30,b31])
open("found_flag.bin","wb").write(flag)
print("SAVED best:",flag.hex(),"vm=%#x"%VM.vm(flag),flush=True)
