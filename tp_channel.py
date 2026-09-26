import sqlite3
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()

tags=[t[0] for t in cur.execute("SELECT DISTINCT asset_tag FROM samples ORDER BY asset_tag")]

# global dead-zone search across ALL packets (like timeseries trap)
all_delays=[]
per={}
for tag in tags:
    rows=cur.execute("SELECT seq_no, gateway_time_ns-device_time_ns FROM samples WHERE asset_tag=? ORDER BY seq_no",(tag,)).fetchall()
    d=[(s, sk/1e6) for (s,sk) in rows]  # ms
    per[tag]=d
    all_delays += [x for _,x in d]

all_delays.sort()
# find largest gap between consecutive sorted delays (dead zone)
biggest=(0,0,0)
for i in range(len(all_delays)-1):
    gap=all_delays[i+1]-all_delays[i]
    if gap>biggest[0]:
        biggest=(gap, all_delays[i], all_delays[i+1])
print(f'GLOBAL: min={all_delays[0]:.3f} max={all_delays[-1]:.3f}')
print(f'GLOBAL biggest gap = {biggest[0]:.3f}ms between {biggest[1]:.3f} and {biggest[2]:.3f}')

# per-sensor: bimodality check -> find each sensor's biggest internal gap in the middle 90%
print('\nper-sensor dead-zone (biggest gap within delay range):')
for tag in tags:
    vals=sorted(x for _,x in per[tag])
    bg=(0,0,0)
    for i in range(len(vals)-1):
        g=vals[i+1]-vals[i]
        if g>bg[0]: bg=(g,vals[i],vals[i+1])
    print(f'  {tag}: range[{vals[0]:.1f},{vals[-1]:.1f}] biggestgap={bg[0]:.2f} @({bg[1]:.2f},{bg[2]:.2f})')
