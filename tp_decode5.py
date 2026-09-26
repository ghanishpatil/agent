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
            bit = bits[i+k] if msb else bits[i+7-k]
            b=(b<<1)|bit
        out.append(b)
    return bytes(out)

def find_magic(bb):
    hits=[]
    for m in [b'HTF',b'TP',b'TRP',b'R9',b'\x78\x9c',b'\x78\xda',b'DFR',b'PK',b'FLAG',b'{']:
        i=bb.find(m)
        if i>=0: hits.append((m,i))
    return hits

def detrend(delay, win):
    out=[]
    n=len(delay)
    for i in range(n):
        a=max(0,i-win); b=min(n,i+win+1)
        window=sorted(delay[a:b])
        med=window[len(window)//2]
        out.append(delay[i]-med)
    return out

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2']:
    lst=sorted(by[tag])
    delay=[(gw-dev)/1e6 for seq,dev,gw,val,q in lst]
    print(f"\n########## {tag} ##########")
    for win in [3,5,8,15,25]:
        res=detrend(delay,win)
        for msb in [True,False]:
            bits=[1 if r>0 else 0 for r in res]
            bb=bits_to_bytes(bits,msb)
            h=find_magic(bb)
            asc=''.join(chr(x) if 32<=x<127 else '.' for x in bb[:24])
            if h:
                print(f"  win={win} msb={msb} MAGIC {h}: {bb[:32].hex()}")
            # also show inverted
            bits=[1 if r<0 else 0 for r in res]
            bb=bits_to_bytes(bits,msb)
            h=find_magic(bb)
            if h:
                print(f"  win={win} msb={msb} INV MAGIC {h}: {bb[:32].hex()}")
        # print a sample regardless
        bits=[1 if r>0 else 0 for r in res]
        bb=bits_to_bytes(bits,True)
        print(f"  win={win} sample: {bb[:16].hex()} |{''.join(chr(x) if 32<=x<127 else '.' for x in bb[:16])}|")
