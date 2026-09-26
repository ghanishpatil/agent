import struct, re
db=open(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db','rb').read()
pagesize=struct.unpack('>H',db[16:18])[0]
print('pagesize',pagesize,'npages',len(db)//pagesize)

# The label values likely include recognizable text; residue/blob are BLOBs.
# Search for 'label'-ish text near lane profiles. First find where 'retired_lane_profiles' schema row is, and its rootpage.
# Parse sqlite_master by reading table-leaf cells of page1.
# Simpler: search entire file for record patterns of retired_lane_profiles: slot(int) label(text) blob blob
# The CREATE shows columns: slot INTEGER PK, label TEXT, blob BLOB, residue BLOB
# In a table b-tree leaf cell: varint payloadlen, varint rowid, header(varint hdrlen, serial types...), body.
# Let's brute scan for cells whose header decodes to [ (0 for PK int), TEXT, BLOB, BLOB ].

def read_varint(b, o):
    res=0
    for i in range(9):
        c=b[o+i]
        if i==8:
            res=(res<<8)|c; return res,o+9
        res=(res<<7)|(c&0x7f)
        if not (c&0x80): return res,o+i+1
    return res,o+9

def serial_len(t):
    if t==0: return 0
    if t<=4: return t
    if t==5: return 6
    if t==6 or t==7: return 8
    if t==8 or t==9: return 0
    if t>=12:
        return (t-12)//2 if t%2==0 else (t-13)//2
    return 0

found=[]
for base in range(len(db)-4):
    # try parse a record header starting somewhere; we look for hdr pattern
    # heuristic: find printable label text and back up
    pass

# Better: locate 'retired_lane' occurrences and dump surrounding pages fully
idxs=[m.start() for m in re.finditer(rb'retired_lane_profiles', db)]
print('schema mentions at', idxs)

# Find likely data: labels for lane profiles might be like 'lane', slot names. Dump any page containing BLOB-ish flag material.
# Search for the module code strings as ascii inside db (o4,dx,c7...) which might be labels
for kw in [b'lane_',b'slot',b'profile',b'residue',b'effective',b'A1',b'B1',b'C1',b'o4',b'dx']:
    c=db.count(kw)
    #print(kw,c)

# Dump full raw around each schema mention (the actual rows are elsewhere, but let's find freelist pages)
# SQLite header: freelist trunk page at offset 32 (4 bytes), count at 36
first_freelist=struct.unpack('>I',db[32:36])[0]
freecount=struct.unpack('>I',db[36:40])[0]
print('first_freelist_page',first_freelist,'freecount',freecount)

def page(n):  # 1-based
    return db[(n-1)*pagesize:(n)*pagesize]

# walk freelist trunk
freepages=[]
p=first_freelist
while p:
    pg=page(p)
    nextt=struct.unpack('>I',pg[0:4])[0]
    L=struct.unpack('>I',pg[4:8])[0]
    for i in range(L):
        lp=struct.unpack('>I',pg[8+i*4:12+i*4])[0]
        freepages.append(lp)
    p=nextt
print('freelist leaf pages:', freepages[:50], '...total',len(freepages))

# Dump printable strings from freelist pages
for fp in freepages:
    pg=page(fp)
    ss=re.findall(rb'[ -~]{3,}', pg)
    interesting=[s for s in ss if not s.startswith(b'HTF{r9_')]
    if interesting:
        print(f'--- free page {fp} ---')
        for s in interesting[:40]:
            print('  ',s)
