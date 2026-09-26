import requests, json, re, time, hashlib

BASE = 'http://54.210.184.191:8080'
s = requests.Session()

r = s.post(BASE + '/begin', timeout=15)
session = r.json()['session']
print('Session:', session)

# Get first trial
r2 = s.get(BASE + '/trial', params={'session': session}, timeout=10)
trial = r2.json()
print('Trial:', trial)
# trial = {"i": 0, "s": "<hash>"}

# The "s" is likely a SHA256 challenge - we need to find a vow
# Try POSTing vow with session and different answers
for payload in [
    {'session': session, 'vow': trial['s']},
    {'session': session, 'vow': ''},
    {'session': session, 'answer': trial['s']},
    {'session': session, 'vow': session},
    {'session': session},
    {'session': session, 'vow': hashlib.sha256(trial['s'].encode()).hexdigest()},
    {'session': session, 'vow': hashlib.sha256((session + trial['s']).encode()).hexdigest()},
    {'session': session, 'vow': hashlib.sha256((trial['s'] + session).encode()).hexdigest()},
]:
    r3 = s.post(BASE + '/vow', json=payload, timeout=10)
    print(f'POST /vow {list(payload.keys())}: {r3.status_code} {r3.text[:200]}')
    if r3.status_code == 200 and r3.json().get('ok'):
        print('SUCCESS!')
        break
