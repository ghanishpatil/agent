import struct
exec(open(r'f:\mission-git-hackss\mission-git-hackss\ext4parse.py').read().split('parse_dir(2')[0])

# scan all inodes; report ones with nonzero size / links, especially deleted (links=0 but blocks set) or dtime set
print('scanning inodes 1..%d'%inodes_count)
linked={11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,2}
for ino in range(1, inodes_count+1):
    try:
        raw=read_inode(ino)
    except Exception:
        continue
    mode=u16(raw,0)
    links=u16(raw,26)
    size=inode_size_bytes(raw)
    dtime=u32(raw,20)  # deletion time
    blocks_lo=u32(raw,28)
    if size>0 and (ino not in linked):
        ftype='?'
        print(f'ino={ino} mode={mode:o} links={links} size={size} dtime={dtime} blocks={blocks_lo}')
