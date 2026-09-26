import sqlite3
c = sqlite3.connect('historian_cache.db')
print("=== system_info ===")
for k, v in c.execute("select key, value from system_info"):
    print(f"{k!r}: {v!r}")

print("\n=== runtime_events (ordered by event_time_ns) ===")
for row in c.execute("select id,event_time_ns,lane,code,detail from runtime_events order by event_time_ns"):
    print(row)

print("\n=== distinct asset_tags ===")
tags = [r[0] for r in c.execute("select distinct asset_tag from samples order by asset_tag")]
print(tags, len(tags))

print("\n=== per-tag seq_no range and count ===")
for t in tags:
    mn, mx, n = c.execute("select min(seq_no),max(seq_no),count(*) from samples where asset_tag=?", (t,)).fetchone()
    print(f"{t}: seq {mn}..{mx} count={n}")
