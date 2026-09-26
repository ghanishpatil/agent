import ext4, os, datetime

img = os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')
f = open(img,'rb')
vol = ext4.Volume(f)

def ts(v):
    try:
        return datetime.datetime.utcfromtimestamp(v).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(v)

def walk(inode, path=''):
    for entry, ftype in inode.opendir():
        name = entry.name
        if isinstance(name, bytes):
            name = name.decode('utf-8','replace')
        if name in ('.','..'):
            continue
        full = path + '/' + name
        try:
            child = inode.volume.inodes[entry.inode]
        except Exception:
            try:
                child = vol.inode_at(entry.inode)
            except Exception as e:
                print(full, 'ERR', e); continue
        mode = child.i_mode
        is_dir = (mode & 0x4000) != 0
        size = child.i_size
        print(f'{"D" if is_dir else "F"} {full:45s} size={size:>8} m={ts(child.i_mtime)} c={ts(child.i_ctime)} cr={ts(child.i_crtime)} ino={entry.inode}')
        if is_dir:
            try:
                walk(child, full)
            except Exception as e:
                print(full,'DIRERR',e)

walk(vol.root)
