import ext4, os

img = os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')
f = open(img,'rb')
vol = ext4.Volume(f)

outdir = 'tp_files'
os.makedirs(outdir, exist_ok=True)

targets = {}
def walk(inode, path=''):
    for entry, ftype in inode.opendir():
        name = entry.name
        if isinstance(name, bytes):
            name = name.decode('utf-8','replace')
        if name in ('.','..'):
            continue
        full = path + '/' + name
        child = inode.volume.inodes[entry.inode]
        is_dir = (child.i_mode & 0x4000) != 0
        if is_dir:
            walk(child, full)
        else:
            targets[full] = child

walk(vol.root)

for full, inode in targets.items():
    safe = ''.join(c if (c.isalnum() or c in '._-') else '__' for c in full.strip('/').replace('/','__'))
    data = inode.open().read()
    with open(os.path.join(outdir, safe),'wb') as o:
        o.write(data)
    print(f'extracted {full} -> {safe} ({len(data)} bytes)')
