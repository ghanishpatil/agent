l0=bytes.fromhex('43395452000404060301030200040301000205010003020a020300010b030200010f030102004792')
l1=bytes.fromhex('43395452010404060200010302040301020007020003010a010002030b030002010d02010300ada9')

def crc16_ccitt(data, init=0xffff):
    crc=init
    for b in data:
        crc ^= b<<8
        for _ in range(8):
            if crc & 0x8000: crc=((crc<<1)^0x1021)&0xffff
            else: crc=(crc<<1)&0xffff
    return crc

for name,d in [('lane0',l0),('lane1',l1)]:
    body=d[:-2]; tail=d[-2:]
    print(name,'tail',tail.hex(),
          'crc_over_all_body',hex(crc16_ccitt(body)),
          'crc_over_after_magic',hex(crc16_ccitt(body[4:])),
          'crc_no_init',hex(crc16_ccitt(body,0)))
    # structure guess: magic(4) laneid(1) count(1) then records
    print('  bytes:', ' '.join(f'{b:02x}' for b in d))
    print('  laneid',d[4],'count',d[5])
    p=6
    recs=[]
    while p < len(d)-2:
        n=d[p]
        rec=d[p+1:p+1+n]
        recs.append((n,list(rec)))
        p+=1+n
    for n,r in recs:
        print('   rec len',n,'->',r)
