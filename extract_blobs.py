import struct, re
db=open(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db','rb').read()
pagesize=4096

def read_varint(b,o):
    res=0
    for i in range(9):
        c=b[o+i]
        if i==8:
            return (res<<8)|c, o+9
        res=(res<<7)|(c&0x7f)
        if not (c&0x80):
            return res,o+i+1
    return res,o+9

def serial_len(t):
    if t==0 or t==8 or t==9: return 0
    if 1<=t<=4: return t
    if t==5: return 6
    if t==6 or t==7: return 8
    if t>=12:
        return (t-12)//2 if (t%2==0) else (t-13)//2
    return 0

# The row payload: header=[typ_slot, typ_label(text), typ_blob(blob), typ_residue(blob)]
# We know label text 'r9-retired-0NN'. Find each label occurrence and back up to parse the full record.
rows=[]
for m in re.finditer(rb'r9-retired-\d{3}', db):
    labelpos=m.start()
    labeltext=m.group()
    # The label is a TEXT column. Its serial type = 13 + 2*len (odd => text). len=14 -> type=13+28=41.
    L=len(labeltext)  # 14
    # Preceding this label in the payload body is the slot value; before body is the header.
    # header layout: hdrlen varint, then serial types. Let's search backwards for header start.
    # Simpler: the record cell format on a leaf: [payload_len varint][rowid varint][header...][body...]
    # body order: slot, label, blob, residue. label starts at labelpos, so slot value is just before.
    # Find header: it ends right where body starts (= slot value start). slot is INTEGER PK often stored as NULL(0) in body.
    # Let's scan a window before labelpos for a plausible header: hdrlen small, then [t_slot, 13+2*14+? ...]
    # type for label text len14 = 41 (0x29). Search for 0x29 within 12 bytes before labelpos region as a header serial type.
    window_start=max(0,labelpos-40)
    win=db[window_start:labelpos+4]
    # find 0x29 (41) which should be the label's serial type in header, with blob/residue types following
    # header appears BEFORE body; body starts at labelpos - (len of slot value)
    # Let's brute: for hdrlen in small range, try to parse header ending at some point, body slot then label at labelpos
    parsed=None
    for hdr_start in range(labelpos-1, max(0,labelpos-40), -1):
        hlen,p=read_varint(db,hdr_start)
        if hlen<3 or hlen>12: continue
        if hdr_start+hlen> labelpos: 
            # header could end at body start = labelpos - slotlen
            pass
        # parse serial types
        types=[]
        q=p
        ok=True
        while q < hdr_start+hlen:
            t,q=read_varint(db,q)
            types.append(t)
        if q!=hdr_start+hlen: continue
        if len(types)!=4: continue
        # body starts at hdr_start+hlen
        body=hdr_start+hlen
        slen0=serial_len(types[0])
        # label should start at body+slen0
        if body+slen0!=labelpos: continue
        if types[1]!=13+2*L: continue
        # blob and residue types must be BLOB (even, >=12)
        if types[2]<12 or types[2]%2!=0: continue
        if types[3]<12 or types[3]%2!=0: continue
        blob_len=serial_len(types[2]); res_len=serial_len(types[3])
        lab=db[labelpos:labelpos+L]
        blob=db[labelpos+L:labelpos+L+blob_len]
        residue=db[labelpos+L+blob_len:labelpos+L+blob_len+res_len]
        parsed=(lab.decode(),types,blob,residue)
        break
    if parsed:
        rows.append(parsed)
    else:
        rows.append((labeltext.decode(),None,None,None))

rows.sort(key=lambda r:r[0])
for lab,types,blob,residue in rows:
    if blob is None:
        print(lab,'PARSE FAILED')
        continue
    print(f'{lab}: types={types} blob_len={len(blob)} residue_len={len(residue)}')
    print('   blob:', blob.hex())
    print('   residue:', residue.hex())
