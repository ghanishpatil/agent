#!/usr/bin/env python3
"""
Trigger repetition detection by sending same command many times
"""
import requests
import time

BASE_URL = "http://chall-6be9171d.evt-207.glabs.ctf7.com"

print("="*80)
print("TRIGGERING REPETITION DETECTION")
print("="*80)

session = requests.Session()

# Try sending the same command many times rapidly
commands_to_try = ['help', 'status', 'check', 'flag', 'test', 'ping']

for cmd in commands_to_try:
    print(f"\n[Sending '{cmd}' repeatedly with delays]")
    
    for i in range(1, 51):
        try:
            r = session.post(f"{BASE_URL}/run",
                            json={"cmd": cmd},
                            timeout=10)
            data = r.json()
            output = data.get('output', '')
            
            if i % 5 == 0:
                print(f"  Attempt {i}: {output[:80]}")
            
            if 'Kaal{' in output or 'FLAG{' in output:
                print(f"\n{'='*80}")
                print(f"✓✓✓ FOUND FLAG after {i} attempts!")
                print(f"Command: {cmd}")
                print(f"Output: {output}")
                print('='*80)
                exit(0)
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.05)
            
        except Exception as e:
            print(f"  Attempt {i} error: {e}")
            break

print("\n[Trying without delays - rapid fire]")
for cmd in ['help', 'check']:
    print(f"\nRapid fire '{cmd}'...")
    for i in range(1, 101):
        try:
            r = session.post(f"{BASE_URL}/run",
                            json={"cmd": cmd},
                            timeout=10)
            data = r.json()
            output = data.get('output', '')
            
            if i % 10 == 0:
                print(f"  Attempt {i}: {output[:80]}")
            
            if 'Kaal{' in output or 'FLAG{' in output:
                print(f"\n{'='*80}")
                print(f"✓✓✓ FOUND FLAG after {i} attempts!")
                print(f"Output: {output}")
                print('='*80)
                exit(0)
                
        except Exception as e:
            if i % 10 == 0:
                print(f"  Attempt {i} error: {e}")

print("\n" + "="*80)
