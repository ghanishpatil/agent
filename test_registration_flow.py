#!/usr/bin/env python3
"""
Test registration flow to understand DOB format and requirements
"""

import requests
import json
import random
import string

BASE_URL = "https://learning-vault-15.emergent.host"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
})

print("="*70)
print("TESTING REGISTRATION FLOW")
print("="*70)

# Generate random test account
random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
test_email = f"test{random_suffix}@test.com"
test_password = "TestPass123!@#"
test_dob = "1995-06-15"

print(f"\n[*] Creating test account:")
print(f"    Email: {test_email}")
print(f"    Password: {test_password}")
print(f"    DOB: {test_dob}")

try:
    # Try to register
    register_data = {
        "email": test_email,
        "password": test_password,
        "dob": test_dob,
        "name": "Test User"
    }
    
    resp = session.post(f"{BASE_URL}/api/auth/register", json=register_data, timeout=10)
    print(f"\n[*] Registration Status: {resp.status_code}")
    print(f"[*] Response: {resp.text}")
    
    if resp.status_code == 200 or resp.status_code == 201:
        print("\n[+] Registration successful!")
        
        # Try to login
        print("\n[*] Testing login...")
        login_data = {"email": test_email, "password": test_password}
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        print(f"    Login Status: {login_resp.status_code}")
        print(f"    Response: {login_resp.text[:200]}")
        
        if login_resp.status_code == 200:
            print("\n[+] Login successful!")
            
            # Test password reset flow with known DOB
            print("\n[*] Testing password reset with known DOB...")
            new_pass = "NewPass123!@#"
            reset_data = {
                "email": test_email,
                "dob": test_dob,
                "new_password": new_pass
            }
            reset_resp = session.post(f"{BASE_URL}/api/auth/reset-password", json=reset_data, timeout=10)
            print(f"    Reset Status: {reset_resp.status_code}")
            print(f"    Response: {reset_resp.text}")
            
            if reset_resp.status_code == 200:
                print("\n[+] Password reset works with correct DOB!")
                print("[*] This confirms DOB verification is real, not a honeypot")
                
                # Try wrong DOB
                print("\n[*] Testing with wrong DOB...")
                wrong_reset = {
                    "email": test_email,
                    "dob": "1990-01-01",
                    "new_password": "WrongPass123"
                }
                wrong_resp = session.post(f"{BASE_URL}/api/auth/reset-password", json=wrong_reset, timeout=10)
                print(f"    Status: {wrong_resp.status_code}")
                print(f"    Response: {wrong_resp.text}")
                
    elif resp.status_code == 422:
        print("\n[*] Validation error - checking required fields...")
        print(f"    Details: {resp.text}")
        
except Exception as e:
    print(f"\n[-] Error: {e}")

print("\n[*] Checking if admin account exists...")
try:
    # Try to register with admin email (should fail if exists)
    admin_reg = {
        "email": "admin@ethara.ai",
        "password": "test123",
        "dob": "2000-01-01"
    }
    resp = session.post(f"{BASE_URL}/api/auth/register", json=admin_reg, timeout=10)
    print(f"    Status: {resp.status_code}")
    print(f"    Response: {resp.text}")
    
    if "already exists" in resp.text.lower() or "already registered" in resp.text.lower():
        print("[+] Admin account confirmed to exist")
except:
    pass
