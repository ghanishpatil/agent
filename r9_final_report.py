#!/usr/bin/env python3
"""
Temporal Paradox - final flag derivation (self-contained).
Rebuilds everything from the disk image + rebuilds the transforms.
"""
import os

IMG = os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')

def crc16_ccitt(data):           # matches ELF func 0x1849
    crc = 0xffff
    for b in data:
        crc ^= (b << 8); crc &= 0xffff
        for _ in range(8):
            crc = ((crc<<1)^0x1021)&0xffff if (crc&0x8000) else (crc<<1)&0xffff
    return crc

TYPE2MOD = {0x22:'cf',0x31:'o5',0x35:'sn',0x38:'o4',0x3a:'x3',0x3c:'cr',0x46:'zl',
            0x49:'da',0x6b:'c7',0x6d:'ml',0x84:'dx',0x90:'g8',0x9d:'o3',0xa9:'c8',
            0xc0:'bz',0xc1:'lc',0xd2:'ds',0xd3:'xz',0xd4:'mh',0xd5:'xs'}
# pipeline slot order (rodata name table @0x22b7)
SLOT = ['o3','o4','o5','dx','da','ds','c7','c8','cf','cr','sn','g8','x3','mh','ml','xs','lc','zl','bz','xz']

def parse(rec):
    body = rec[8:-2]; p=0; out={}
    while p < len(body):
        t=body[p]; l=body[p+1]; out[TYPE2MOD[t]] = body[p+2:p+2+l]; p += 2+l
    return out

d = open(IMG,'rb').read()
offs=[]; s=0
while True:
    i=d.find(b'R9CF',s)
    if i<0: break
    offs.append(i); s=i+1

records={}
for n,o in enumerate(offs[:12]):
    ln = d[o+5] | (d[o+6]<<8)
    rec = d[o:o+ln]
    if crc16_ccitt(rec[:-2]) != ((rec[-2]<<8)|rec[-1]):   # CRC gate: real vs tampered
        continue
    records[n] = parse(rec)

# lane id from o4 ; generation from mh (little-endian counter)
def lane(r): return 1 if int.from_bytes(r['o4'],'little')==0x3e80 else 0
def gen(r):  return int.from_bytes(r['mh'],'little')

print("Valid (CRC-passing) records:", sorted(records))
for n in sorted(records):
    r=records[n]
    print(f"  rec{n}: lane{lane(r)} gen={gen(r)}  cf={r['cf'].hex()} g8={r['g8'].hex()} mh={r['mh'].hex()} ml={r['ml'].hex()}")

# effective lane state = current lane (lane1, loaded latest per rollout.log 03:14) + newest generation
cur_lane = 1
newest = max((n for n in records if lane(records[n])==cur_lane), key=lambda n: gen(records[n]))
r = records[newest]
# flag payload = data modules in pipeline-slot order: cf(8) g8(11) mh(13) ml(14)
payload = r['cf'] + r['g8'] + r['mh'] + r['ml']
print(f"\nEffective record = rec{newest} (lane{cur_lane}, gen {gen(r)})")
print("PRIMARY FLAG:  HTF{r9_%s}" % payload.hex())

# lane0 alternative
newest0 = max((n for n in records if lane(records[n])==0), key=lambda n: gen(records[n]))
r0=records[newest0]
print("ALT (lane0):   HTF{r9_%s}" % (r0['cf']+r0['g8']+r0['mh']+r0['ml']).hex())
