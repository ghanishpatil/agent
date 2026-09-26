import sys
exec(open(r'f:\mission-git-hackss\mission-git-hackss\ext4parse.py').read().split('parse_dir(2')[0])

# dump r9sampler (26) and lane cals raw hex
for ino,name in [(26,'r9sampler'),(30,'lane_0.cal'),(31,'lane_1.cal')]:
    c=read_file(ino)
    open(r'f:\mission-git-hackss\mission-git-hackss\out_'+name,'wb').write(c)
    print(name, 'len', len(c))

# lane cal hex
for ino,name in [(30,'lane_0.cal'),(31,'lane_1.cal')]:
    c=read_file(ino)
    print(name, c.hex())
