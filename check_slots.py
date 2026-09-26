import struct, sqlite3
vals_hex = ['cc583f4d','fb4eea48','f7535567','a68d20eb','40c8cc59','24ebc118',
            '990bdb03','fd28d642','58804bc5','5e14b0ed','50460000','803e0000',
            'e2aa95907ea02d1a','b2bd','1b37','1c37','ec3e']
for h in vals_hex:
    b=bytes.fromhex(h)
    line=f'{h}: '
    if len(b)==4:
        le=struct.unpack('<I',b)[0]; be=struct.unpack('>I',b)[0]
        fle=struct.unpack('<f',b)[0]; fbe=struct.unpack('>f',b)[0]
        line+=f'u32le={le} u32be={be} f32le={fle:.6g} f32be={fbe:.6g}'
    elif len(b)==8:
        le=struct.unpack('<Q',b)[0]; dle=struct.unpack('<d',b)[0]
        line+=f'u64le={le} f64le={dle:.6g}'
    elif len(b)==2:
        line+=f'u16le={struct.unpack("<H",b)[0]} u16be={struct.unpack(">H",b)[0]}'
    print(line)

print('--- check against DB device_time_ns/gateway_time_ns low dwords and seq ---')
con=sqlite3.connect(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db')
cur=con.cursor()
# does any of these 4-byte LE dwords equal (device_time_ns & 0xffffffff) or seq or value bits?
for h in ['cc583f4d','fb4eea48','f7535567','a68d20eb','40c8cc59','24ebc118','990bdb03','fd28d642','58804bc5','5e14b0ed']:
    le=struct.unpack('<I',bytes.fromhex(h))[0]
    # search device/gateway low32
    r=cur.execute('select asset_tag,seq_no from samples where (device_time_ns & 4294967295)=?',(le,)).fetchall()
    r2=cur.execute('select asset_tag,seq_no from samples where (gateway_time_ns & 4294967295)=?',(le,)).fetchall()
    print(h,'dev_low32_match',r[:3],'gw_low32_match',r2[:3])
