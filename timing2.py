import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()

tags=[r[0] for r in cur.execute('select distinct asset_tag from samples order by asset_tag')]

# For each sensor: examine gateway-device skew distribution
for tag in tags:
    rows=list(cur.execute('select seq_no,device_time_ns,gateway_time_ns from samples where asset_tag=? order by seq_no',(tag,)))
    skews=[r[2]-r[1] for r in rows]
    neg=[s for s in skews if s<0]
    mn=min(skews); mx=max(skews)
    print(f'{tag}: n={len(rows)} skew_min={mn} skew_max={mx} neg={len(neg)}')

print()
# Focus TEMP.A2: dump negative-skew samples ordered by seq, show device-gateway delta
print('=== CR9.TEMP.A2 negative-skew (device-gateway) deltas ===')
rows=list(cur.execute("select seq_no,device_time_ns,gateway_time_ns from samples where asset_tag='CR9.TEMP.A2' order by seq_no"))
negrows=[(r[0],r[1]-r[2]) for r in rows if r[2]<r[1]]
print('count',len(negrows))
deltas=[d for _,d in negrows]
print('deltas first 40:', deltas[:40])
# are deltas clustered around specific values?
from collections import Counter
# scale to ms
print('delta range', min(deltas), max(deltas))
