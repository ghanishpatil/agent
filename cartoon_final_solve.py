#!/usr/bin/env python3
import requests
import re

print("="*80)
print("CARTOON NETWORK CTF - COMPLETE WALKTHROUGH")
print("="*80)

base_url = "https://joyful-mandazi-1c2213.netlify.app"

# Binary from page2 script
binary_data = "01010000 01001100 01000101 01000001 01010011 01000101 00100000 01001000 01000101 01001100 01010000"
decoded_binary = ''.join([chr(int(b, 2)) for b in binary_data.split()])
print(f"\n[BINARY DATA FROM PAGE 2]")
print(f"Binary: {binary_data}")
print(f"Decoded: {decoded_binary}")

# Try common page names
pages_to_try = [
    'page3.html',
    'page3',
    'final.html',
    'final',
    'flag.html',
    'flag',
    'complete.html',
    'complete',
    'victory.html',
    'victory',
    'congratulations.html',
    'congratulations',
    'success.html',
    'success',
]

print(f"\n[SEARCHING FOR FINAL PAGE]")
for page in pages_to_try:
    url = f"{base_url}/{page}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"\n✓ FOUND: {url}")
            print(f"Content preview:")
            print(response.text[:500])
            
            # Look for flag
            flags = re.findall(r'(flag\{[^}]+\}|FLAG\{[^}]+\}|CTF\{[^}]+\})', response.text, re.IGNORECASE)
            if flags:
                print("\n" + "="*80)
                print("FLAG FOUND:")
                print("="*80)
                for flag in flags:
                    print(f"  {flag}")
                break
    except:
        pass

# Check if there's a sitemap or robots.txt
print(f"\n[CHECKING SITEMAP/ROBOTS]")
for file in ['sitemap.xml', 'robots.txt', 'sitemap.txt']:
    url = f"{base_url}/{file}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"\n✓ Found {file}:")
            print(response.text[:500])
    except:
        pass

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
Level 1: Click Doraemon → Shows binary clue
Binary: 01101101 01101111 01110010 01110011 01100101
Decoded: "morse"

Level 2 (page2.html): Decode morse code
Morse: .--. .-.. . .- ... . / .... . .-.. .--.
Decoded: "PLEASE HELP"
Enter "PLEASE HELP" → Redirects to /binary-challenge

Level 3: Binary challenge page (not found yet)
- May not be implemented
- Or requires specific path/parameter

The challenge may be incomplete or require manual interaction.
""")
