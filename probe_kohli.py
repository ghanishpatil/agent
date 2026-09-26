#!/usr/bin/env python3
"""
Probe different approaches for the Kohli challenge
"""
import requests
import time

BASE = "http://chall-743ceb0c.evt-207.glabs.ctf7.com"

def run_cmd(cmd):
    r = requests.post(f"{BASE}/run", json={"cmd": cmd}, timeout=10)
    d = r.json()
    return d

# Try different endpoints
print("=== Checking endpoints ===")
for path in ["/robots.txt", "/flag", "/flag.txt", "/api", "/read", "/source", "/.env", "/admin"]:
    time.sleep(1)
    try:
        r = requests.get(f"{BASE}{path}", timeout=5)
        print(f"GET {path} => {r.status_code} | {r.text[:200]}")
    except Exception as e:
        print(f"GET {path} => ERROR: {e}")

print("\n=== Trying different POST bodies ===")
time.sleep(2)

# Try different JSON structures
payloads = [
    {"cmd": "read", "offset": 0},
    {"cmd": "read", "pos": 0},
    {"cmd": "read", "index": 0},
    {"cmd": "read", "addr": 0},
    {"cmd": "read", "byte": 0},
    {"offset": 0},
    {"pos": 0},
    {"read": 0},
    {"addr": 0},
    {"cmd": "read(0)"},
    {"cmd": "read(0,1)"},
    {"cmd": "read(flag.txt, 0)"},
    {"cmd": "read(flag.txt, 0, 1)"},
]

for p in payloads:
    time.sleep(1.5)
    r = requests.post(f"{BASE}/run", json=p, timeout=10)
    d = r.json()
    out = d.get("output", "").strip()
    print(f"POST {p} => {out}")

print("\n=== Trying sequential reads (ball by ball) ===")
time.sleep(2)

# Try reading byte by byte like "ball by ball"
for i in range(100):
    time.sleep(0.5)
    payloads_to_try = [
        {"cmd": f"read {i}"},
        {"cmd": "read", "offset": i},
        {"cmd": "read", "pos": i},
        {"cmd": "read", "index": i},
    ]
    
    for p in payloads_to_try:
        r = requests.post(f"{BASE}/run", json=p, timeout=10)
        d = r.json()
        out = d.get("output", "").strip()
        
        if out and out != "0x00" and not out.startswith("[ERR]"):
            print(f"[{i}] {p} => {out}")
            
            if "Kaal{" in out or "FLAG{" in out:
                print(f"\n{'='*80}")
                print(f"FOUND FLAG: {out}")
                print('='*80)
                exit(0)
