import os
d=r'f:\mission-git-hackss\mission-git-hackss\blobs'
# tag byte -> slot mapping (from tagswitch.py)
tag2slot={0x22:8,0x31:2,0x35:10,0x38:1,0x3a:12,0x3c:9,0x46:17,0x49:4,0x6b:6,0x6d:14,
          0x84:3,0x90:11,0x9d:0,0xa9:7,0xc0:18,0xc1:16,0xd2:5,0xd3:19,0xd4:13,0xd5:15}
for n in sorted(os.listdir(d)):
    if not n.endswith('.r9cf'): continue
    b=open(os.path.join(d,n),'rb').read()
    # header: R9CF(4) laneid(1) len(2 LE) then body until crc(2)
    assert b[:4]==b'R9CF'
    laneid=b[4]; length=b[5]|(b[6]<<8)
    body=b[7:length-2]; crc=b[length-2:length]
    # parse [tag][len][payload]
    p=0; recs=[]
    while p < len(body):
        tag=body[p]; ln=body[p+1]; payload=body[p+2:p+2+ln]; p+=2+ln
        recs.append((tag,tag2slot.get(tag,'?'),ln,payload.hex()))
    print(f'--- {n} lane={laneid} len={length} crc={crc.hex()} nrecs={len(recs)} ---')
    # sort by slot
    for tag,slot,ln,pl in sorted(recs,key=lambda x:(x[1] if isinstance(x[1],int) else 99)):
        print(f'   slot {slot:>2} tag={tag:#04x} len={ln} payload={pl}')
