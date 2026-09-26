import sqlite3
from collections import defaultdict

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()
rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,val,q in rows:
    by[tag].append((seq,dev,gw,val,q))

# verify device_time at markers
tag='CR9.PRES.A1'
lst=sorted(by[tag])
markers=[s for s in lst if s[4]==0x80]
print("markers for",tag)
for seq,dev,gw,val,q in markers:
    print(f"  seq={seq} dev={dev} dev%1e9={dev%1000000000} gw={gw} gw-dev(ms)={(gw-dev)/1e6:.3f}")

# device time at seq0 for all sensors - is it identical (shared epoch)?
print("\nseq=0 device_time per sensor:")
for tag in sorted(by):
    lst=sorted(by[tag])
    s0=lst[0]
    print(f"  {tag}: dev={s0[1]} gw={s0[2]}")

# The nominal cadence: device_time roughly increments 1e9 per seq (1 sample/sec)
# expected_dev(seq) = dev0 + seq*nominal. Find nominal from markers: (dev[4985]-dev[0])/4985
lst=sorted(by['CR9.PRES.A1'])
dev0=lst[0][1]
m=[s for s in lst if s[4]==0x80]
for i in range(1,len(m)):
    dseq=m[i][0]-m[0][0]; dt=m[i][1]-m[0][1]
    print(f"marker {i}: dseq={dseq} dt_ns={dt} per_seq={dt/dseq:.1f}")
