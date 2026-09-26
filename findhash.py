import struct

# binary hash funcs
def xorshift(x):  # 0x1249
    x&=0xffffffff
    x=(x^((x<<13)&0xffffffff))&0xffffffff
    x=(x^(x>>17))&0xffffffff
    x=(x^((x<<5)&0xffffffff))&0xffffffff
    return x
def lcg(x):  # 0x1263
    return (x*0x19660d+0x3c6ef35f)&0xffffffff

prof={
'002':{0:'c86d6068',1:'50460000',2:'04',3:'04',4:'02',5:'08',6:'02',7:'02',8:'f7535567',9:'e2aa95907ea02d1a',10:'02',11:'cc583f4d',12:'0002',13:'1b37',14:'40c8cc59',15:'02',16:'fb4eea48',17:'02',18:'b2bd',19:'01'},
'003':{0:'55249ec5',1:'803e0000',2:'04',3:'04',4:'01',5:'07',6:'01',7:'01',8:'a68d20eb',9:'e2aa95907ea02d1a',10:'02',11:'cc583f4d',12:'0102',13:'1b37',14:'24ebc118',15:'02',16:'fb4eea48',17:'02',18:'b2bd',19:'01'},
'006':{0:'951fa507',1:'50460000',2:'04',3:'04',4:'02',5:'08',6:'02',7:'02',8:'f7535567',9:'e2aa95907ea02d1a',10:'02',11:'cc583f4d',12:'0002',13:'1c37',14:'990bdb03',15:'02',16:'fb4eea48',17:'02',18:'b2bd',19:'01'},
'008':{0:'68f089df',1:'50460000',2:'04',3:'04',4:'02',5:'08',6:'02',7:'02',8:'f7535567',9:'e2aa95907ea02d1a',10:'02',11:'58804bc5',12:'0002',13:'ec3e',14:'990bdb03',15:'02',16:'5e14b0ed',17:'02',18:'b2bd',19:'01'},
'009':{0:'cb0cf9e7',1:'803e0000',2:'04',3:'04',4:'01',5:'07',6:'01',7:'01',8:'a68d20eb',9:'e2aa95907ea02d1a',10:'02',11:'58804bc5',12:'0102',13:'ec3e',14:'fd28d642',15:'02',16:'5e14b0ed',17:'02',18:'b2bd',19:'01'},
'010':{0:'560d9fde',1:'803e0000',2:'04',3:'04',4:'01',5:'07',6:'01',7:'01',8:'a68d20eb',9:'e2aa95907ea02d1a',10:'02',11:'cc583f4d',12:'0102',13:'1c37',14:'fd28d642',15:'02',16:'fb4eea48',17:'02',18:'b2bd',19:'01'},
}

# slot0 as uint32 (both endian)
for p in prof:
    b=bytes.fromhex(prof[p][0])
    print(p,'slot0 LE',hex(struct.unpack('<I',b)[0]),'BE',hex(struct.unpack('>I',b)[0]))

# hypothesis: slot0 = hash chain over slots 1..19 data bytes. Build byte streams and test.
def slotbytes(p, order):
    out=b''
    for s in order:
        out+=bytes.fromhex(prof[p][s])
    return out

def try_match(p):
    target_le=struct.unpack('<I',bytes.fromhex(prof[p][0]))[0]
    target_be=struct.unpack('>I',bytes.fromhex(prof[p][0]))[0]
    # candidate streams: slots 1..19 in order, and just the 4-byte data slots
    streams={
      'slots1_19': slotbytes(p,range(1,20)),
      'data_words': slotbytes(p,[8,11,14,16]),
      'data_words2': slotbytes(p,[1,8,11,14,16]),
      'all_after0': slotbytes(p,list(range(1,20))),
    }
    for name,st in streams.items():
        # fnv-like with xorshift/lcg over dwords and bytes
        # try lcg over bytes
        h=0
        for by in st:
            h=lcg(h^by)
        # try xorshift accumulate
        h2=0
        for by in st:
            h2=xorshift(h2+by)&0xffffffff
        # try over dwords
        for endian in ['<','>']:
            for tgt,tn in [(target_le,'LE'),(target_be,'BE')]:
                if h==tgt: print(p,name,'LCG-byte matches',tn)
                if h2==tgt: print(p,name,'XORSHIFT-byte matches',tn)
    return

for p in prof:
    try_match(p)
print('done initial probe')
