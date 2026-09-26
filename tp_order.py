import sqlite3
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
cur=con.cursor()

# For the two anomalous sensors, look at whether device_time ordering vs seq_no reveals structure.
# Key idea (Temporal Paradox): device clock had an RX fallback -> the "true" time is gateway; 
# ordering samples by gateway_time vs device_time may differ => that difference = payload.

for tag in ['CR9.FLOW.A4','CR9.TEMP.A2']:
    rows = cur.execute("SELECT seq_no, device_time_ns, gateway_time_ns FROM samples WHERE asset_tag=?", (tag,)).fetchall()
    # order by device_time
    by_dev = sorted(rows, key=lambda r: r[1])
    by_gw  = sorted(rows, key=lambda r: r[2])
    seq_by_dev = [r[0] for r in by_dev]
    seq_by_gw  = [r[0] for r in by_gw]
    # are seq numbers monotonic when sorted by device time? by gateway time?
    def monotonic(lst):
        return all(lst[i]<=lst[i+1] for i in range(len(lst)-1))
    print(f'{tag}: seq monotonic by device_time? {monotonic(seq_by_dev)}  by gateway_time? {monotonic(seq_by_gw)}')
    # how many positions differ between the two orderings
    diff = sum(1 for a,b in zip(seq_by_dev, seq_by_gw) if a!=b)
    print(f'   orderings differ in {diff}/{len(rows)} positions')
    print('   seq by device (first 30):', seq_by_dev[:30])
    print('   seq by gateway(first 30):', seq_by_gw[:30])
