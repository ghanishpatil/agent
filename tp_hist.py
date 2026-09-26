import sqlite3
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2']:
    rows = cur.execute("SELECT seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples WHERE asset_tag=? ORDER BY seq_no", (tag,)).fetchall()
    skews=[(g-d)/1e6 for (s,d,g,v,q) in rows]
    print(f'=== {tag} n={len(skews)} ===')
    # histogram in 500ms buckets
    buckets={}
    for sk in skews:
        b=int(sk//500)*500
        buckets[b]=buckets.get(b,0)+1
    for b in sorted(buckets):
        print(f'  [{b:8}..{b+500:8}) ms : {buckets[b]}')
    # first 40 skews in seq order
    print('  first 40 skews (ms):', [round(x,1) for x in skews[:40]])
