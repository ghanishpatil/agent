#!/usr/bin/env python3
"""
Final attempt - try many more repetitions
"""
import requests
import time

BASE_URL = "http://chall-6be9171d.evt-207.glabs.ctf7.com"

print("="*80)
print("FINAL KOHLI SOLVE - MASSIVE REPETITION")
print("="*80)

session = requests.Session()

# Try a LOT of repetitions - maybe 100+ triggers the detection
cmd = 'help'
print(f"\nSending '{cmd}' 200 times...")

for i in range(1, 201):
    try:
        r = session.post(f"{BASE_URL}/run",
                        json={"cmd": cmd},
                        timeout=10)
        data = r.json()
        output = data.get('output', '')
        
        if i % 20 == 0 or 'FLAG' in output or 'Kaal' in output:
            print(f"  Attempt {i}: {output}")
        
        if 'Kaal{' in output or 'FLAG{' in output:
            print(f"\n{'='*80}")
            print(f"✓✓✓ FOUND FLAG after {i} attempts!")
            print(f"Output: {output}")
            print('='*80)
            break
        
        time.sleep(0.1)
        
    except Exception as e:
        print(f"  Attempt {i} error: {e}")

print("\n" + "="*80)
