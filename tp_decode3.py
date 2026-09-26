import sqlite3
from collections import defaultdict

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()
rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,val,q in rows:
    by[tag].append((seq,dev,gw,val,q))

# registration order by seq0 device offset
order=sorted(by, key=lambda t: sorted(by[t])[0][1])
print("Registration order (by seq0 device time):")
for t in order:
    print(f"  {t}: seq0_dev_offset_ms={ (sorted(by[t])[0][1] % 1000000000)/1e6 :.1f}")

# For carrier sensors, gateway_time at seq0 is round -> gateway modulated
# The device clock IS a clean 1s metronome (dev = dev0 + seq*1e9 + noise? check FLOW)
def analyze(tag):
    lst=sorted(by[tag])
    dev0=lst[0][1]
    print(f"\n=== {tag} ===  dev0={dev0}")
    # is device a clean metronome? dev - (dev0 + seq*1e9)
    devresid=[(dev - (dev0 + seq*1_000_000_000)) for seq,dev,gw,val,q in lst]
    print("  device residual (dev - dev0 - seq*1e9) ns, first 12:", [f"{r/1e6:.3f}ms" for r in devresid[:12]])
    print("  device residual stats: min=%.3f max=%.3f"%(min(devresid)/1e6,max(devresid)/1e6))
    # gateway relative to device
    delay=[(gw-dev)/1e6 for seq,dev,gw,val,q in lst]
    print("  gw-dev delay first 12 ms:", [f"{d:.3f}" for d in delay[:12]])
    return lst

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2','CR9.PRES.A1']:
    analyze(tag)
