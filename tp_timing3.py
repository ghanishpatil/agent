import sqlite3
from collections import defaultdict
import statistics

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()
rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,val,q in rows:
    by[tag].append((seq,dev,gw,val,q))

# For normal sensors, look at whole-stream global dead zone (like sibling)
# Collect skew for the 12 normal sensors, check for empty dead-zone
normal=['CR9.COOL.C1','CR9.CURR.B2','CR9.LEVL.A5','CR9.LOAD.C2','CR9.PRES.A1','CR9.RPM_.A6','CR9.SPED.B6','CR9.TENS.B5','CR9.THCK.B4','CR9.TORQ.B1','CR9.VIBR.A3','CR9.VOLT.B3']

# per-sensor: subtract sensor's own min (local baseline) -> relative skew
print("=== Per normal sensor: relative skew (skew - local_min), look for bimodal ===")
for tag in normal:
    lst=sorted(by[tag])
    skews=[(gw-dev)/1e6 for seq,dev,gw,val,q in lst]
    base=min(skews)
    rel=[s-base for s in skews]
    # count in bands: how many are "elevated" (rel > some cut)?
    hi=[r for r in rel if r>50]
    print(f"  {tag}: base={base:.1f} n_rel>50ms={len(hi)}  max_rel={max(rel):.1f}")

# Global dead zone across all normal sensors (absolute skew minus per-sensor base)
allrel=[]
for tag in normal:
    lst=sorted(by[tag])
    skews=[(gw-dev)/1e6 for seq,dev,gw,val,q in lst]
    base=min(skews)
    allrel.extend(s-base for s in skews)
allrel.sort()
# find gaps
print("\n=== Global relative-skew gap analysis (normal sensors) ===")
# look at sorted, find largest empty gap in low region
prev=allrel[0]; maxgap=0; gaploc=None
for v in allrel:
    if v-prev>maxgap:
        maxgap=v-prev; gaploc=(prev,v)
    prev=v
print(f"largest gap: {maxgap:.3f} ms between {gaploc}")
# distribution around threshold candidates
import bisect
for cut in [20,30,40,50,60,70,80,100]:
    below=bisect.bisect_left(allrel,cut)
    print(f"  cut={cut}: below={below} above={len(allrel)-below}")
