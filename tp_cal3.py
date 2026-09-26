import binascii

# lane_0 body bytes
b0=[4, 4, 6, 3,1,3,2,0, 4,3,1,0,2,5,1,0,3,2,10,2,3,0,1,11,3,2,0,1,15,3,1,2,0]
b1=[4, 4, 6, 2,0,1,3,2, 4,3,1,2,0,7,2,0,3,1,10,1,0,2,3,11,3,0,2,1,13,2,1,3,0]

# Let's re-derive from actual file to be safe
for lane in (0,1):
    p = rf'f:\mission-git-hackss\mission-git-hackss\tp_files\var__lib__deltaforge__lane_{lane}.cal'
    d = open(p,'rb').read()
    body = d[5:38]
    print(f"=== lane {lane} body ({len(body)} bytes) ===")
    print(list(body))
    # hypothesis: body = header then variable-length records
    # first byte maybe = num records? 4?
    # Let's try TLV-ish: [tag,len,vals...]
    print("try parse as [tag][len][payload]:")
    i=0
    while i < len(body):
        tag=body[i]
        ln=body[i+1] if i+1<len(body) else None
        print(f"  @+{i}: tag={tag} len={ln} payload={body[i+2:i+2+ln] if ln is not None else None}")
        if ln is None: break
        i += 2+ln
    print()
