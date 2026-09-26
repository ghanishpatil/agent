import binascii, struct

def crc16_ccitt(data, init=0xFFFF):
    crc = init
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

for lane in (0,1):
    p = rf'f:\mission-git-hackss\mission-git-hackss\tp_files\var__lib__deltaforge__lane_{lane}.cal'
    d = open(p,'rb').read()
    print(f"=== lane_{lane}.cal len={len(d)} ===")
    print("full hex:", binascii.hexlify(d).decode())
    magic = d[:4]
    laneb = d[4]
    body = d[5:38]
    trailer = d[38:40]
    print("magic", magic, "lane", laneb)
    print("body hex:", binascii.hexlify(body).decode(), "len", len(body))
    print("trailer:", binascii.hexlify(trailer).decode())
    # try crc over various ranges
    for start,end in [(0,38),(5,38),(0,40),(4,38),(5,40)]:
        c = crc16_ccitt(d[start:end])
        print(f"  crc16_ccitt d[{start}:{end}] = {c:04x}  (BE={c:04x} LE={((c&0xff)<<8)|(c>>8):04x})")
    # interpret body as slot triples? bytes look like groups
    print("body bytes:", list(body))
    print()
