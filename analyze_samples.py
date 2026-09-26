import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()

# quality distribution
print('=== quality distribution ===')
for r in cur.execute('select quality,count(*) from samples group by quality order by count(*) desc'):
    print(r)

print('=== per tag: seq range, time range ===')
for r in cur.execute('''select asset_tag, min(seq_no), max(seq_no), count(distinct seq_no),
   min(device_time_ns), max(device_time_ns) from samples group by asset_tag'''):
    print(r)

# check device vs gateway skew stats for one tag
print('=== skew (gateway-device) for CR9.PRES.A1, first 20 by device_time ===')
for r in cur.execute('''select seq_no, device_time_ns, gateway_time_ns, gateway_time_ns-device_time_ns as skew, sensor_value, quality
   from samples where asset_tag='CR9.PRES.A1' order by device_time_ns limit 20'''):
    print(r)
