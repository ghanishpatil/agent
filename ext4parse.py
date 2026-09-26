import struct, sys

IMG = r'f:\mission-git-hackss\mission-git-hackss\temporal_paradox\Temporal Paradox\gateway_snapshot.img'
d = open(IMG,'rb').read()

sb = d[1024:2048]
def u16(b,o): return struct.unpack('<H',b[o:o+2])[0]
def u32(b,o): return struct.unpack('<I',b[o:o+4])[0]

inodes_count=u32(sb,0)
blocks_count=u32(sb,4)
log_bs=u32(sb,24)
BS=1024<<log_bs
blocks_per_group=u32(sb,32)
inodes_per_group=u32(sb,40)
inode_size=u16(sb,88)
first_ino=u32(sb,84)
feat_incompat=u32(sb,96)
desc_size=u16(sb,0xfe) if (feat_incompat & 0x80) else 32
first_data_block = u32(sb,20)  # 0 if BS>1024 else 1
print('BS',BS,'inode_size',inode_size,'desc_size',desc_size,'inodes_per_group',inodes_per_group,'blocks_per_group',blocks_per_group,'first_data_block',first_data_block, file=sys.stderr)

# group descriptor table starts at block after superblock
gdt_block = first_data_block + 1
gdt_off = gdt_block*BS
num_groups = (blocks_count + blocks_per_group -1)//blocks_per_group

def group_inode_table(g):
    o = gdt_off + g*desc_size
    lo = u32(d,o+8)  # bg_inode_table_lo
    hi = u32(d,o+40) if desc_size>=40 else 0
    return (hi<<32)|lo

def read_inode(ino):
    g=(ino-1)//inodes_per_group
    idx=(ino-1)%inodes_per_group
    itblk=group_inode_table(g)
    off=itblk*BS + idx*inode_size
    return d[off:off+inode_size]

def inode_size_bytes(raw):
    lo=u32(raw,4); hi=u32(raw,108); return (hi<<32)|lo

def extent_blocks(raw):
    # parse extent tree from i_block (offset 40, 60 bytes)
    iblock = raw[40:100]
    blocks=[]
    def parse(node):
        magic=u16(node,0)
        if magic!=0xf30a: return
        entries=u16(node,2); depth=u16(node,6)
        p=12
        for i in range(entries):
            if depth==0:
                ee_block=u32(node,p)
                ee_len=u16(node,p+4)
                ee_start_hi=u16(node,p+6)
                ee_start_lo=u32(node,p+8)
                start=(ee_start_hi<<32)|ee_start_lo
                for k in range(ee_len):
                    blocks.append((ee_block+k, start+k))
            else:
                ei_leaf_lo=u32(node,p+4)
                ei_leaf_hi=u16(node,p+8)
                child=((ei_leaf_hi<<32)|ei_leaf_lo)
                parse(d[child*BS:child*BS+BS])
            p+=12
    parse(iblock)
    return blocks

def read_file(ino):
    raw=read_inode(ino)
    size=inode_size_bytes(raw)
    flags=u32(raw,32)
    data=bytearray(size)
    if flags & 0x10000000:  # inline data
        # inline in i_block area (60 bytes) + xattr - simplistic
        inl=raw[40:40+60]
        return bytes(inl[:size])
    if flags & 0x80000:  # extents
        for logical,phys in extent_blocks(raw):
            chunk=d[phys*BS:phys*BS+BS]
            data[logical*BS:logical*BS+len(chunk)]=chunk[:max(0,size-logical*BS)]
        return bytes(data[:size])
    else:
        # classic block pointers (12 direct)
        for i in range(12):
            b=u32(raw,40+i*4)
            if b:
                chunk=d[b*BS:b*BS+BS]
                data[i*BS:i*BS+len(chunk)]=chunk[:max(0,size-i*BS)]
        return bytes(data[:size])

def times(raw):
    atime=u32(raw,8); ctime=u32(raw,12); mtime=u32(raw,16); crtime=u32(raw,144) if inode_size>=160 else 0
    return atime,ctime,mtime,crtime

def parse_dir(ino, path='', depth=0, seen=None):
    if seen is None: seen=set()
    if ino in seen: return
    seen.add(ino)
    raw=read_inode(ino)
    mode=u16(raw,0)
    if (mode & 0xF000)!=0x4000:
        return
    content=read_file(ino)
    p=0
    entries=[]
    while p < len(content):
        if p+8>len(content): break
        e_ino=u32(content,p)
        rec_len=u16(content,p+4)
        name_len=content[p+6]
        ftype=content[p+7]
        if rec_len<8: break
        name=content[p+8:p+8+name_len]
        if e_ino!=0 and name not in (b'.',b'..'):
            entries.append((name.decode('latin1'),e_ino,ftype))
        p+=rec_len
    for name,e_ino,ftype in entries:
        full=path+'/'+name
        r=read_inode(e_ino)
        a,c,m,cr=times(r)
        sz=inode_size_bytes(r)
        print(f'{full}\tino={e_ino}\ttype={ftype}\tsize={sz}\tmtime={m}\tctime={c}\tcrtime={cr}\tatime={a}')
        if ftype==2:  # dir
            parse_dir(e_ino, full, depth+1, seen)

parse_dir(2, '')
