#!/usr/bin/env python3
"""
Standalone reimplementation of /usr/local/sbin/r9sampler.

Behaviour recovered by static analysis + Unicorn validation:
  * main(argc, argv): opens argv[1] "rb", reads FIRST 0x10000 bytes into a buffer.
  * Scans buffer for records beginning with magic "R9CF".
  * Record layout:
        off 0 : "R9CF"              (4 bytes magic)
        off 4 : version (0x01)
        off 5 : length low byte
        off 6 : length high byte    -> total_len = lo | (hi<<8)
        off 7 : reserved (0x00)
        off 8.. : TLV entries  [code(1), count(1), payload(count)] repeated
        last 2 bytes : CRC16 (big-endian) over record[0 .. total_len-2]
  * A record is ACCEPTED iff CRC matches. accepted counter += 1 per accepted record.
  * For each accepted record, every TLV entry is stored into global tables:
        slot_bytes[module_idx*12 .. +count] = payload
        slot_count[module_idx]              = count
    (code byte -> module_idx via the recovered jump-table map BYTE2IDX)
  * After the loop, a 'guard' byte is computed from FIXED constants plus ONE
    data byte: slot_bytes[2*12] i.e. module o5's first payload byte.
  * Prints:  accepted=%u guard=%02x
"""
M32=0xffffffff
MODS="o3 o4 o5 dx da ds c7 c8 cf cr sn g8 x3 mh ml xs lc zl bz xz".split()
# recovered raw-code-byte -> module index (0..19)
BYTE2IDX={0x22:8,0x31:2,0x35:10,0x38:1,0x3a:12,0x3c:9,0x46:17,0x49:4,0x6b:6,
 0x6d:14,0x84:3,0x90:11,0x9d:0,0xa9:7,0xc0:18,0xc1:16,0xd2:5,0xd3:19,0xd4:13,0xd5:15}

def crc16(buf,n):                      # sub_1849 (poly 0x1021, init 0xffff, MSB-first)
    c=0xffffffff
    for i in range(n):
        c=(c^((buf[i]<<8)&M32))&M32
        for _ in range(8):
            two=(c*2)&M32
            c=two if (c&0x8000)==0 else (two^0x1021)&M32
    return c&0xffff

# ---- guard helper functions (verified against binary via Unicorn) ----
def _f1273(edi,esi,edx,ecx,r8):        # sub_1273
    if edi==1:
        e=((ecx>>8)^edx^r8^esi)&0xff; return 0xa7 if e==0 else e
    edx=(edx^ecx^esi)&M32; e=edx^r8
    return 0x6d2b79f5 if edx==r8 else e&M32
def _fnv(x):                           # sub_1249
    a=((x<<13)&M32)^x; b=((a>>17)&M32)^a; return (((b<<5)&M32)^b)&M32
def _h12ab(edi,esi,val):               # sub_12ab
    if edi==1:
        c=val&M32; e=(c>>1)&M32; si=(esi&0xff)^e; e=si if c&1 else e; return e&0xff,e&M32
    h=_fnv(val); return h&1,h
def _m12ef(edi,esi,edx,ecx):           # sub_12ef
    if edi==1: return (edx^esi)%ecx if ecx else 0
    if edi==2: return (esi+edx)%ecx if ecx else 0
    return (ecx-edx+esi)%ecx if ecx else 0
def _emit8(edi,esi):                   # sub_1362
    c=(edi>>3)&1; d=(edi>>2)&1; s=edi&1; e=(edi>>1)&1
    o=[(d^c^s)&0xff,(e^c^s)&0xff,c,(e^d^s)&0xff,d,e,s,0]
    if esi==8:
        x=0
        for i in range(7): x^=o[i]
        o[7]=x&0xff
    return o
def _p131d(buf,n,mode):                # sub_131d
    r=0
    for i in range(n):
        sh=(n-1-i) if mode==1 else i
        r|=(buf[i]&1)<<sh
    return r&M32
def _g1898(edi,esi):                   # sub_1898 (tag switch)
    T={0:{4:1,5:2,3:0},1:{2:4,3:5,1:3},2:{7:6,8:7},3:{2:9,3:0xa,1:8},
       4:{1:0xb,2:0xc},5:{1:0xd,2:0xe},6:{1:0xf,2:0x10},7:{2:0x12,3:0x13,1:0x11}}
    return T.get(edi,{}).get(esi,0x63) if edi<=7 else 0x63

def r9sampler(file_bytes):
    buf=file_bytes[:0x10000]                 # binary only reads first 64 KiB
    n=len(buf)
    slot_bytes=bytearray(20*12); slot_count=bytearray(20)
    accepted=0; rbx=0
    while rbx < n-0xa:
        if buf[rbx:rbx+4]!=b"R9CF": rbx+=1; continue
        tl=(buf[rbx+6]<<8)|buf[rbx+5]
        if tl<=9 or rbx+tl>n: rbx+=1; continue
        rec=buf[rbx:rbx+tl]
        if (crc16(rec,tl-2)) != ((rec[tl-2]<<8)|rec[tl-1]): rbx+=1; continue
        # accepted record: store all TLV entries
        if tl>0xa:
            code=rec[8]; cnt=rec[9]; r14=cnt+0xa; esi=0xa
            if tl>=r14:
                while True:
                    idx=BYTE2IDX.get(code)
                    if idx is not None and idx<=0x13 and cnt<=0xc:
                        slot_bytes[idx*12:idx*12+cnt]=rec[esi:esi+cnt]
                        slot_count[idx]=cnt
                    esi2=r14+2
                    if esi2>=tl: break
                    code=rec[r14]; cnt=rec[r14+1]; r14=esi2+cnt
                    if tl>=r14: esi=esi2
                    else: break
        accepted+=1; rbx+=1
    # ---- guard ----
    v48=_f1273(2,0x19,0x37,0x51,0)
    b40=_emit8(9,8)
    v44=(_g1898(0,slot_bytes[2*12])^0x4f)&M32
    ebx,_=_h12ab(2,0x51,v48)
    r12=_m12ef(2,1,2,0x10)
    ebx=((((ebx^_p131d(b40,4,1))^v44)^r12)^0x6f)&0xff
    return accepted, ebx, slot_bytes, slot_count

if __name__=="__main__":
    import sys
    data=open(sys.argv[1],"rb").read() if len(sys.argv)>1 else b""
    acc,guard,_,_=r9sampler(data)
    print(f"accepted={acc} guard={guard:02x}")
