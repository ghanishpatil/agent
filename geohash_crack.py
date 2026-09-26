#!/usr/bin/env python3
"""
Geohash-based cracking for Equator Navigation
"""

import requests
import pygeohash as pgh
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

TARGET_URL = "http://138.199.163.92:12973/"

def generate_geohash_keys():
    """Generate various geohash-based keys"""
    print("="*60)
    print("Generating Geohash-Based Keys")
    print("="*60)
    
    # Null Island coordinates
    lat, lon = 0.0, 0.0
    
    keys = []
    
    # Generate geohashes at different precisions
    for precision in range(1, 13):
        gh = pgh.encode(lat, lon, precision=precision)
        keys.append(gh)
        print(f"Precision {precision}: {gh}")
    
    # Also try nearby coordinates
    for dlat in [-0.1, 0, 0.1]:
        for dlon in [-0.1, 0, 0.1]:
            gh = pgh.encode(lat + dlat, lon + dlon, precision=8)
            keys.append(gh)
    
    return keys

def try_decrypt_with_geohash_keys(keys):
    """Try to decrypt backup.bin with geohash keys"""
    print("\n" + "="*60)
    print("Trying Decryption with Geohash Keys")
    print("="*60)
    
    with open('backup.bin', 'rb') as f:
        data = f.read()
    
    for key_str in keys:
        # Try different key derivations
        key_variants = [
            hashlib.sha256(key_str.encode()).digest(),
            hashlib.md5(key_str.encode()).digest() * 2,
            key_str.encode().ljust(32, b'\x00'),
            key_str.encode().ljust(32, b'0'),
        ]
        
        for key in key_variants:
            # Try different IVs
            iv_variants = [
                b'\x00' * 16,
                hashlib.md5(key_str.encode()).digest(),
                key[:16],
            ]
            
            for iv in iv_variants:
                try:
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(data)
                    
                    # Try to unpad and decode
                    try:
                        unpadded = unpad(decrypted, 16)
                        text = unpadded.decode('utf-8', errors='ignore')
                        
                        if 'kaal{' in text.lower():
                            print(f"\n[!!!] FLAG FOUND!")
                            print(f"    Geohash key: {key_str}")
                            print(f"    Decrypted: {text}")
                            return text
                        
                        # Check if it's printable
                        if all(32 <= b < 127 for b in unpadded):
                            print(f"\n[*] Printable output with key: {key_str}")
                            print(f"    {text}")
                    except:
                        pass
                    
                    # Try without unpadding
                    text = decrypted.decode('utf-8', errors='ignore')
                    if 'kaal{' in text.lower():
                        print(f"\n[!!!] FLAG FOUND (no unpad)!")
                        print(f"    Geohash key: {key_str}")
                        print(f"    Decrypted: {text}")
                        return text
                except:
                    pass
    
    print("[-] No valid decryption found")
    return None

def try_login_with_geohash(keys):
    """Try login with geohash as password"""
    print("\n" + "="*60)
    print("Trying Login with Geohash Passwords")
    print("="*60)
    
    session = requests.Session()
    
    usernames = ["admin", "geohash", "nullisland"]
    
    for username in usernames:
        for password in keys[:20]:  # Try first 20
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
                    
                    try:
                        data = resp.json()
                        if 'token' in data:
                            return data['token']
                    except:
                        pass
            except:
                pass
    
    return None

def main():
    print("Geohash-Based Cracking")
    print()
    
    # Generate geohash keys
    keys = generate_geohash_keys()
    
    # Try decryption
    result = try_decrypt_with_geohash_keys(keys)
    if result:
        return
    
    # Try login
    token = try_login_with_geohash(keys)
    if token:
        print(f"\n[+] Got token: {token}")
        
        # Test admin endpoint
        session = requests.Session()
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = session.get(TARGET_URL + 'admin', headers=headers)
        print(f"\n[+] Admin response: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    main()
