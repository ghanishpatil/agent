#!/usr/bin/env python3
"""
Try massive repetition to trigger the detection
"""
import requests
import time
import re

BASE = "http://chall-35f0557e.evt-207.glabs.ctf7.com"

print("="*80)
print("MASSIVE REPETITION ATTACK")
print("="*80)

session = requests.Session()

# Try 500 repetitions
cmd = 'help'
print(f"\nSending '{cmd}' 500 times...")

for i in range(1, 501):
    try:
        r = session.post(f"{BASE}/run", json={"cmd": cmd}, timeout=10)
        d = r.json()
        out = d.get("output", "").strip()
        
        if i % 50 == 0 or "FLAG{" in out or "Kaal{" in out:
            print(f"  [{i}] {out}")
        
        if "FLAG{" in out or "Kaal{" in out:
            print(f"\n{'='*80}")
            print(f"✓✓✓ FOUND FLAG after {i} attempts!")
            print(f"{'='*80}")
            print(f"Output: {out}")
            
            flag = re.search(r'(Kaal|FLAG)\{[^}]+\}', out)
            if flag:
                print(f"\nFLAG: {flag.group(0)}")
            print('='*80)
            break
        
        time.sleep(0.05)
    except Exception as e:
        if i % 50 == 0:
            print(f"  [{i}] Error: {e}")

print("\n" + "="*80)
