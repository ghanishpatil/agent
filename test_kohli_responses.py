#!/usr/bin/env python3
"""
Test what responses we get from the Kohli server
"""

import requests
import time

BASE_URL = "http://chall-6eb444b0.evt-207.glabs.ctf7.com"

print("="*80)
print("TESTING KOHLI SERVER RESPONSES")
print("="*80)

# First, check the main page
print("\n[*] Fetching main page...")
try:
    r = requests.get(BASE_URL, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)} bytes")
    
    # Check for any flags in the HTML
    if 'FLAG{' in r.text or 'Kaal{' in r.text:
        print("[!] FLAG FOUND IN HTML!")
        import re
        flags = re.findall(r'(FLAG|Kaal)\{[^}]+\}', r.text)
        for flag in flags:
            print(f"  {flag}")
except Exception as e:
    print(f"Error: {e}")

# Test different commands
print("\n[*] Testing various commands...")
session = requests.Session()

test_commands = [
    'help', 'flag', 'status', 'check', 'read', 'ls', 'cat', 
    'whoami', 'id', 'pwd', 'echo test', 'ping', 'info'
]

for cmd in test_commands:
    try:
        r = session.post(
            f"{BASE_URL}/run",
            json={"cmd": cmd},
            timeout=10
        )
        data = r.json()
        output = data.get('output', '').strip()
        print(f"  '{cmd}' => {output[:80]}")
        
        if 'FLAG{' in output or 'Kaal{' in output:
            print(f"\n[!] FLAG FOUND with command '{cmd}'!")
            print(f"Output: {output}")
            break
            
        time.sleep(0.2)
    except Exception as e:
        print(f"  '{cmd}' => Error: {e}")

# Test repetition with a single command
print("\n[*] Testing repetition pattern (50 attempts with 'help')...")
for i in range(1, 51):
    try:
        r = session.post(
            f"{BASE_URL}/run",
            json={"cmd": "help"},
            timeout=10
        )
        data = r.json()
        output = data.get('output', '').strip()
        
        if i % 10 == 0 or output != "0x00":
            print(f"  Attempt {i}: {output[:80]}")
        
        if 'FLAG{' in output or 'Kaal{' in output:
            print(f"\n[!] FLAG FOUND after {i} attempts!")
            print(f"Output: {output}")
            break
            
        time.sleep(0.1)
    except Exception as e:
        if i % 10 == 0:
            print(f"  Attempt {i}: Error: {e}")

print("\n" + "="*80)
