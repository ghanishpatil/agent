import sqlite3, struct
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()

# Order sensors by their code A1..A6,B1..B6,C1,C2 (natural flag order?)
tags=[r[0] for r in cur.execute('select distinct asset_tag from samples')]
def code(t): return t.split('.')[-1]
order = sorted(tags, key=lambda t:(code(t)[0], code(t)[1]))
print('code order:', [code(t) for t in order])

# Hypothesis A: byte = low byte of (gateway-device skew) of seq 0
print('--- seq0 skew low bytes ---')
bs=[]
for t in order:
    r=cur.execute('select gateway_time_ns-device_time_ns from samples where asset_tag=? and seq_no=0',(t,)).fetchone()
    bs.append(r[0]&0xff)
print(bytes(bs).hex())

# Hypothesis B: sensor_value of seq0 -> IEEE754 double bytes, take one
print('--- seq0 value doubles ---')
for t in order:
    v=cur.execute('select sensor_value from samples where asset_tag=? and seq_no=0',(t,)).fetchone()[0]
    print(code(t), v, struct.pack('<d',v).hex())
