import sqlite3, statistics
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()

# per-sensor skew (gateway - device) stats
print('=== per-sensor skew (gateway_time_ns - device_time_ns) ===')
tags = [t[0] for t in cur.execute("SELECT DISTINCT asset_tag FROM samples ORDER BY asset_tag").fetchall()]
for tag in tags:
    rows = cur.execute("SELECT gateway_time_ns-device_time_ns FROM samples WHERE asset_tag=? ORDER BY seq_no", (tag,)).fetchall()
    vals=[r[0] for r in rows]
    mean=statistics.mean(vals); sd=statistics.pstdev(vals)
    print(f'{tag}: n={len(vals)} mean={mean/1e6:9.3f}ms std={sd/1e6:8.3f}ms min={min(vals)/1e6:8.3f} max={max(vals)/1e6:9.3f}')
