import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()

tags=[r[0] for r in cur.execute('select distinct asset_tag from samples order by asset_tag')]
print('tags order:', tags)

# For each sensor: count "temporal paradox" inversions = pairs where device order != gateway order
# Specifically count samples whose gateway_time is out of order relative to device_time sequence
for tag in tags:
    rows=list(cur.execute('select seq_no, device_time_ns, gateway_time_ns, quality from samples where asset_tag=? order by device_time_ns',(tag,)))
    gw=[r[2] for r in rows]
    # count adjacent inversions in gateway when sorted by device
    inv=sum(1 for i in range(1,len(gw)) if gw[i]<gw[i-1])
    # count negative skew
    neg=sum(1 for r in rows if r[2]<r[1])
    print(f'{tag}: n={len(rows)} adj_gw_inversions={inv} negative_skew={neg}')
