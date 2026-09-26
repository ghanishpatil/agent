import sqlite3, statistics
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()

def get(tag, col):
    return [r[0] for r in cur.execute(f"SELECT {col} FROM samples WHERE asset_tag=? ORDER BY seq_no",(tag,)).fetchall()]

tag='CR9.TEMP.A2'
dev=get(tag,'device_time_ns'); gw=get(tag,'gateway_time_ns')
delay=[(gw[i]-dev[i])/1e6 for i in range(len(dev))]

def detrend(vals, win):
    out=[]
    for i in range(len(vals)):
        lo=max(0,i-win); hi=min(len(vals),i+win+1)
        out.append(vals[i]-statistics.median(vals[lo:hi]))
    return out

res=detrend(delay,8)
print('TEMP.A2 detrended residual (first 96), rounded:')
print([round(x,1) for x in res[:96]])
print('\nresidual stats: min=%.1f max=%.1f'%(min(res),max(res)))
# histogram fine
import collections
h=collections.Counter(round(x/5)*5 for x in res)
print('histogram (5ms bins):')
for k in sorted(h): print(f'  {k:6}: {h[k]}')
