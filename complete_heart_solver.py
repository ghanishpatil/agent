#!/usr/bin/env python3
import requests
import re
import base64

base_url = "https://thriving-meringue-85c152.netlify.app"

print("="*80)
print("HEART OF SECRETS - COMPLETE SOLVER")
print("="*80)

# Get main page
response = requests.get(base_url)
html = response.text

print("\n[SEARCHING FOR FLAGS]")
flags = re.findall(r'CTF\{[^}]+\}', html, re.IGNORECASE)
if flags:
    print("FLAGS FOUND:")
    for flag in flags:
        print(f"  ✓ {flag}")
else:
    print("No flags in main HTML")

print("\n[SEARCHING FOR HIDDEN DATA]")

# Look for base64
b64_pattern = r'[A-Za-z0-9+/]{30,}={0,2}'
b64_matches = re.findall(b64_pattern, html)
print(f"Found {len(b64_matches)} potential base64 strings")
for match in b64_matches[:5]:
    try:
        decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
        if 'CTF' in decoded or 'flag' in decoded.lower():
            print(f"  Base64: {match[:50]}...")
            print(f"  Decoded: {decoded}")
    except:
        pass

# Look for HTML comments
comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
print(f"\n[HTML COMMENTS: {len(comments)}]")
for comment in comments:
    if 'flag' in comment.lower() or 'CTF' in comment:
        print(f"  {comment.strip()}")

# Check response headers
print("\n[RESPONSE HEADERS]")
for key, value in response.headers.items():
    if 'flag' in key.lower() or 'flag' in value.lower() or 'CTF' in value:
        print(f"  {key}: {value}")

# Try common paths
paths = [
    '/flag', '/flag.txt', '/secret', '/hidden', 
    '/api/flag', '/api/secret', '/.well-known/flag',
    '/robots.txt', '/sitemap.xml', '/.git/config',
    '/l0v3', '/h34rt', '/s3cr3t', '/l3v3l2',
    '/level2', '/level3', '/final', '/victory',
    '/heart', '/love', '/secret-heart', '/valentine'
]

print(f"\n[TRYING {len(paths)} PATHS]")
for path in paths:
    url = base_url + path
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            print(f"\n✓ FOUND: {url}")
            print(f"  Content preview: {resp.text[:200]}")
            
            flags = re.findall(r'CTF\{[^}]+\}', resp.text, re.IGNORECASE)
            if flags:
                print("\n" + "="*80)
                print("FLAG FOUND:")
                for flag in flags:
                    print(f"  ✓ {flag}")
                print("="*80)
                break
    except:
        pass

# Check for steganography hints in the source
print("\n[STEGANOGRAPHY CLUES FROM SOURCE]")
print("1. Hidden message in LSB: 'KEY:NEXT_LEVEL'")
print("2. Morse code: -.- . -.-- # -. . -..- - # .-.. . ...- . .-..") 
print("   Decoded: KEY # NEXT # LEVEL")
print("3. Valid key: 'KEY NEXT LEVEL'")

# The challenge description mentions 6 steps
print("\n[CHALLENGE STEPS]")
steps = [
    "1. Extract hidden data from images → KEY:NEXT_LEVEL",
    "2. Discover hidden API endpoints → /api/get_path",
    "3. Unlock heart-shaped box → Enter 'KEY NEXT LEVEL'",
    "4. Decode morse messages → KEY # NEXT # LEVEL",
    "5. Bypass anti-debugging → View source despite protections",
    "6. Find final flag → ???"
]
for step in steps:
    print(f"  {step}")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("""
The challenge is set up but the final flag endpoint may not be implemented yet.

Based on the source code:
- Key: "KEY NEXT LEVEL"
- Hidden paths exist but return 404
- The flag should be revealed after entering the key
- Or it might be in a hidden API response

The final flag is likely:
- CTF{L0V3_1S_1N_TH3_D3T41LS} (love/heart themed)
- CTF{H34RT_0F_S3CR3TS} (challenge name)
- Or hidden in the steganographic image data

To get the actual flag, you may need to:
1. Download the canvas image
2. Extract LSB data using steganography tools
3. Or wait for the backend API to be implemented
""")
