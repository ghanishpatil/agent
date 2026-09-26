#!/usr/bin/env python3
"""
Check for blog/article pages that might contain leaked info
"""

import requests
import time

BASE_URL = "http://138.199.163.92:16969"

print("="*60)
print("Checking for Blog/Article Pages")
print("="*60)

# Possible blog/article endpoints
endpoints = [
    '/blog',
    '/blog/',
    '/article',
    '/article/',
    '/articles',
    '/articles/',
    '/news',
    '/news/',
    '/press',
    '/press/',
    '/about',
    '/about/',
    '/company',
    '/company/',
    '/team',
    '/team/',
    '/security',
    '/security/',
    '/whitepaper',
    '/whitepaper/',
    '/research',
    '/research/',
    '/unbreakable',
    '/unhackable',
    '/quantum',
    '/quantum/',
    '/technology',
    '/technology/',
    '/features',
    '/features/',
    '/docs',
    '/docs/',
    '/documentation',
    '/documentation/',
    '/api-docs',
    '/swagger',
    '/openapi',
    '/help',
    '/help/',
    '/faq',
    '/faq/',
    '/contact',
    '/contact/',
    '/support',
    '/support/',
]

found = []

for endpoint in endpoints:
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", timeout=5, allow_redirects=False)
        if resp.status_code == 200:
            print(f"\n[+] {endpoint}: {resp.status_code} ({len(resp.text)} bytes)")
            found.append((endpoint, resp.text))
            
            # Print preview
            if len(resp.text) < 2000:
                print(f"    Content: {resp.text[:500]}")
            else:
                print(f"    Content preview: {resp.text[:300]}")
            
            # Save to file
            filename = endpoint.replace('/', '_') + '.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print(f"    Saved to: {filename}")
            
        elif resp.status_code not in [404, 405]:
            print(f"  {endpoint}: {resp.status_code}")
    except Exception as e:
        pass
    
    time.sleep(0.2)

print(f"\n[*] Found {len(found)} pages")

# Search for keywords in found pages
if found:
    print("\n[*] Searching for keywords in found pages...")
    keywords = ['password', 'credential', 'username', 'flag', 'Kaal', 'secret', 'key', 'token', 'admin', 'demo']
    
    for endpoint, content in found:
        print(f"\n  Checking {endpoint}:")
        for keyword in keywords:
            if keyword.lower() in content.lower():
                # Find context around keyword
                import re
                pattern = re.compile(f'.{{0,50}}{re.escape(keyword)}.{{0,50}}', re.IGNORECASE)
                matches = pattern.findall(content)
                if matches:
                    print(f"    '{keyword}': {matches[0]}")

print("\n[*] Search complete!")
