#!/usr/bin/env python3
"""
Ultimate insider solve - try all approaches
"""

import hashlib
import requests
import base64

username = "hello"
password_hash = "707b10ba2d8020957997e4127c99147091087a71"
encrypted_token = "SpSkjxA0b6VamrI9Be5tJQdSKPJ0GDQ6v8oYEKxGm_6DjsPQC023ozS_5yEuObxQLckTDAOBIc_j3liJ59OawLGpSDajKwvFeJYGVcxNDethuFUJmJnoLC3Oa-8HHf2JWm-J57v0CGbR8LemUJ07pUb4yfJaasomxoB7"

print("=" * 60)
print("ULTIMATE INSIDER SOLVE")
print("=" * 60)

# The challenge mentions "location of storage devices"
# Try location-based passwords
location_passwords = [
    'location', 'storage', 'device', 'harddisk', 'disk',
    'external', 'hidden', 'coordinates', 'gps', 'map',
    'latitude', 'longitude', 'address', 'place', 'site',
    'warehouse', 'office', 'building', 'room', 'locker',
    'safe', 'vault', 'cabinet', 'drawer', 'box'
]

print("\n[*] Trying location-related passwords...")
for pwd in location_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == password_hash:
        print(f"[+] PASSWORD FOUND: {pwd}")
        break

# Try the author name
author_passwords = ['le0', 'Le0', 'LE0', 'leo', 'Leo', 'LEO', 'leonard', 'Leonard']
print("\n[*] Trying author-related passwords...")
for pwd in author_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == password_hash:
        print(f"[+] PASSWORD FOUND: {pwd}")
        break

# Try combinations
combo_passwords = [
    'helloworld', 'hello world', 'hello_world', 'hello-world',
    'worldhello', 'world hello', 'world_hello', 'world-hello',
    'insider7', 'insider ctf', 'insiderctf7', 'betrayal7',
    'kaal7', 'kaalchakra7', 'ctf7', 'challenge7'
]

print("\n[*] Trying combination passwords...")
for pwd in combo_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == password_hash:
        print(f"[+] PASSWORD FOUND: {pwd}")
        break

# Try numbers and dates
date_passwords = [
    '2026', '2025', '25032026', '250326', '03252026', '032526',
    '7', '77', '777', '7777', 'seven', 'Seven', 'SEVEN'
]

print("\n[*] Trying date/number passwords...")
for pwd in date_passwords:
    h = hashlib.sha1(pwd.encode()).hexdigest()
    if h == password_hash:
        print(f"[+] PASSWORD FOUND: {pwd}")
        break

# The encrypted token might decode to coordinates or location
print("\n[*] Analyzing token for location data...")
try:
    token_standard = encrypted_token.replace('-', '+').replace('_', '/')
    padding = 4 - (len(token_standard) % 4)
    if padding != 4:
        token_standard += '=' * padding
    
    decoded = base64.b64decode(token_standard)
    
    # Look for coordinate patterns (numbers with dots)
    hex_str = decoded.hex()
    print(f"Token hex: {hex_str}")
    
    # Try to find patterns that look like coordinates
    # Coordinates are usually like: 28.6139, 77.2090 (latitude, longitude)
    
except Exception as e:
    print(f"Error: {e}")

# Try accessing the site with the token in different ways
print("\n[*] Trying to use token with website...")
url = "https://login-page-auqw.vercel.app"

# Try as session cookie
try:
    session = requests.Session()
    session.cookies.set('session', encrypted_token)
    session.cookies.set('token', encrypted_token)
    session.cookies.set('auth', encrypted_token)
    
    response = session.get(url + '/flag')
    if response.status_code == 200 and 'kaal{' in response.text.lower():
        print(f"[+] FLAG FOUND: {response.text}")
    
    response = session.get(url + '/admin')
    if response.status_code == 200 and 'kaal{' in response.text.lower():
        print(f"[+] FLAG FOUND: {response.text}")
        
except Exception as e:
    print(f"Token usage error: {e}")

print("\n[!] If password not found, try online hash cracker:")
print(f"[!] Hash: {password_hash}")
print("[!] https://crackstation.net/")
print("[!] https://hashes.com/en/decrypt/hash")
