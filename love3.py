import requests, json, hashlib, time

BASE = 'http://54.210.184.191:8080'
s = requests.Session()

r = s.post(BASE + '/begin', timeout=15)
session = r.json()['session']
print('Session:', session)

r2 = s.get(BASE + '/trial', params={'session': session}, timeout=10)
trial = r2.json()
print('Trial:', trial)
trial_s = trial['s']

# POW: find nonce where sha256(s+nonce) starts with 0s
# Try different prefix lengths
for prefix_len in [1, 2, 3, 4]:
    prefix = '0' * prefix_len
    for nonce in range(100000):
        h = hashlib.sha256(f"{trial_s}{nonce}".encode()).hexdigest()
        if h.startswith(prefix):
            # try submitting this nonce
            for key in ['vow', 'nonce', 'proof', 'answer']:
                payload = {'session': session, key: str(nonce)}
                r3 = s.post(BASE + '/vow', json=payload, timeout=8)
                if r3.status_code == 200 and r3.json().get('ok'):
                    print(f'SUCCESS! prefix={prefix} nonce={nonce} key={key}')
                    print(r3.text)
                    exit(0)
                print(f'nonce={nonce} key={key} prefix={prefix}: {r3.status_code} {r3.text[:80]}')
            break  # try next prefix length

# Also try: sha256(nonce+s)
print('\nTrying sha256(nonce+s):')
for nonce in range(10000):
    h = hashlib.sha256(f"{nonce}{trial_s}".encode()).hexdigest()
    if h.startswith('0'):
        payload = {'session': session, 'vow': str(nonce)}
        r3 = s.post(BASE + '/vow', json=payload, timeout=8)
        print(f'nonce={nonce}: {r3.status_code} {r3.text[:80]}')
        if r3.status_code == 200 and r3.json().get('ok'):
            print('SUCCESS!')
            exit(0)
        break
