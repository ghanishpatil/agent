import requests, time, json

BASE = 'https://ashen-checkpoint-challenge--yoriichi13.replit.app'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

payload = {
    'branch': '2be49a24a0fb370fe0c02676f5183bb4097bb15d11958e794626bc66b2fdb317',
    'nonce': '872418',
    'witness': '8f188312465744d4c6c40a2a8da72d1bddd2ed7805c55d03a7acd343ca6478d8'
}

print('Waiting for cooldown to clear...')
last_cd = 999
while True:
    r = s.get(BASE + '/api/chakra/status', timeout=10)
    data = r.json()
    cd = data.get('cooldownSeconds', 0)
    ready = data.get('ready', False)
    print(f'  ready={ready} cooldown={cd}s attempts={data.get("attempts")}')
    if ready:
        print('READY! Submitting NOW...')
        r2 = s.post(BASE + '/api/chakra/submit', json=payload, timeout=20)
        print(r2.status_code, r2.text[:500])
        if r2.status_code != 429:
            break
        # someone else hit it, wait again
        new_cd = r2.json().get('cooldownSeconds', 120)
        print(f'Hit again! waiting {new_cd}s')
        time.sleep(new_cd + 2)
    else:
        time.sleep(cd + 1)
