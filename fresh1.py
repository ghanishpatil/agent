import sqlite3
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()
tags=[r[0] for r in cur.execute('select distinct asset_tag from samples order by asset_tag')]

def printable(bs):
    return ''.join(chr(c) if 32<=c<127 else '.' for c in bs)

# For each sensor, build byte streams from low bytes of timestamps and value, check for HTF or printable runs
for tag in tags:
    rows=list(cur.execute('select seq_no,device_time_ns,gateway_time_ns,sensor_value from samples where asset_tag=? order by seq_no',(tag,)))
    for field,idx in [('gw&ff',2),('dev&ff',1)]:
        bs=bytes((rows[i][idx])&0xff for i in range(len(rows)))
        if b'HTF' in bs:
            j=bs.find(b'HTF'); print(tag,field,'HTF!',bs[j:j+40]); 
        # check ordered by device_time too
    # also gateway-device skew low byte
    bs2=bytes(((rows[i][2]-rows[i][1])&0xff) for i in range(len(rows)))
    if b'HTF' in bs2:
        j=bs2.find(b'HTF'); print(tag,'skew&ff HTF!',bs2[j:j+40])

# global check: order ALL samples by gateway_time, take low byte
allrows=list(cur.execute('select device_time_ns,gateway_time_ns,sensor_value,asset_tag,quality from samples order by gateway_time_ns'))
bs=bytes(r[1]&0xff for r in allrows)
print('global gw low-byte HTF?', bs.find(b'HTF'))
bs=bytes(r[0]&0xff for r in allrows)
print('global dev low-byte HTF?', bs.find(b'HTF'))
print('done')
