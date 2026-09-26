#!/usr/bin/env python3
"""Final solver for Hate.Breachpoint.live"""

import requests
import json

base_url = "https://hate.breachpoint.live"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/x-www-form-urlencoded'
})

encoded = "U0kcfdLN_WhDhNldOLdHJ"

print("="*60)
print("TESTING PATHS WITH ENCODED STRING")
print("="*60)

# Try as path
paths = [
    f"/{encoded}",
    f"/api/{encoded}",
    f"/flag/{encoded}",
    f"/{encoded.lower()}",
    f"/{encoded.upper()}",
    f"/challenge/{encoded}",
    f"/secret/{encoded}",
    f"/hint/{encoded}",
]

for path in paths:
    try:
        url = base_url + path
        resp = session.get(url, timeout=5)
        print(f"\n{path}")
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Content: {resp.text[:200]}")
            if 'CTF{' in resp.text or 'FLAG{' in resp.text:
                print(f"\n{'='*60}")
                print("FLAG FOUND!")
                print(f"{'='*60}")
                print(resp.text)
    except Exception as e:
        pass

print("\n" + "="*60)
print("TESTING FORM SUBMISSION")
print("="*60)

# Try submitting the encoded string
try:
    resp = session.post(base_url, data={'input': encoded}, timeout=5)
    print(f"\nSubmitting '{encoded}':")
    print(f"  Status: {resp.status_code}")
    print(f"  Content: {resp.text[:500]}")
    if 'CTF{' in resp.text or 'FLAG{' in resp.text:
        print(f"\n{'='*60}")
        print("FLAG FOUND!")
        print(f"{'='*60}")
        # Extract flag
        import re
        flags = re.findall(r'(CTF\{[^}]+\}|FLAG\{[^}]+\})', resp.text)
        for flag in flags:
            print(flag)
except Exception as e:
    print(f"Error: {e}")

# Try submitting decoded hex
hex_decoded = "53491c7dd2cd5a10e136574e2dd1c9"
try:
    resp = session.post(base_url, data={'input': hex_decoded}, timeout=5)
    print(f"\nSubmitting hex '{hex_decoded}':")
    print(f"  Status: {resp.status_code}")
    if 'CTF{' in resp.text or 'FLAG{' in resp.text:
        print(f"\n{'='*60}")
        print("FLAG FOUND!")
        print(f"{'='*60}")
        import re
        flags = re.findall(r'(CTF\{[^}]+\}|FLAG\{[^}]+\})', resp.text)
        for flag in flags:
            print(flag)
except Exception as e:
    pass

# Try API endpoint with JSON
print("\n" + "="*60)
print("TESTING API ENDPOINTS")
print("="*60)

api_paths = ['/api/submit', '/api/check', '/api/verify', '/api/flag', '/submit', '/check', '/verify']
for api_path in api_paths:
    try:
        url = base_url + api_path
        # Try POST with JSON
        resp = session.post(url, json={'input': encoded}, timeout=5)
        if resp.status_code != 404:
            print(f"\n{api_path} (JSON POST):")
            print(f"  Status: {resp.status_code}")
            print(f"  Content: {resp.text[:200]}")
            if 'CTF{' in resp.text or 'FLAG{' in resp.text:
                print(f"\n{'='*60}")
                print("FLAG FOUND!")
                print(f"{'='*60}")
                print(resp.text)
    except:
        pass

# Check if there's a Next.js API route
print("\n" + "="*60)
print("CHECKING NEXT.JS PATTERNS")
print("="*60)

# The page uses Next.js, check for API routes
nextjs_paths = [
    '/api/hate',
    '/api/simple',
    '/api/challenge',
    '/_next/data',
    '/api/submit',
]

for path in nextjs_paths:
    try:
        url = base_url + path
        resp = session.get(url, timeout=5)
        if resp.status_code != 404:
            print(f"\n{path}:")
            print(f"  Status: {resp.status_code}")
            print(f"  Content: {resp.text[:200]}")
    except:
        pass

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
