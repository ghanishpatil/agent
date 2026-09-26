import os
img=os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')
d=open(img,'rb').read()

def crc16_ccitt(data):
    # matches asm at 0x1849: init 0xffff, poly 0x1021, process byte<<8, MSB-first, 8 iters
    crc = 0xffff
    for b in data:
        crc ^= (b << 8)
        crc &= 0xffff
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xffff
            else:
                crc = (crc << 1) & 0xffff
    return crc

offs=[]; s=0
while True:
    i=d.find(b'R9CF',s)
    if i<0: break
    offs.append(i); s=i+1

for n,o in enumerate(offs[:12]):
    rec = d[o:o+2]  # placeholder
    ln = d[o+5] | (d[o+6]<<8)
    body = d[o:o+ln-2]
    stored = (d[o+ln-2]<<8) | d[o+ln-1]
    calc = crc16_ccitt(body)
    print(f'rec {n:02d} off={o} len={ln} stored_crc={stored:#06x} calc_crc={calc:#06x} match={stored==calc}')
