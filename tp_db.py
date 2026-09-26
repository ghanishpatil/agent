import sqlite3
con = sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur = con.cursor()
cur.execute("SELECT name,type,sql FROM sqlite_master")
for row in cur.fetchall():
    print(row[0], '|', row[1])
    print('   SQL:', row[2])
print('='*60)
# For each table, show columns and row count and a few rows
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
for t in tables:
    print(f'\n### TABLE {t} ###')
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        cnt = cur.fetchone()[0]
        print('rows:', cnt)
        cur.execute(f'PRAGMA table_info("{t}")')
        cols = cur.fetchall()
        print('cols:', [c[1] for c in cols])
        cur.execute(f'SELECT * FROM "{t}" LIMIT 5')
        for r in cur.fetchall():
            print('  ', r)
    except Exception as e:
        print('ERR', e)
