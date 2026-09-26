import glob, os, binascii

files = sorted(glob.glob(r'f:\mission-git-hackss\mission-git-hackss\blobs\*.residue'))
for f in files[:3]:
    d = open(f,'rb').read()
    print(f"=== {os.path.basename(f)} len={len(d)} ===")
    print("first 64:", binascii.hexlify(d[:64]).decode())
    print("last 32:", binascii.hexlify(d[-32:]).decode())
    # entropy check
    import collections
    cnt=collections.Counter(d)
    print("distinct bytes:", len(cnt), "printable ratio:", sum(1 for b in d if 32<=b<127)/len(d))
    # look for R9CF / HTF / magic
    for m in (b'R9CF',b'HTF',b'C9TR',b'TRP',b'FLAG'):
        if m in d: print("  contains", m, "at", d.find(m))
    print()

# also check all residue same or different
alld=[open(f,'rb').read() for f in files]
print("all residue identical?", len(set(alld))==1)
print("num residue:", len(alld))
