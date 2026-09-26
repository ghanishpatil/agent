import requests, json, hashlib, itertools, time

BASE = 'http://54.210.184.191:8080'
s = requests.Session()

r = s.post(BASE + '/begin', timeout=15)
session = r.json()['session']
print('Session:', session)

r2 = s.get(BASE + '/trial', params={'session': session}, timeout=10)
trial = r2.json()
print('Trial 0:', trial)
# s = some hash, i = 0

# The description says "41 trials, each a different shape"
# "every vow" - POST /vow with the answer
# "the heart speaks its name" - GET /heart returns flag when done

# s looks like sha256. Maybe we need to find nonce where sha256(nonce)==s?
# Or maybe s IS the answer we echo back?
# Or maybe vow needs the session + something derived from s?

# Try: vow = s itself as hex
trial_s = trial['s']

# Try all reasonable key names and value combos
combos = [
    {'session': session, 'vow': trial_s},
    {'session': session, 'vow': int(trial_s, 16)},  # as int string
    {'session': session, 'proof': trial_s},
    {'session': session, 'hash': trial_s},
    {'session': session, 'answer': trial_s},
    {'session': session, 'name': trial_s},
    {'session': session, 'vow': trial['i']},
    {'session': session, 'vow': str(trial['i'])},
    # maybe vow needs sha256 of s
    {'session': session, 'vow': hashlib.sha256(bytes.fromhex(trial_s)).hexdigest()},
    # sha256 of session
    {'session': session, 'vow': hashlib.sha256(session.encode()).hexdigest()},
    # sha256 of session+s
    {'session': session, 'vow': hashlib.sha256((session+trial_s).encode()).hexdigest()},
    # sha256 of i+s
    {'session': session, 'vow': hashlib.sha256(f"{trial['i']}{trial_s}".encode()).hexdigest()},
    # maybe vow = preimage of s? s=sha256(i) ?
    # check: sha256("0") == s?
]

for i_val in range(50):
    if hashlib.sha256(str(i_val).encode()).hexdigest() == trial_s:
        print(f'PREIMAGE FOUND: sha256("{i_val}") = s')
        combos.insert(0, {'session': session, 'vow': str(i_val)})

for c in combos:
    try:
        r3 = s.post(BASE + '/vow', json=c, timeout=8)
        print(f'vow={str(list(c.values())[1])[:20]}: {r3.status_code} {r3.text[:100]}')
        if r3.status_code == 200 and '"ok":true' in r3.text:
            print('SUCCESS! Moving to next trial...')
            break
    except Exception as e:
        print(f'Error: {e}')
