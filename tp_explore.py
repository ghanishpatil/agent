import sqlite3
DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con = sqlite3.connect(DB)
c = con.cursor()
print("=== master ===")
for r in c.execute("SELECT name,type,rootpage FROM sqlite_master").fetchall():
    print(r)
print("=== system_info ===")
try:
    for r in c.execute("SELECT * FROM system_info").fetchall():
        print(r)
except Exception as e:
    print("err", e)
print("=== runtime_events ===")
try:
    for r in c.execute("SELECT * FROM runtime_events").fetchall():
        print(r)
except Exception as e:
    print("err", e)
print("=== samples schema ===")
print(c.execute("PRAGMA table_info(samples)").fetchall())
print("distinct asset_tag:")
for r in c.execute("SELECT asset_tag, COUNT(*) FROM samples GROUP BY asset_tag").fetchall():
    print(r)
