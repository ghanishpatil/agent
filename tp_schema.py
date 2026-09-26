import sqlite3
c = sqlite3.connect('historian_cache.db')
print("=== TABLES ===")
for name, sql in c.execute("select name, sql from sqlite_master where type='table'"):
    print(f"\n--- {name} ---")
    print(sql)
print("\n=== ROW COUNTS ===")
for (name,) in c.execute("select name from sqlite_master where type='table'"):
    try:
        n = c.execute(f"select count(*) from '{name}'").fetchone()[0]
        print(f"{name}: {n}")
    except Exception as e:
        print(f"{name}: ERR {e}")
