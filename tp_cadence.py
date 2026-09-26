import sqlite3
from collections import Counter
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()
tags=[t[0] for t in cur.execute("SELECT DISTINCT asset_tag FROM samples ORDER BY asset_tag")]

for clock in ['device_time_ns','gateway_time_ns']:
    print(f'\n########## cadence of {clock} (delta between consecutive seq) ##########')
    for tag in tags:
        rows=cur.execute(f"SELECT seq_no,{clock} FROM samples WHERE asset_tag=? ORDER BY seq_no",(tag,)).fetchall()
        deltas=[(rows[i+1][1]-rows[i][1]) for i in range(len(rows)-1)]
        # distinct deltas
        c=Counter(deltas)
        distinct=len(c)
        common=c.most_common(4)
        print(f'  {tag}: n={len(deltas)} distinct_deltas={distinct} top={[(round(d/1e6,3),cnt) for d,cnt in common]}')
