#!/usr/bin/env python3
"""
Inspect the Kohli server more thoroughly
"""

import requests
import re

BASE_URL = "http://chall-6eb444b0.evt-207.glabs.ctf7.com"

print("="*80)
print("INSPECTING KOHLI SERVER")
print("="*80)

# Get main page
print("\n[*] Fetching main page...")
r = requests.get(BASE_URL)
html = r.text

print(f"Status: {r.status_code}")
print(f"Content-Length: {len(html)}")

# Save HTML
with open('kohli_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved to: kohli_page.html")

# Check for flags in HTML
flags = re.findall(r'(FLAG|Kaal)\{[^}]+\}', html)
if flags:
    print(f"\n[!] FLAGS FOUND IN HTML:")
    for flag in flags:
        print(f"  {flag}")

# Get app.js
print("\n[*] Fetching app.js...")
try:
    r = requests.get(f"{BASE_URL}/app.js")
    js = r.text
    print(f"Status: {r.status_code}")
    print(f"Content-Length: {len(js)}")
    
    with open('kohli_app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Saved to: kohli_app.js")
    
    # Check for flags in JS
    flags = re.findall(r'(FLAG|Kaal)\{[^}]+\}', js)
    if flags:
        print(f"\n[!] FLAGS FOUND IN JS:")
        for flag in flags:
            print(f"  {flag}")
    
    # Look for interesting patterns
    print("\n[*] Interesting patterns in JS:")
    if 'FLAG{' in js or 'Kaal{' in js:
        print("  - Contains flag marker")
    if 'startsWith' in js:
        print("  - Uses startsWith check")
        # Find what it checks for
        starts_with = re.findall(r"startsWith\(['\"]([^'\"]+)['\"]\)", js)
        for sw in starts_with:
            print(f"    Checks for: {sw}")
    
except Exception as e:
    print(f"Error fetching app.js: {e}")

# Try other common endpoints
print("\n[*] Testing common endpoints...")
endpoints = [
    '/flag', '/flag.txt', '/admin', '/api/flag', 
    '/debug', '/status', '/health', '/info',
    '/robots.txt', '/.git/config', '/config.json'
]

for endpoint in endpoints:
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if r.status_code == 200:
            print(f"  {endpoint}: {r.status_code} ({len(r.text)} bytes)")
            if 'FLAG{' in r.text or 'Kaal{' in r.text:
                print(f"    [!] Contains flag!")
                flags = re.findall(r'(FLAG|Kaal)\{[^}]+\}', r.text)
                for flag in flags:
                    print(f"      {flag}")
        elif r.status_code != 404:
            print(f"  {endpoint}: {r.status_code}")
    except:
        pass

# Check response headers
print("\n[*] Response headers from main page:")
for key, value in r.headers.items():
    print(f"  {key}: {value}")

print("\n" + "="*80)
