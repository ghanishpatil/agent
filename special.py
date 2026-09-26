import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()
print('=== quality=128 samples (all 84) ===')
rows=list(cur.execute('''select asset_tag,seq_no,device_time_ns,gateway_time_ns,sensor_value,quality
  from samples where quality=128 order by asset_tag,seq_no'''))
print('count',len(rows))
from collections import defaultdict
bytag=defaultdict(list)
for r in rows:
    bytag[r[0]].append(r)
for tag in sorted(bytag):
    print(tag, 'n=',len(bytag[tag]))
    for r in bytag[tag]:
        print('   seq',r[1],'dev',r[2],'gw',r[3],'val',r[4])
