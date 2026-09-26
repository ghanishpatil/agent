#!/usr/bin/env python3
"""
Analyze login responses more carefully
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import time

BASE_URL = "http://138.199.163.92:16969"

def sha256hex(text):
    return hashlib.sha256(text.encode()).hexdigest()

def solve_pow_fast(challenge, difficulty=18):
    target = 2 ** (256 - difficulty)
    nonce = 0
    while True:
        hash_result = sha256hex(challenge + str(nonce))
        if int(hash_result, 16) < target:
            return nonce
        nonce += 1

def get_pow_challenge():
    resp = requests.get(f"{BASE_URL}/login")
    soup = BeautifulSoup(resp.text, 'html.parser')
    challenge_input = soup.find('input', {'name': 'pow_challenge'})
    if challenge_input:
        return challenge_input.get('value')
    return None

def analyze_response_differences():
    """Analyze what different status codes mean"""
    print("[*] Analyzing response differences...")
    
    challenge = get_pow_challenge()
    if not challenge:
        return
    
    nonce = solve_pow_fast(challenge)
    
    # Test cases
    tests = [
        ('admin', 'wrong', 'Wrong password for existing user'),
        ('nonexistent12345', 'anything', 'Non-existent user'),
        ('', '', 'Empty credentials'),
        ('a', 'b', 'Short credentials'),
    ]
    
    for username, password, description in tests:
        print(f"\n[*] Test: {description}")
        print(f"  Username: '{username}', Password: '{password}'")
        
        data = {
            'pow_challenge': challenge,
            'pow_nonce': str(nonce),
            'username': username,
            'password': password
        }
        
        resp = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
        print(f"  Status: {resp.status_code}")
        print(f"  Length: {len(resp.text)}")
        
        # Look for error messages
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Check for any text that might be an error message
        body_text = soup.get_text()
        if 'error' in body_text.lower() or 'invalid' in body_text.lower() or 'wrong' in body_text.lower():
            print(f"  Error message found: {body_text[:200]}")
        
        time.sleep(1)

def check_register_endpoint():
    """Check for registration functionality"""
    print("\n[*] Checking for registration...")
    
    paths = [
        '/register',
        '/signup',
        '/create-account',
        '/new-user',
        '/join',
        '/api/register',
        '/api/signup',
        '/api/user/create',
    ]
    
    for path in paths:
        resp = requests.get(f"{BASE_URL}{path}", allow_redirects=False)
        if resp.status_code not in [404, 405]:
            print(f"  [+] {path}: {resp.status_code}")
            if len(resp.text) < 1000:
                print(f"      {resp.text[:200]}")

def check_password_reset():
    """Check for password reset functionality"""
    print("\n[*] Checking for password reset...")
    
    paths = [
        '/forgot-password',
        '/reset-password',
        '/recover',
        '/api/forgot-password',
        '/api/reset-password',
    ]
    
    for path in paths:
        resp = requests.get(f"{BASE_URL}{path}", allow_redirects=False)
        if resp.status_code not in [404, 405]:
            print(f"  [+] {path}: {resp.status_code}")

def check_for_default_accounts():
    """Check for default/demo accounts"""
    print("\n[*] Checking for default accounts...")
    
    challenge = get_pow_challenge()
    if not challenge:
        return
    
    nonce = solve_pow_fast(challenge)
    
    # Common default accounts
    accounts = [
        ('demo', 'demo'),
        ('test', 'test123'),
        ('guest', 'guest'),
        ('user', 'password'),
        ('admin', ''),  # Empty password
        ('', 'admin'),  # Empty username
    ]
    
    for username, password in accounts:
        data = {
            'pow_challenge': challenge,
            'pow_nonce': str(nonce),
            'username': username,
            'password': password
        }
        
        resp = requests.post(f"{BASE_URL}/login", data=data, allow_redirects=False)
        print(f"  {username}:{password} - Status: {resp.status_code}")
        
        if resp.status_code == 302:
            print(f"    [!] Redirect to: {resp.headers.get('Location')}")
            print(f"    [!] Cookies: {dict(resp.cookies)}")
        
        time.sleep(1)

def check_source_for_hints():
    """Check source code for hints"""
    print("\n[*] Checking source code for hints...")
    
    resp = requests.get(f"{BASE_URL}/login")
    
    # Look for interesting patterns
    import re
    
    # Look for credentials in comments
    patterns = [
        r'username.*[:=].*["\']([^"\']+)["\']',
        r'password.*[:=].*["\']([^"\']+)["\']',
        r'user.*[:=].*["\']([^"\']+)["\']',
        r'pass.*[:=].*["\']([^"\']+)["\']',
        r'credential',
        r'default',
        r'TODO',
        r'FIXME',
        r'XXX',
        r'HACK',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, resp.text, re.IGNORECASE)
        if matches:
            print(f"  Pattern '{pattern}': {matches}")

if __name__ == "__main__":
    print("="*60)
    print("Analyzing Login Responses")
    print("="*60)
    
    analyze_response_differences()
    check_register_endpoint()
    check_password_reset()
    check_for_default_accounts()
    check_source_for_hints()
    
    print("\n[*] Analysis complete!")
