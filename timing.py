import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()

for tag in ['CR9.TEMP.A2','CR9.FLOW.A4']:
    rows=list(cur.execute('select seq_no,device_time_ns,gateway_time_ns,sensor_value,quality from samples where asset_tag=? order by device_time_ns',(tag,)))
    print(f'=== {tag} n={len(rows)} ===')
    # skew stats
    skews=[r[2]-r[1] for r in rows]
    neg=[r for r in rows if r[2]<r[1]]
    print('negative-skew count',len(neg))
    # Look at the anomalous ones: are they at regular intervals? extract a bit per sample (neg=1,pos=0)
    bits=''.join('1' if r[2]<r[1] else '0' for r in rows)
    print('bit pattern (first 200):',bits[:200])
    # try decode bits as bytes
    # trim to multiple of 8
    b=bits[:len(bits)//8*8]
    by=bytes(int(b[i:i+8],2) for i in range(0,len(b),8))
    printable=''.join(chr(c) if 32<=c<127 else '.' for c in by)
    print('bits->ascii (first 80):',printable[:80])
    # count runs
    print()
