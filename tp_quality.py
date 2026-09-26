import sqlite3
from collections import defaultdict, Counter

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()

# distinct quality values
print("quality distribution overall:")
for r in c.execute("SELECT quality, COUNT(*) FROM samples GROUP BY quality").fetchall():
    print("  q=0x%02x count=%d"%(r[0],r[1]))

rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,val,q in rows:
    by[tag].append((seq,dev,gw,val,q))

print("\nPer-sensor: samples with quality != 0xc0 (the marked ones):")
for tag in sorted(by):
    marked=[(seq,dev,gw,val,q) for seq,dev,gw,val,q in by[tag] if q!=0xc0]
    qs=[q for *_,q in marked]
    seqs=[seq for seq,*_ in marked]
    print(f"  {tag:14} n_marked={len(marked)} qualities={[hex(x) for x in qs]}")
    print(f"        seqs={seqs}")
