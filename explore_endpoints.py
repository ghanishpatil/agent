#!/usr/bin/env python3
"""
Explore endpoints and look for clues
"""

import requests

TARGET_URL = "http://138.199.163.92:12669/"

endpoints = [
    '',
    'robots.txt',
    'sitemap.xml',
    '.git',
    'flag',
    'flag.txt',
    'admin',
    'api',
    'lore',
    'citadel',
    'ravens',
    'wall',
    'secret',
    'truth',
]

print("="*60)
print("EXPLORING ENDPOINTS")
print("="*60)

for endpoint in endpoints:
    try:
        url = TARGET_URL + endpoint
        resp = requests.get(url, timeout=5)
        print(f"\n[{resp.status_code}] {endpoint}")
        if resp.status_code == 200:
            print(f"  Content-Type: {resp.headers.get('Content-Type', 'unknown')}")
            print(f"  Length: {len(resp.text)}")
            if len(resp.text) < 500:
                print(f"  Content: {resp.text[:200]}")
            # Check for interesting headers
            for header, value in resp.headers.items():
                if header.lower() not in ['content-type', 'content-length', 'date', 'server', 'connection']:
                    print(f"  {header}: {value}")
    except Exception as e:
        print(f"[ERR] {endpoint}: {e}")

print("\n" + "="*60)
