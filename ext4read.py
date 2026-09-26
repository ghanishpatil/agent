import struct, sys
sys.path.insert(0, r'f:\mission-git-hackss\mission-git-hackss')
import importlib.util
spec=importlib.util.spec_from_file_location('e','f:\\mission-git-hackss\\mission-git-hackss\\ext4parse.py')
# Instead just reimplement read via exec of functions
exec(open(r'f:\mission-git-hackss\mission-git-hackss\ext4parse.py').read().split('parse_dir(2')[0])

for ino,name in [(27,'rollout.log'),(28,'triage_cache.txt'),(29,'.gdb_history'),(30,'lane_0.cal'),(31,'lane_1.cal')]:
    print('='*40, name, 'ino', ino)
    try:
        c=read_file(ino)
        print(c.decode('latin1'))
    except Exception as e:
        print('ERR',e)
