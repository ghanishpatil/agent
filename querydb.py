import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()
cur.execute("select name,type,sql from sqlite_master")
rows=cur.fetchall()
print('objects',len(rows))
for r in rows:
    print('---',r[1],r[0])
    print(r[2])
print('='*50)
for r in rows:
    if r[1]=='table':
        name=r[0]
        try:
            cur.execute(f'select count(*) from "{name}"')
            cnt=cur.fetchone()[0]
            print(f'TABLE {name}: {cnt} rows')
            cur.execute(f'select * from "{name}" limit 5')
            cols=[c[0] for c in cur.description]
            print('  cols:', cols)
            for row in cur.fetchall():
                print('  ', row)
        except Exception as e:
            print('ERR',name,e)
