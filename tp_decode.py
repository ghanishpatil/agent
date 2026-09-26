import sqlite3, statistics
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()

def get_delays(tag):
    rows=cur.execute("SELECT seq_no, gateway_time_ns-device_time_ns FROM samples WHERE asset_tag=? ORDER BY seq_no",(tag,)).fetchall()
    return [sk/1e6 for (s,sk) in rows]  # ms, in seq order

def bits_to_bytes(bits, msb=True):
    out=bytearray()
    for i in range(0, len(bits)//8*8, 8):
        chunk=bits[i:i+8]
        if not msb: chunk=chunk[::-1]
        out.append(int(''.join(map(str,chunk)),2))
    return bytes(out)

def find_anchor(data):
    hits=[]
    for anchor in [b'HTF', b'flag', b'FLAG', b'{', b'TP', b'DFR9', b'HTF{', b'R9']:
        idx=data.find(anchor)
        if idx>=0: hits.append((anchor,idx))
    return hits

def printable_runs(data, minlen=4):
    runs=[]; cur_run=b''
    for b in data:
        if 32<=b<127:
            cur_run+=bytes([b])
        else:
            if len(cur_run)>=minlen: runs.append(cur_run)
            cur_run=b''
    if len(cur_run)>=minlen: runs.append(cur_run)
    return runs

def detrend(vals, win=8):
    out=[]
    for i in range(len(vals)):
        lo=max(0,i-win); hi=min(len(vals),i+win+1)
        base=statistics.median(vals[lo:hi])
        out.append(vals[i]-base)
    return out

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2']:
    d=get_delays(tag)
    print(f'\n================ {tag} ================')
    # Method A: threshold at median (absolute)
    med=statistics.median(d)
    for name, series, thr in [('raw@median', d, med)]:
        for pol in [0,1]:
            bits=[(1 if v>=thr else 0) if pol==0 else (0 if v>=thr else 1) for v in series]
            for msb in [True, False]:
                data=bits_to_bytes(bits, msb)
                h=find_anchor(data)
                if h:
                    print(f'  [A {name} pol={pol} msb={msb}] ANCHORS {h}  head={data[:24].hex()}')
    # Method B: detrended residual, threshold 0
    res=detrend(d, 8)
    for pol in [0,1]:
        bits=[(1 if v>=0 else 0) if pol==0 else (0 if v>=0 else 1) for v in res]
        for msb in [True, False]:
            data=bits_to_bytes(bits, msb)
            h=find_anchor(data)
            runs=printable_runs(data,5)
            if h:
                print(f'  [B detrend pol={pol} msb={msb}] ANCHORS {h} head={data[:24].hex()}')
            if runs:
                print(f'  [B detrend pol={pol} msb={msb}] runs>=5: {runs[:6]}')
    # Method C: differential (increase vs decrease from prev)
    diff=[d[i]-d[i-1] for i in range(1,len(d))]
    for pol in [0,1]:
        bits=[(1 if v>=0 else 0) if pol==0 else (0 if v>=0 else 1) for v in diff]
        for msb in [True,False]:
            data=bits_to_bytes(bits,msb)
            h=find_anchor(data)
            if h:
                print(f'  [C diff pol={pol} msb={msb}] ANCHORS {h} head={data[:24].hex()}')
