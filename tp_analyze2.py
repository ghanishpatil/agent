import sqlite3, statistics
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()
tags=[t[0] for t in cur.execute("SELECT DISTINCT asset_tag FROM samples ORDER BY asset_tag")]

# 1) quality=0x80 positions per sensor
print('=== quality=0x80 (128) seq positions per sensor ===')
for tag in tags:
    rows=cur.execute("SELECT seq_no FROM samples WHERE asset_tag=? AND quality=128 ORDER BY seq_no",(tag,)).fetchall()
    print(f'  {tag}: {[r[0] for r in rows]}')

def get_delays(tag):
    rows=cur.execute("SELECT gateway_time_ns-device_time_ns FROM samples WHERE asset_tag=? ORDER BY seq_no",(tag,)).fetchall()
    return [sk/1e6 for (sk,) in rows]

def detrend(vals, win=8):
    out=[]
    for i in range(len(vals)):
        lo=max(0,i-win); hi=min(len(vals),i+win+1)
        out.append(vals[i]-statistics.median(vals[lo:hi]))
    return out

def autocorr(res, maxlag=64):
    n=len(res); mean=sum(res)/n
    c0=sum((x-mean)**2 for x in res)
    peaks=[]
    for lag in range(1,maxlag+1):
        c=sum((res[i]-mean)*(res[i+lag]-mean) for i in range(n-lag))/c0
        peaks.append((lag, round(c,3)))
    return peaks

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2']:
    d=get_delays(tag)
    res=detrend(d,8)
    print(f'\n=== {tag} autocorrelation (detrended) ===')
    ac=autocorr(res,32)
    print('  ', ac[:16])
    # sign grid first 200
    signs=''.join('+' if r>=0 else '-' for r in res[:200])
    print('  sign grid[:200]:', signs)
