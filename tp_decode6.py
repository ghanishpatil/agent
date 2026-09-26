import sqlite3
from collections import defaultdict

DB = r'f:\mission-git-hackss\mission-git-hackss\tp_files\var__cache__deltaforge__historian_cache.db'
con=sqlite3.connect(DB); c=con.cursor()
rows=c.execute("SELECT asset_tag, seq_no, device_time_ns, gateway_time_ns, sensor_value, quality FROM samples ORDER BY asset_tag, seq_no").fetchall()
by=defaultdict(list)
for tag,seq,dev,gw,val,q in rows:
    by[tag].append((seq,dev,gw,val,q))

def bits_to_bytes(bits, msb=True):
    out=bytearray()
    for i in range(0,len(bits)//8*8,8):
        b=0
        for k in range(8):
            bit=bits[i+k] if msb else bits[i+7-k]
            b=(b<<1)|bit
        out.append(b)
    return bytes(out)

MAGICS=[b'HTF',b'TP',b'TPX',b'R9',b'DFR',b'\x78\x9c',b'\x78\xda',b'\x1f\x8b',b'PK\x03\x04',b'{"']
def scan(bb):
    res=[]
    for m in MAGICS:
        i=bb.find(m)
        if 0<=i<64: res.append((m,i))
    return res

def linfit_residual(xs, ys):
    n=len(xs)
    mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    slope=sxy/sxx if sxx else 0; inter=my-slope*mx
    return [y-(slope*x+inter) for x,y in zip(xs,ys)]

def moving_med_detrend(vals, win):
    out=[]; n=len(vals)
    for i in range(n):
        a=max(0,i-win); b=min(n,i+win+1)
        w=sorted(vals[a:b]); out.append(vals[i]-w[len(w)//2])
    return out

results=[]
for tag in sorted(by):
    lst=sorted(by[tag])
    seqs=[s[0] for s in lst]
    devs=[s[1] for s in lst]
    gws=[s[2] for s in lst]
    delay=[(gw-dev) for dev,gw in zip(devs,gws)]
    # candidate signals
    signals={}
    signals['gw_grid']=[(gw - (gws[0]+seq*1_000_000_000)) for seq,gw in zip(seqs,gws)]  # gw vs 1s grid
    signals['dev_grid']=[(dev - (devs[0]+seq*1_000_000_000)) for seq,dev in zip(seqs,devs)]
    signals['delay']=delay
    signals['gw_linres']=linfit_residual(seqs,gws)
    for signame,sig in signals.items():
        for win in [4,8,16,32]:
            res=moving_med_detrend(sig,win)
            for msb in (True,False):
                for inv in (False,True):
                    bits=[ (1 if (r>0)!=inv else 0) for r in res]
                    bb=bits_to_bytes(bits,msb)
                    hits=scan(bb)
                    if hits:
                        results.append((tag,signame,win,msb,inv,hits,bb[:32].hex()))

print(f"total magic hits: {len(results)}")
for r in results[:60]:
    print(r)
