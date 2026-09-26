import sqlite3
from collections import defaultdict

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()
rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,val,q in rows:
    by[tag].append((seq,dev,gw,val,q))

def bits_to_bytes(bits):
    out=bytearray()
    for i in range(0,len(bits)//8*8,8):
        b=0
        for k in range(8): b=(b<<1)|bits[i+k]
        out.append(b)
    return bytes(out)

def try_decode(tag, verbose=False):
    lst=sorted(by[tag])
    delay=[(gw-dev)/1e6 for seq,dev,gw,val,q in lst]
    n=len(delay)
    # markers split into segments
    markers=[i for i,(seq,dev,gw,val,q) in enumerate(lst) if q==0x80]
    # Look at delay distribution to find threshold via median
    sd=sorted(delay)
    med=sd[len(sd)//2]
    # find biggest gap in a central window
    print(f"\n=== {tag} n={n} markers_idx={markers} median_delay={med:.2f}")
    # histogram
    lo=min(delay); hi=max(delay)
    print(f"  delay range {lo:.2f}..{hi:.2f}")
    # Attempt: threshold = median, bit=1 if delay>med
    for thr_name, thr in [('median',med)]:
        bits=[1 if d>thr else 0 for d in delay]
        bb=bits_to_bytes(bits)
        print(f"  thr={thr_name}({thr:.1f}) first16 bytes: {bb[:16].hex()} ascii={''.join(chr(x) if 32<=x<127 else '.' for x in bb[:16])}")
        bits2=[1 if d<thr else 0 for d in delay]  # inverted
        bb2=bits_to_bytes(bits2)
        print(f"     inverted first16: {bb2[:16].hex()} ascii={''.join(chr(x) if 32<=x<127 else '.' for x in bb2[:16])}")

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2']:
    try_decode(tag)

# FLOW.A4 has interleaved cadence - separate even/odd samples
print("\n\n=== FLOW.A4 de-interleaved ===")
lst=sorted(by['CR9.FLOW.A4'])
delay=[(gw-dev)/1e6 for seq,dev,gw,val,q in lst]
for phase in [0,1]:
    sub=delay[phase::2]
    sd=sorted(sub); med=sd[len(sd)//2]
    bits=[1 if d>med else 0 for d in sub]
    bb=bits_to_bytes(bits)
    print(f"phase{phase} med={med:.1f} n={len(sub)}: {bb[:20].hex()} | {''.join(chr(x) if 32<=x<127 else '.' for x in bb[:20])}")
    bits=[1 if d<med else 0 for d in sub]
    bb=bits_to_bytes(bits)
    print(f"   inv: {bb[:20].hex()} | {''.join(chr(x) if 32<=x<127 else '.' for x in bb[:20])}")
