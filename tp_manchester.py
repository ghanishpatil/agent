import sqlite3, statistics
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()

def get_delays(tag):
    rows=cur.execute("SELECT gateway_time_ns-device_time_ns FROM samples WHERE asset_tag=? ORDER BY seq_no",(tag,)).fetchall()
    return [sk/1e6 for (sk,) in rows]

def detrend(vals, win=8):
    out=[]
    for i in range(len(vals)):
        lo=max(0,i-win); hi=min(len(vals),i+win+1)
        out.append(vals[i]-statistics.median(vals[lo:hi]))
    return out

def bits_to_str(bits, msb=True):
    out=bytearray()
    for i in range(0,len(bits)//8*8,8):
        ch=bits[i:i+8]
        if not msb: ch=ch[::-1]
        out.append(int(''.join(map(str,ch)),2))
    return bytes(out)

def anchors(data):
    hits=[]
    for a in [b'HTF',b'flag',b'{',b'DFR9',b'HT',b'TP']:
        i=data.find(a)
        if i>=0: hits.append((a,i))
    return hits

d=get_delays('CR9.FLOW.A4')
res=detrend(d,8)
signs=[1 if r>=0 else 0 for r in res]

# The clock is + - + - ... (period 2). Expected pattern at index i = (i%2==0 ->1 else 0).
# Differential decode: bit = whether sample MATCHES expected clock (0) or BREAKS it (1), or vice versa.
for phase in [0,1]:
    expected=[(1 if (i%2==phase) else 0) for i in range(len(signs))]
    breaks=[1 if signs[i]!=expected[i] else 0 for i in range(len(signs))]
    # Now these 'breaks' occur in pairs (a break in a manchester pair). Try grouping every 2 samples -> 1 bit
    # Option 1: raw breaks as bits
    for pol in [0,1]:
        b=[x^pol for x in breaks]
        for msb in [True,False]:
            data=bits_to_str(b,msb)
            h=anchors(data)
            if h:
                print(f'[raw breaks phase={phase} pol={pol} msb={msb}] {h} head={data[:20]}')
    # Option 2: pair up samples (i,i+1); the excursion magnitude sign of the PAIR
    # bit = sign of (res[2k] - res[2k+1]) -> which of the pair is higher
    pass

# Manchester: each 2 samples = 1 bit. bit=1 if high-then-low, 0 if low-then-high (or vice versa)
for start in [0,1]:
    bits=[]
    i=start
    while i+1 < len(res):
        a,b=res[i],res[i+1]
        bits.append(1 if a> b else 0)
        i+=2
    for pol in [0,1]:
        bb=[x^pol for x in bits]
        for msb in [True,False]:
            data=bits_to_str(bb,msb)
            h=anchors(data)
            if h:
                print(f'[manchester start={start} pol={pol} msb={msb}] {h} head={data[:24]}  ascii={data[:24].decode("latin1")}')
print('done FLOW.A4')
