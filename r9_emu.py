#!/usr/bin/env python3
"""Full faithful emulation of r9sampler main(), fed a buffer."""
M32=0xffffffff
mods="o3 o4 o5 dx da ds c7 c8 cf cr sn g8 x3 mh ml xs lc zl bz xz".split()
BYTE2IDX={0x22:8,0x31:2,0x35:10,0x38:1,0x3a:12,0x3c:9,0x46:17,0x49:4,0x6b:6,
 0x6d:14,0x84:3,0x90:11,0x9d:0,0xa9:7,0xc0:18,0xc1:16,0xd2:5,0xd3:19,0xd4:13,0xd5:15}

def crc16(buf,n):
    eax=0xffffffff
    for i in range(n):
        eax=(eax^((buf[i]<<8)&M32))&M32
        for _ in range(8):
            two=(eax*2)&M32
            eax=two if (eax&0x8000)==0 else (two^0x1021)&M32
    return eax&0xffff

def f_1273(edi,esi,edx,ecx,r8d):
    if edi==1:
        eax=((ecx>>8)^edx^r8d^esi)&0xff
        return 0xa7 if eax==0 else eax
    edx=(edx^ecx^esi)&M32; eax=edx^r8d
    if edx==r8d: eax=0x6d2b79f5
    return eax&M32
def fnv_1249(x):
    eax=((x<<13)&M32)^x; edx=((eax>>17)&M32)^eax; eax=((edx<<5)&M32)^edx
    return eax&M32
def h_12ab(edi,esi,val):
    if edi==1:
        c=val&M32; edx=(c>>1)&M32; si=(esi&0xff)^edx
        edx2=si if (c&1) else edx
        return (edx2&0xff, edx2&M32)
    h=fnv_1249(val); return (h&1,h&M32)
def m_12ef(edi,esi,edx,ecx):
    if edi==1: return ((edx^esi)%ecx) if ecx else 0
    if edi==2: return ((esi+edx)%ecx) if ecx else 0
    return ((ecx-edx+esi)%ecx) if ecx else 0
def emit8_1362(edi,esi):
    out=[0]*8; c=(edi>>3)&1; d=(edi>>2)&1; s=edi&1; e=(edi>>1)&1
    out[0]=(d^c^s)&0xff; out[1]=(e^c^s)&0xff; out[2]=c; out[3]=(e^d^s)&0xff
    out[4]=d; out[5]=e; out[6]=s
    if esi==8:
        cl=0
        for i in range(7): cl^=out[i]
        out[7]=cl&0xff
    return out
def p_131d(buf,n,mode):
    r8=0
    for i in range(n):
        bit=buf[i]&1; shift=(n-1-i) if mode==1 else i
        r8|=(bit<<shift)
    return r8&M32
def g_1898(edi,esi):
    T={0:{4:1,5:2,3:0},1:{2:4,3:5,1:3},2:{7:6,8:7},3:{2:9,3:0xa,1:8},
       4:{1:0xb,2:0xc},5:{1:0xd,2:0xe},6:{1:0xf,2:0x10},7:{2:0x12,3:0x13,1:0x11}}
    return T.get(edi,{}).get(esi,0x63) if edi<=7 else 0x63

def run(buf, verbose=False):
    n=len(buf)
    slot_bytes=bytearray(20*12); slot_count=bytearray(20)
    accepted=0
    rbx=0; limit=n-0xa
    while rbx<limit:
        if buf[rbx:rbx+4]!=b"R9CF": rbx+=1; continue
        total_len=(buf[rbx+6]<<8)|buf[rbx+5]
        if total_len<=9: rbx+=1; continue
        if rbx+total_len>n: rbx+=1; continue
        rec=buf[rbx:rbx+total_len]
        c=crc16(rec,total_len-2); emb=(rec[total_len-2]<<8)|rec[total_len-1]
        if (c&0xffff)!=(emb&0xffff): rbx+=1; continue
        # valid record -> parse TLV entries, then accepted++
        if total_len>0xa:
            code=rec[8]; cnt=rec[9]; r14=cnt+0xa
            if total_len>=r14:
                esi=0xa
                while True:
                    idx=BYTE2IDX.get(code)
                    if idx is not None and idx<=0x13 and cnt<=0xc:
                        for k in range(cnt): slot_bytes[idx*12+k]=rec[esi+k]
                        slot_count[idx]=cnt
                    esi2=r14+2
                    if esi2>=total_len: break
                    code=rec[r14]; cnt=rec[r14+1]
                    r14=esi2+cnt
                    if total_len>=r14:
                        esi=esi2; continue
                    else: break
        accepted+=1
        rbx+=1
    # ---- guard computation (0x1b80..0x1c30) ----
    v48=f_1273(2,0x19,0x37,0x51,0)          # [rbp-0x48]
    buf40=emit8_1362(9,8)                    # [rbp-0x40], 8 bytes
    slot2b0=slot_bytes[0x18]                 # byte ptr [rip+0x24b1]=0x4078 = slot idx2 (o5) byte0
    a=g_1898(0, slot2b0)                     # xor 0x4f
    v44=(a^0x4f)&M32
    ebx,newv48=h_12ab(2,0x51,v48)            # rdx=&[rbp-0x48]; updates v48; ebx=ret
    r12=m_12ef(2,1,2,0x10)                   # (1+2)%16=3
    pd=p_131d(buf40,4,1)                     # pack 4 bits mode1
    ebx=(ebx^pd)&M32
    ebx=(ebx^v44)&M32
    ebx=(ebx^r12)&M32
    ebx=(ebx^0x6f)&M32
    guard=ebx&0xff
    return accepted, guard, slot_bytes, slot_count

if __name__=="__main__":
    db=open(r"f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db","rb").read()
    acc,guard,sb,sc=run(db)
    print(f"WHOLE DB: accepted={acc} guard={guard:02x}")
    print(f"HTF{{r9_{guard:02x}}}")
