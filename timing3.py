import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()

for tag in ['CR9.TEMP.A2','CR9.FLOW.A4']:
    rows=list(cur.execute('select seq_no,device_time_ns,gateway_time_ns from samples where asset_tag=? order by seq_no',(tag,)))
    anom=[r[0] for r in rows if r[2]<r[1]]  # seq_no of anomalous
    print(f'=== {tag} anomalous count={len(anom)} ===')
    print('anom seq positions first 60:', anom[:60])
    # gaps between consecutive anomalous seqs
    gaps=[anom[i]-anom[i-1] for i in range(1,len(anom))]
    print('gaps first 60:', gaps[:60])
    # runs of consecutive anomalous
    runs=[]
    i=0
    while i<len(anom):
        j=i
        while j+1<len(anom) and anom[j+1]==anom[j]+1: j+=1
        runs.append(anom[j]-anom[i]+1); i=j+1
    print('run lengths first 60:', runs[:60])
    print('num runs', len(runs))
    print()
