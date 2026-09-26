import sqlite3, datetime
con = sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur = con.cursor()

def to_utc(ns):
    return datetime.datetime.utcfromtimestamp(ns/1e9).strftime('%Y-%m-%d %H:%M:%S.%f')

# Overall time ranges for device vs gateway clocks
cur.execute("SELECT MIN(device_time_ns),MAX(device_time_ns),MIN(gateway_time_ns),MAX(gateway_time_ns) FROM samples")
dmin,dmax,gmin,gmax = cur.fetchone()
print('device range :', to_utc(dmin), '->', to_utc(dmax))
print('gateway range:', to_utc(gmin), '->', to_utc(gmax))

# Clock skew stats
cur.execute("SELECT AVG(gateway_time_ns-device_time_ns), MIN(gateway_time_ns-device_time_ns), MAX(gateway_time_ns-device_time_ns) FROM samples")
print('skew avg/min/max (ns):', cur.fetchone())

# The egress at 03:26:00 UTC. What is that in epoch ns? runtime rollout says 2026-09-09T03:26:00Z
egress = datetime.datetime(2026,9,9,3,26,0,tzinfo=datetime.timezone.utc)
egress_ns = int(egress.timestamp()*1e9)
print('egress_ns (03:26:00Z):', egress_ns, '=', to_utc(egress_ns))

# Note the DB times: convert a sample to see what date they land on
print('sample device example:', to_utc(1788393202324853994))
