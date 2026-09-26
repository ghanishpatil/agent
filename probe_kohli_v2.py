#!/usr/bin/env python3
"""
Probe Kohli challenge - fixed version
"""
import requests
import time
import re

BASE = "http://chall-743ceb0c.evt-207.glabs.ctf7.com"

print("=== Testing basic command ===")
try:
    r = requests.post(f"{BASE}/run", json={"cmd": "help"}, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Raw response: {r.text[:500]}")
    
    try:
        d = r.json()
        print(f"JSON: {d}")
    except:
        print("Not valid JSON")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Trying read with different parameters ===")
time.sleep(2)

# Try reading byte by byte
for i in range(50):
    time.sleep(0.3)
    
    try:
        r = requests.post(f"{BASE}/run", json={"cmd": f"read {i}"}, timeout=10)
        
        try:
            d = r.json()
            out = d.get("output", "").strip()
        except:
            out = r.text.strip()
        
        if out and out != "0x00" and not out.startswith("[ERR]"):
            print(f"[{i}] read {i} => {out}")
            
            if "Kaal{" in out or "FLAG{" in out:
                print(f"\n{'='*80}")
                print(f"FOUND FLAG: {out}")
                print('='*80)
                
                # Extract flag
                flag = re.search(r'(Kaal|FLAG)\{[^}]+\}', out)
                if flag:
                    print(f"\nFLAG: {flag.group(0)}")
                exit(0)
    except Exception as e:
        if i % 10 == 0:
            print(f"[{i}] Error: {e}")

print("\n=== Trying with offset parameter ===")
time.sleep(2)

for i in range(50):
    time.sleep(0.3)
    
    try:
        r = requests.post(f"{BASE}/run", json={"cmd": "read", "offset": i}, timeout=10)
        
        try:
            d = r.json()
            out = d.get("output", "").strip()
        except:
            out = r.text.strip()
        
        if out and out != "0x00" and not out.startswith("[ERR]"):
            print(f"[{i}] read offset={i} => {out}")
            
            if "Kaal{" in out or "FLAG{" in out:
                print(f"\n{'='*80}")
                print(f"FOUND FLAG: {out}")
                print('='*80)
                exit(0)
    except Exception as e:
        if i % 10 == 0:
            print(f"[{i}] Error: {e}")
