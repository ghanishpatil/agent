import re
exec(open(r'f:\mission-git-hackss\mission-git-hackss\ext4parse.py').read().split('parse_dir(2')[0])
db=read_file(25)
print('db size', len(db))
open(r'f:\mission-git-hackss\mission-git-hackss\historian_cache.db','wb').write(db)
print('first 64 hex', db[:64].hex())
print('first 200 repr', db[:200])
# sqlite?
print('is sqlite:', db[:16])
