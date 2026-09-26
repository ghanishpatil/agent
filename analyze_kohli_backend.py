#!/usr/bin/env python3
"""
Analyze the backend behavior more carefully
"""

import requests
import time
import json

BASE_URL = "http://chall-6eb444b0.evt-207.glabs.ctf7.com"

print("="*80)
print("ANALYZING KOHLI BACKEND BEHAVIOR")
print("="*80)

# Test 1: Check if there are any cookies or session tokens
print("\n[Test 1] Checking session management...")
session = requests.Session()
r = session.post(f"{BASE_URL}/run", json={"cmd": "help"})
print(f"Cookies: {session.cookies.get_dict()}")
print(f"Response headers: {dict(r.headers)}")

# Test 2: See if response varies with different user agents
print("\n[Test 2] Testing with different User-Agents...")
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.68.0",
    "python-requests/2.28.0"
]

for ua in user_agents:
    try:
        r = requests.post(
            f"{BASE_URL}/run",
            json={"cmd": "help"},
            headers={"User-Agent": ua},
            timeout=5
        )
        data = r.json()
        print(f"  UA: {ua[:30]}... => {data.get('output', '')[:50]}")
        time.sleep(0.5)
    except Exception as e:
        print(f"  UA: {ua[:30]}... => Error: {e}")

# Test 3: Check response timing
print("\n[Test 3] Measuring response times...")
session = requests.Session()
times = []

for i in range(20):
    start = time.time()
    try:
        r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=5)
        elapsed = time.time() - start
        data = r.json()
        output = data.get('output', '')
        times.append(elapsed)
        print(f"  Request {i+1}: {elapsed:.3f}s => {output[:40]}")
        time.sleep(0.2)
    except Exception as e:
        print(f"  Request {i+1}: Error - {e}")

if times:
    print(f"\n  Average response time: {sum(times)/len(times):.3f}s")
    print(f"  Min: {min(times):.3f}s, Max: {max(times):.3f}s")

# Test 4: Try sending with additional parameters
print("\n[Test 4] Testing with additional parameters...")
test_payloads = [
    {"cmd": "help"},
    {"cmd": "help", "count": 100},
    {"cmd": "help", "repeat": True},
    {"cmd": "help", "force": True},
    {"cmd": "help help help"},
    {"cmd": "help; help; help"},
]

for payload in test_payloads:
    try:
        r = requests.post(f"{BASE_URL}/run", json=payload, timeout=5)
        data = r.json()
        print(f"  {str(payload)[:40]}... => {data.get('output', '')[:50]}")
        time.sleep(0.3)
    except Exception as e:
        print(f"  {str(payload)[:40]}... => Error: {e}")

# Test 5: Check if there's a specific threshold
print("\n[Test 5] Testing for threshold detection...")
print("Sending requests and watching for pattern changes...")

session = requests.Session()
last_output = None
change_count = 0

for i in range(1, 151):
    try:
        r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=5)
        data = r.json()
        output = data.get('output', '').strip()
        
        if output != last_output:
            change_count += 1
            print(f"  [{i:3d}] Output changed to: {output[:60]}")
            last_output = output
        
        if 'FLAG{' in output or 'Kaal{' in output:
            print(f"\n[!] FLAG FOUND at request {i}!")
            print(f"Output: {output}")
            break
        
        time.sleep(0.15)
    except Exception as e:
        if i % 30 == 0:
            print(f"  [{i:3d}] Error: {e}")

print(f"\nTotal output changes: {change_count}")

print("\n" + "="*80)
