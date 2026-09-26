import vm_model as VM
SBOX=VM.SBOX; p=0x01000193; MASK=0xffffffff
def rol8(v,n): v&=0xff; return ((v<<n)|(v>>(8-n)))&0xff

# Emulate the VM but LOG every XORCMP comparison (a,b,match) with a step id.
def emulate(inp, collect=True):
    M=[0]*16; H=0x811c9dc5
    M[1]=0; M[3]=0x42
    cmps=[]
    step=0
    while True:
        i=M[1]
        M[0]=inp[i] if i<32 else 0
        M[4]=(M[1]+1)&0xff
        M[2]=inp[M[4]] if M[4]<32 else 0
        M[5]=rol8(M[3],3)
        # pc27 XORCMP M4(=x1) vs M5(=rol3K)
        M[4]=M[2]
        a,b=M[4],M[5]; cmps.append(('c27',step,a==b))
        M[4]^=M[5]
        M[4]=SBOX[M[4]]
        # pc33 XORCMP M4(sbox..) vs M0(x0)
        a,b=M[4],M[0]; cmps.append(('c33',step,a==b))
        M[4]^=M[0]
        M[0]=M[2]; M[2]=M[4]
        M[5]=M[3]
        # pc45 XORCMP M5(K) vs M1(i)
        a,b=M[5],M[1]; cmps.append(('c45',step,a==b))
        M[5]^=M[1]
        M[4]=M[2]
        # pc51 XORCMP M4(T) vs M5(K^i)
        a,b=M[4],M[5]; cmps.append(('c51',step,a==b))
        M[4]^=M[5]
        M[4]=SBOX[M[4]]
        # pc57 XORCMP M4(sbox) vs M0(x1)
        a,b=M[4],M[0]; cmps.append(('c57',step,a==b))
        M[4]^=M[0]
        M[0]=M[2]; M[2]=M[4]
        # HASH
        a2=M[0]; b2=M[2]
        eax=((H^a2)*p)&MASK; ecx=((b2<<8)|M[1])&MASK; eax=((eax^ecx)*p)&MASK; H=eax
        # pc69 XORCMP M0(T) vs M2(U)
        a,b=M[0],M[2]; cmps.append(('c69',step,a==b))
        M[0]^=M[2]; M[3]=M[0]
        M[1]=(M[1]+2)&0xff
        step+=1
        if M[1]==0x20: break
    return H,cmps

PRINT=list(range(0x20,0x7f))
known=bytearray(b'\x00'*32)
known[0:6]=b'IATCQ{'
known[31]=ord('}')
solved=set(range(6))|{31}

# Greedy: make ALL comparisons match, left to right.
for it in range(60):
    H,cmps=emulate(bytes(known))
    total_match=sum(1 for _,_,m in cmps if m)
    if H==0x86d03165:
        print("HASH MATCH with", bytes(known)); break
    # first failing comparison
    fail=next((idx for idx,(name,st,m) in enumerate(cmps) if not m), None)
    if fail is None:
        print("all cmps match but hash != target:", bytes(known), hex(H)); break
    fname,fstep,_=cmps[fail]
    base_before=sum(1 for _,_,m in cmps[:fail] if m)
    best=None
    for pos in range(32):
        if pos in solved: continue
        for v in PRINT:
            t=bytearray(known); t[pos]=v
            _,c2=emulate(bytes(t))
            if fail<len(c2) and c2[fail][2]:  # the failing cmp now matches
                before=sum(1 for _,_,m in c2[:fail] if m)
                if before>=base_before:
                    tot=sum(1 for _,_,m in c2 if m)
                    if best is None or tot>best[0]:
                        best=(tot,pos,v)
        if best is not None:
            break
    if best is None:
        print("stuck at cmp",fname,fstep,"known=",bytes(known)); break
    _,pos,v=best
    known[pos]=v; solved.add(pos)
    print(f"[it{it}] cmp {fname} step{fstep} -> pos{pos}='{chr(v)}'  known={bytes(known)}")

print("final:",bytes(known), "hash",hex(emulate(bytes(known))[0]))
