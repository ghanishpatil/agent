import os
IMG=os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')
def crc16(data):
    c=0xffff
    for b in data:
        c^=(b<<8); c&=0xffff
        for _ in range(8):
            c=((c<<1)^0x1021)&0xffff if c&0x8000 else (c<<1)&0xffff
    return c
TYPE2MOD={0x22:'cf',0x31:'o5',0x35:'sn',0x38:'o4',0x3a:'x3',0x3c:'cr',0x46:'zl',
 0x49:'da',0x6b:'c7',0x6d:'ml',0x84:'dx',0x90:'g8',0x9d:'o3',0xa9:'c8',
 0xc0:'bz',0xc1:'lc',0xd2:'ds',0xd3:'xz',0xd4:'mh',0xd5:'xs'}
SLOT=['o3','o4','o5','dx','da','ds','c7','c8','cf','cr','sn','g8','x3','mh','ml','xs','lc','zl','bz','xz']
d=open(IMG,'rb').read()
offs=[];s=0
while True:
    i=d.find(b'R9CF',s)
    if i<0:break
    offs.append(i);s=i+1
def parse(rec):
    body=rec[8:-2];p=0;out={}
    while p<len(body):
        t=body[p];l=body[p+1];out[TYPE2MOD[t]]=body[p+2:p+2+l];p+=2+l
    return out
for n in [8,9]:
    o=offs[n];ln=d[o+5]|(d[o+6]<<8);rec=d[o:o+ln]
    r=parse(rec)
    print(f'=== rec{n} in SLOT order ===')
    allbytes=b''
    for m in SLOT:
        if m in r:
            v=r[m]
            print(f'  {m:3} = {v.hex():20} ascii={"".join(chr(b) if 32<=b<127 else "." for b in v)}')
    # data carriers cf g8 mh ml in slot order
    carriers=b''.join(r[m] for m in ['cf','g8','mh','ml'])
    print(f'  carriers cf|g8|mh|ml = {carriers.hex()}  -> HTF{{r9_{carriers.hex()}}}')
    print(f'  ascii of carriers: {"".join(chr(b) if 32<=b<127 else "." for b in carriers)}')
