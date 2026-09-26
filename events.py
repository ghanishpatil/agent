import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()
print('=== system_info ===')
for r in cur.execute('select key,value from system_info'):
    print(r)
print('=== runtime_events (all) ===')
for r in cur.execute('select id,event_time_ns,lane,code,detail from runtime_events order by event_time_ns'):
    print(r)
print('=== distinct asset_tags ===')
for r in cur.execute('select asset_tag,count(*) from samples group by asset_tag'):
    print(r)
