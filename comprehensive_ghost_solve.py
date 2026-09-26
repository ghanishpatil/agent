#!/usr/bin/env python3
"""
Comprehensive Ghost Draft solver
Hints point to:
1. Fragment identifiers (#) - client-side only
2. Deleted data that still exists
3. DOM clobbering or client-side inclusion
"""

import requests

BASE = "https://ghost.vishwactf.com"

# Try all possible endpoints
endpoints = [
    "/", "/index.html", "/app.js", "/main.js", "/script.js",
    "/api/docs", "/api/reports", "/api/draft", "/api/deleted",
    "/docs", "/reports", "/draft", "/deleted", "/ghost",
    "/admin", "/internal", "/secret", "/flag",
    "/.git/HEAD", "/.env", "/config.json",
    "/app", "/document", "/report",
]

print("[*] Scanning all endpoints...")
for ep in endpoints:
    try:
        r = requests.get(f"{BASE}{ep}", timeout=5)
        if r.status_code == 200:
            content = r.text
            print(f"\n[+] {ep} ({len(content)} bytes)")
            if "VishwaCTF{" in content:
                print(f"[!!!] FLAG: {content}")
                break
            if len(content) > 30 and content != "Welcome to Secure Docs":
                print(f"    Preview: {content[:200]}")
    except:
        pass

# Check for HTML with hidden elements
print("\n[*] Checking main page HTML structure...")
r = requests.get(BASE)
html = r.text
print(f"Full HTML:\n{html}")

# Check response headers
print(f"\n[*] Response headers:")
for k, v in r.headers.items():
    print(f"    {k}: {v}")
