import sqlite3
from collections import defaultdict
import statistics

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()
rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,q in rows:
    by[tag].append((seq,dev,gw,q))

def hist(vals, nb=40):
    lo=min(vals); hi=max(vals); w=(hi-lo)/nb if hi>lo else 1
    buckets=[0]*nb
    for v in vals:
        b=min(nb-1,int((v-lo)/w))
        buckets[b]+=1
    return lo,hi,w,buckets

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2','CR9.PRES.A1']:
    lst=by[tag]
    skews=[(gw-dev)/1e6 for seq,dev,gw,q in lst]
    print(f"\n=== {tag} ===")
    lo,hi,w,bk=hist(skews,40)
    for i,cnt in enumerate(bk):
        bar='#'*min(80,cnt//20)
        print(f"  [{lo+i*w:9.1f}] {cnt:5} {bar}")

# Now look at DEVICE time delta cadence per sensor (is device clock a metronome?)
print("\n=== device_time_ns delta cadence (first sensor) ===")
for tag in ['CR9.PRES.A1','CR9.FLOW.A4','CR9.TEMP.A2']:
    lst=sorted(by[tag])
    devs=[dev for seq,dev,gw,q in lst]
    deltas=[(devs[i+1]-devs[i])/1e6 for i in range(min(2000,len(devs)-1))]
    from collections import Counter
    cc=Counter(round(d,3) for d in deltas)
    print(f"  {tag}: device delta ms distinct top: {cc.most_common(5)}")
