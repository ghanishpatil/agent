import os, glob

targets = []
# whole disk image (includes deleted/unallocated)
targets.append(os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img'))
# all extracted files
targets += glob.glob('tp_files/*')

for t in targets:
    with open(t,'rb') as f:
        data = f.read()
    idxs = []
    start = 0
    while True:
        i = data.find(b'R9CF', start)
        if i < 0:
            break
        idxs.append(i)
        start = i+1
    if idxs:
        print(f'{t}: R9CF at offsets {idxs[:20]}{" ..." if len(idxs)>20 else ""} (count={len(idxs)})')
    # also look for C9TR
    c = data.count(b'C9TR')
    if c:
        print(f'   {t}: C9TR count={c}')
