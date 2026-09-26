import sqlite3
con = sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur = con.cursor()

print('=== system_info (all) ===')
for r in cur.execute("SELECT key,value FROM system_info"):
    print(' ', r[0], '=', r[1])

print('\n=== runtime_events (all 22) ===')
for r in cur.execute("SELECT id,event_time_ns,lane,code,detail FROM runtime_events ORDER BY id"):
    print(' ', r)

print('\n=== distinct asset_tags in samples ===')
for r in cur.execute("SELECT asset_tag, COUNT(*), MIN(seq_no), MAX(seq_no) FROM samples GROUP BY asset_tag"):
    print(' ', r)
