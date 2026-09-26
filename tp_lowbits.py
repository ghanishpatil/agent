import sqlite3
from collections import defaultdict

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()
rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,val,q in rows:
    by[tag].append((seq,dev,gw,val,q))

# Look at low bits of device_time_ns and gateway_time_ns
tag='CR9.PRES.A1'
lst=sorted(by[tag])
print(f"{tag} first 10 samples:")
for seq,dev,gw,val,q in lst[:10]:
    print(f"  seq={seq} dev={dev} gw={gw} dev%1000={dev%1000} gw%1000={gw%1000} dev%1e6={dev%1000000} val={val} q={hex(q)}")

# Check: are device_time_ns low 3 digits (sub-microsecond) always 0? What granularity?
print("\nGranularity check across all sensors:")
for tag in sorted(by):
    lst=by[tag]
    devmods=set(dev%1000 for seq,dev,gw,val,q in lst[:500])
    gwmods=set(gw%1000 for seq,dev,gw,val,q in lst[:500])
    print(f"  {tag}: dev%1000 distinct={len(devmods)} gw%1000 distinct={len(gwmods)}  dev sample low3={[ (dev%1000) for seq,dev,gw,val,q in lst[:5]]}")
