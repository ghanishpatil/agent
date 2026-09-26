import hashlib, requests, time, json

BASE = 'https://ashen-checkpoint-challenge--yoriichi13.replit.app'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

branch = '2be49a24a0fb370fe0c02676f5183bb4097bb15d11958e794626bc66b2fdb317'
nonce_str = '872418'
proof = '000000c094854d931d6a2e9a4cc661ee977577c267013776ce7542ed77b456d8'

br_bytes = bytes.fromhex(branch)
proof_bytes = bytes.fromhex(proof)

# Generate all witness candidates
witnesses = []

for tail_len in [8, 16, 32]:  # last N chars or bytes
    for rot in range(0, 64, 7):  # rotation amounts
        # hex string rotation
        br_rot = branch[rot:] + branch[:rot]
        for tail_mode in ['hex_chars', 'hex_bytes']:
            if tail_mode == 'hex_chars':
                tail = proof[-tail_len*2:] if tail_len <= 16 else proof[-tail_len:]
            else:
                tail = proof_bytes[-tail_len:].hex()
            # string hash
            w = hashlib.sha256((proof + br_rot + tail).encode()).hexdigest()
            witnesses.append((f'str_rot{rot}_tail{tail_len}{tail_mode}', w))
            # bytes hash  
            try:
                w2 = hashlib.sha256(proof_bytes + bytes.fromhex(br_rot) + bytes.fromhex(tail)).hexdigest()
                witnesses.append((f'bytes_rot{rot}_tail{tail_len}{tail_mode}', w2))
            except: pass

# Remove duplicates
seen = set()
unique = []
for name, w in witnesses:
    if w not in seen:
        seen.add(w)
        unique.append((name, w))

print(f'Total unique witnesses to try: {len(unique)}')

def wait_ready():
    while True:
        r = s.get(BASE + '/api/chakra/status', timeout=10)
        data = r.json()
        if data.get('ready'):
            return True
        cd = data.get('cooldownSeconds', 120)
        print(f'  Cooling {cd}s...')
        time.sleep(cd + 1)

for i, (name, witness) in enumerate(unique):
    print(f'\n[{i+1}/{len(unique)}] Trying {name}: {witness[:20]}...')
    wait_ready()
    payload = {'branch': branch, 'nonce': nonce_str, 'witness': witness}
    r = s.post(BASE + '/api/chakra/submit', json=payload, timeout=20)
    data = r.json()
    print(f'  -> {r.status_code}: {data}')
    if data.get('accepted') or data.get('flag'):
        print(f'\n*** FLAG FOUND! ***')
        print(data)
        break
    if r.status_code == 429:
        cd = data.get('cooldownSeconds', 120)
        print(f'  429 - wait {cd}s')
        time.sleep(cd + 1)
