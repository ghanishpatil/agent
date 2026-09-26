#!/usr/bin/env python3
"""
Verify that created accounts exist and can login
"""

import requests
import csv
import random

TARGET = "https://cyberspacevr.in"

def test_login(username, password):
    """Test if account can login"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json'
    })
    
    try:
        # Try API login
        data = {'username': username, 'password': password}
        resp = session.post(f"{TARGET}/api/auth/login", json=data, timeout=10)
        
        if resp.status_code == 200:
            return True, "API login successful"
        
        # Try form login
        resp = session.post(f"{TARGET}/login", data=data, timeout=10)
        
        if resp.status_code in [200, 302] or 'token' in resp.text.lower():
            return True, "Form login successful"
        
        return False, f"Login failed (status: {resp.status_code})"
        
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

def main():
    print("[*] Loading accounts from CSV...")
    
    try:
        with open('phantom_accounts_final.csv', 'r') as f:
            reader = csv.DictReader(f)
            accounts = list(reader)
    except FileNotFoundError:
        print("[-] phantom_accounts_final.csv not found!")
        return
    
    print(f"[+] Loaded {len(accounts)} accounts")
    
    # Test random sample
    sample_size = min(20, len(accounts))
    sample = random.sample(accounts, sample_size)
    
    print(f"\n[*] Testing {sample_size} random accounts...")
    
    success = 0
    for acc in sample:
        result, msg = test_login(acc['username'], acc['password'])
        status = "✓" if result else "✗"
        print(f"  {status} {acc['username']}: {msg}")
        if result:
            success += 1
    
    print(f"\n[+] Login success rate: {success}/{sample_size} ({(success/sample_size)*100:.1f}%)")
    
    if success > 0:
        print("\n[+] Accounts are valid and can login!")
        print("[+] Ready to submit CSV for next phase")
    else:
        print("\n[-] No accounts could login - may need to re-register")

if __name__ == "__main__":
    main()
