#!/usr/bin/env python3
"""
Get the real flag from Kohli challenge with updated hash
"""
import requests
import time
import re

BASE_URL = "http://chall-6be9171d.evt-207.glabs.ctf7.com"

print("="*80)
print("GETTING REAL KOHLI FLAG")
print("="*80)

session = requests.Session()

# Try different commands and repetition counts
commands = ['help', 'check', 'status', 'flag', 'test']

for cmd in commands:
    print(f"\n[Trying command: {cmd}]")
    
    for i in range(1, 201):
        try:
            r = session.post(f"{BASE_URL}/run",
                            json={"cmd": cmd},
                            timeout=10)
            data = r.json()
            output = data.get('output', '')
            
            # Check for flag
            if 'Kaal{' in output or 'FLAG{' in output:
                print(f"\n{'='*80}")
                print(f"✓✓✓ FOUND FLAG after {i} attempts with command '{cmd}'!")
                print(f"{'='*80}")
                print(f"Output: {output}")
                print('='*80)
                
                # Extract just the flag
                flag_match = re.search(r'(Kaal|FLAG)\{[^}]+\}', output)
                if flag_match:
                    print(f"\nFLAG: {flag_match.group(0)}")
                
                exit(0)
            
            # Print progress
            if i % 25 == 0:
                print(f"  Attempt {i}: {output[:60]}")
            
            time.sleep(0.08)
            
        except Exception as e:
            if i % 25 == 0:
                print(f"  Attempt {i} error: {e}")

print("\n" + "="*80)
print("No flag found. Try increasing repetitions or different commands.")
print("="*80)
