from pwn import *
context.arch='amd64'
P = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e = ELF(P, checksec=False)

# --- decrypt sbox+program (LCG) ---
src = e.read(0x20c0, 0x15d)
seed = 0xc0ffee42
dec = bytearray()
for i in range(0x15d):
    seed = (seed*0x41c64e6d + 0x3039) & 0xffffffff
    dec.append(src[i]^((seed>>16)&0xff))
SBOX = bytes(dec[:256])
PROG = bytes(dec[256:])
p = 0x01000193
MASK = 0xffffffff

def rol8(v,n): 
    v&=0xff; return ((v<<n)|(v>>(8-n)))&0xff

def vm(inp):
    assert len(inp)==32
    M=[0]*16
    H=0x811c9dc5
    M[1]=0
    M[3]=0x42
    while True:
        i=M[1]
        # pc6 LDIN M0=IN[M1]
        M[0]=inp[i] if i<32 else 0
        # pc9 M4=M1 ; pc12 M4+=1
        M[4]=(M[1]+1)&0xff
        # pc15 LDIN M2=IN[M4]
        M[2]=inp[M[4]] if M[4]<32 else 0
        # pc18 M5=M3 ; pc21 rol
        M[5]=rol8(M[3],3)
        # pc24 M4=M2 ; pc27 M4^=M5 ; pc30 sbox ; pc33 M4^=M0
        M[4]=M[2]^M[5]
        M[4]=SBOX[M[4]]
        M[4]=M[4]^M[0]
        # pc36 M0=M2 ; pc39 M2=M4
        M[0]=M[2]
        M[2]=M[4]
        # pc42 M5=M3 ; pc45 M5^=M1
        M[5]=M[3]^M[1]
        # pc48 M4=M2 ; pc51 M4^=M5 ; pc54 sbox ; pc57 M4^=M0
        M[4]=M[2]^M[5]
        M[4]=SBOX[M[4]]
        M[4]=M[4]^M[0]
        # pc60 M0=M2 ; pc63 M2=M4
        M[0]=M[2]
        M[2]=M[4]
        # pc66 HASH(M0,M2,M1)
        a=M[0]; b=M[2]
        eax=(a ^ H)&MASK
        eax=(eax*p)&MASK
        ecx=((b<<8)|M[1])&MASK
        eax=(eax^ecx)&MASK
        eax=(eax*p)&MASK
        H=eax
        # pc69 M0^=M2 ; pc72 M3=M0
        M[0]=M[0]^M[2]
        M[3]=M[0]
        # pc75 M1+=2
        M[1]=(M[1]+2)&0xff
        # pc78 M5=0x20 ; pc81 M5^=M1 ; pc84 JNE if (0x20==M1)? flag=(0x20==M1); if flag==0 loop
        if M[1]==0x20:
            break
    return H

if __name__=="__main__":
    print("SBOX==AES:", SBOX[:8].hex())
    test=b"A"*32
    print("hash(A*32)=",hex(vm(test)))
    test2=b"IATCQ{"+b"0"*25+b"}"
    print("hash(fmt)=",hex(vm(test2)))
    print("TARGET   = 0x86d03165")
