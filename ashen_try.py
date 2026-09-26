import hashlib, requests, time

BASE = 'https://ashen-checkpoint-challenge--yoriichi13.replit.app'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

branch = '2be49a24a0fb370fe0c02676f5183bb4097bb15d11958e794626bc66b2fdb317'
nonce_str = '872418'
proof  = '000000c094854d931d6a2e9a4cc661ee977577c267013776ce7542ed77b456d8'
tail16 = proof[-16:]
tail32 = proof[-32:]

# Already tried: 8f188312... (rot7nibble tail16 str) - REJECTED
# Try rest
witnesses = [
    ('rot7nibble_tail16_bytes', '04a113539dad5ceda2eba61a0e3eac949552721ec25d30b3c9c7e674e509cf40'),
    ('rot7nibble_tail32_str',   '764924c8e85aabb26fbe1420c48c37bb39dea529d5e0e7845a1aeb0f11c8524e'),
    ('rot7nibble_tail32_bytes', '2bb2a9bf11e38a0f3b81a5fc7adf450301c0961cbcfa09d287a02b7a2f711c7a'),
    ('rot7byte_tail16_str',     '5c90107d10f67211e3966b8739791340850036453194a662089544b5a193bba7'),
    ('rot7byte_tail16_bytes',   '3aff767582e2f1d1949b043c79d0bd46da205b0c9f999cff4fe12fdc4c768051'),
    ('rot7byte_tail32_str',     'b1bf686f4f53dd4b2401d8479dfd7f24b21a4aec4749103dbc8b69cb159df77c'),
    ('rot7byte_tail32_bytes',   '19d76c613e729ed2d16a91534c9e9a590da97ec14293eeab66204ee3ea1d6148'),
    ('rot14byte_tail16_str',    'ffdadb59dc5cb398bdca0d2da3e583b9a28619314c6129d80641b01f3d3ef1d0'),
    ('rot14byte_tail16_bytes',  'c7c9675ffd85ee1dc0b0a984e38c1fd10afdedda58168f2ca8adfdc4496f4b42'),
    ('rot14byte_tail32_str',    '658765a699369737d2e04dbf8aa1b73651401e5394ba7c6e36d0a8af7911ecf9'),
    ('rot14byte_tail32_bytes',  '5391aab7fd235bc9a963f74df6e217abf0f8f3fe5815a3272e35d044b5967b5a'),
]

def wait_ready():
    while True:
        r = s.get(BASE + '/api/chakra/status', timeout=10)
        d = r.json()
        if d.get('ready'): return
        cd = d.get('cooldownSeconds', 120)
        print(f'  wait {cd}s...')
        time.sleep(cd + 2)

for name, witness in witnesses:
    print(f'\nTrying {name}: {witness[:16]}...')
    wait_ready()
    payload = {'branch': branch, 'nonce': nonce_str, 'witness': witness}
    r = s.post(BASE + '/api/chakra/submit', json=payload, timeout=20)
    data = r.json()
    print(f'  {r.status_code}: {data}')
    if data.get('accepted') or data.get('flag'):
        print(f'\n*** FLAG: {data} ***')
        break
    if r.status_code == 429:
        cd = data.get('cooldownSeconds', 120)
        time.sleep(cd + 2)
