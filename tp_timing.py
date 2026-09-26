import sqlite3
from collections import defaultdict
import statistics

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()

rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,q in rows:
    by[tag].append((seq,dev,gw,q))

print("Per-sensor skew (gateway - device) in ms:")
stats=[]
for tag in sorted(by):
    lst=by[tag]
    skews=[(gw-dev)/1e6 for seq,dev,gw,q in lst]  # ms
    mean=statistics.mean(skews); std=statistics.pstdev(skews)
    mn=min(skews); mx=max(skews)
    stats.append((tag,mean,std,mn,mx,len(skews)))
    print(f"  {tag:14} n={len(skews)} mean={mean:9.3f} std={std:9.3f} min={mn:9.3f} max={mx:9.3f}")

print()
# anomalous = high std
anom=sorted(stats,key=lambda x:-x[2])[:4]
print("Most anomalous by std:", [(a[0],round(a[2],1)) for a in anom])
