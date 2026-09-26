with open('coll_a.bin','rb') as f:
    a = f.read()

with open('coll_b.bin','rb') as f:
    b = f.read()

print(f'Files are same: {a == b}')
print(f'Length A: {len(a)}')
print(f'Length B: {len(b)}')
print(f'Different bytes: {sum(1 for x,y in zip(a,b) if x!=y)}')

import hashlib
print(f'MD5 A: {hashlib.md5(a).hexdigest()}')
print(f'MD5 B: {hashlib.md5(b).hexdigest()}')
