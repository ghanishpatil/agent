import hashlib, requests, json, time

BASE = 'https://ashen-checkpoint-challenge--yoriichi13.replit.app'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})

# === STEP 1: Verify each block seal ===
# Verify: SHA-256(<height>|<parent hash>|<data>)
transcript = [
    {"height":0,"hash":"241a28c1731447694fbaca89b51bde54b863546c82f1a5ffbdf2329080f8e7ef","parentHash":"0000000000000000000000000000000000000000000000000000000000000000","data":"ASHEN|genesis|the checkpoint remembers"},
    {"height":1,"hash":"348ef3a04e7b7821a4d4a86d21c35eef2592c714e50a205e1765cd06309605d8","parentHash":"241a28c1731447694fbaca89b51bde54b863546c82f1a5ffbdf2329080f8e7ef","data":"EMBER|validator=07|nonce-space=local"},
    {"height":2,"hash":"603447d249e8c11cb3b83cc69238ae77251f179ea29e21b6cef5149a93de2c0b","parentHash":"348ef3a04e7b7821a4d4a86d21c35eef2592c714e50a205e1765cd06309605d8","data":"RUNE|fold=nibblewise|rotation=height"},
    {"height":3,"hash":"ae14f890f77be7233bb524c9d2d42b0c6c5d87113f3b9345410cde35c4df9937","parentHash":"603447d249e8c11cb3b83cc69238ae77251f179ea29e21b6cef5149a93de2c0b","data":"VAULT|witness=terminal|gate=armed"},
    {"height":4,"hash":"53005bc2e96d22ddb0ebc20536951b5cb9ddeb5b741c4df70deb7926a6359f89","parentHash":"ae14f890f77be7233bb524c9d2d42b0c6c5d87113f3b9345410cde35c4df9937","data":"CHAKRA|finality=consensus|signal=alive"},
]

print('=== Verifying seals ===')
for b in transcript:
    preimage = f"{b['height']}|{b['parentHash']}|{b['data']}"
    computed = hashlib.sha256(preimage.encode()).hexdigest()
    match = '✓' if computed == b['hash'] else '✗'
    print(f"Block {b['height']}: {match} computed={computed[:16]}... stored={b['hash'][:16]}...")

# === STEP 2: Rotate each seal left by height nibbles, start with SHA-256("ashen-checkpoint") ===
print('\n=== Building canonical branch ===')
# Start: SHA-256("ashen-checkpoint") as 32 bytes
running = hashlib.sha256(b"ashen-checkpoint").digest()
print('Start:', running.hex())

for b in transcript:
    seal = b['hash']  # 64 hex chars = 32 bytes
    seal_bytes = bytes.fromhex(seal)
    height = b['height']
    
    # Rotate seal left by height nibbles (each nibble = 4 bits)
    # Height nibbles rotation: rotate 64 hex chars left by height positions
    nibble_count = height % 64  # mod 64 nibbles
    rotated_hex = seal[nibble_count:] + seal[:nibble_count]
    rotated_bytes = bytes.fromhex(rotated_hex)
    
    # XOR folded nibbles into 32 bytes (XOR running with rotated seal)
    running = bytes(a ^ b for a, b in zip(running, rotated_bytes))
    print(f"After block {b['height']}: {running.hex()}")

branch = running.hex()
print(f'\nCanonical branch: {branch}')

# === STEP 3: Find nonce with proof starting 00000 ===
commitment = "db685a99157efb1eafeb7c8540a4e43bfc7a10d5a354d40d12f337551f1559b9"
print(f'\n=== Mining proof (00000 prefix) ===')
nonce = 0
start = time.time()
while True:
    nonce_str = str(nonce)
    preimage = commitment + branch + nonce_str
    proof = hashlib.sha256(preimage.encode()).hexdigest()
    if proof.startswith('00000'):
        print(f'Found! nonce={nonce} proof={proof}')
        break
    nonce += 1
    if nonce % 100000 == 0:
        elapsed = time.time() - start
        print(f'  nonce={nonce} elapsed={elapsed:.1f}s')

# === STEP 4: Compute witness ===
# Witness = SHA-256(proof + branch rotated by 7 + proof trailing 16 characters)
branch_hex = branch
branch_rotated7 = branch_hex[7:] + branch_hex[:7]  # rotate left by 7 nibbles
proof_tail16 = proof[-16:]
witness_preimage = proof + branch_rotated7 + proof_tail16
witness = hashlib.sha256(witness_preimage.encode()).hexdigest()
print(f'Witness: {witness}')

# === STEP 5: Submit ===
print('\n=== Submitting ===')
payload = {"branch": branch, "nonce": nonce_str, "witness": witness}
print('Payload:', payload)
r = s.post(BASE + '/api/chakra/submit', json=payload, timeout=20)
print(f'Status: {r.status_code}')
print(r.text[:500])
