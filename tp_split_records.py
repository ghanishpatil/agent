import os
img = os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')
data = open(img,'rb').read()
os.makedirs('tp_records', exist_ok=True)

offs=[]; s=0
while True:
    i=data.find(b'R9CF',s)
    if i<0: break
    offs.append(i); s=i+1

# Only the 12 real records (len=98 => total 100 bytes incl 'R9CF..'? payload len 98 + header)
# header: 'R9CF'(4)+b4(1)+len(2)= 7 bytes; len counts payload; total = 7+len? examine: len=98, dumped 100 bytes ended at crc
# We'll just carve generously: from R9CF to next R9CF (or +104)
for n,o in enumerate(offs):
    end = offs[n+1] if n+1 < len(offs) else o+110
    rec = data[o:end]
    ln = rec[5] | (rec[6]<<8)
    if ln > 4000:  # skip binary false positive
        print(f'skip rec {n} (len={ln}, false positive)')
        continue
    # exact record = 7 header + len payload; but observed 4+1+2=7 then payload... dumped showed 100 bytes for len 98 -> header 4+1+2=7? 7+98=105. Let's carve 4+3+? We'll write from o for (4+3+ln) then +? Actually keep whole gap.
    total = 4 + 3 + ln  # guess
    out = data[o:o+total]
    with open(f'tp_records/rec_{n:02d}.bin','wb') as f:
        f.write(out)
    print(f'rec {n:02d}: off={o} len_field={ln} wrote={len(out)} bytes')
print('done')
