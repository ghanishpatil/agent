#!/usr/bin/env python3
"""
Decode SVG with the secret key
"""

import requests
import time
from xml.etree import ElementTree as ET

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

print("="*60)
print("DECODING WITH SECRET KEY")
print("="*60)

# Wait to avoid rate limit
print("\n[*] Waiting 15 seconds...")
time.sleep(15)

# Fetch SVG with secret
print("\n[*] Fetching SVG with secret key...")
resp = requests.get(TARGET_URL + "svg.php", params={'secret': SECRET_KEY})

if resp.status_code != 200:
    print(f"  Error: {resp.status_code}")
    print(resp.text)
    exit(1)

print(f"  Got {len(resp.text)} bytes")

# Parse SVG
root = ET.fromstring(resp.text)
rects = root.findall('.//{http://www.w3.org/2000/svg}rect')

# Extract only 'bit' class
bits = []
for rect in rects:
    if rect.get('class') == 'bit':
        data_k = int(rect.get('data-k', 0))
        x = int(rect.get('x', 0))
        y = int(rect.get('y', 0))
        fill = rect.get('fill', '')
        opacity = float(rect.get('opacity', 0))
        bits.append({
            'k': data_k,
            'x': x,
            'y': y,
            'fill': fill,
            'opacity': opacity
        })

print(f"\n[*] Found {len(bits)} signal bits")

# Sort by position (reading order)
sorted_bits = sorted(bits, key=lambda b: (b['y'], b['x']))

# Try different decoding methods
print("\n[*] Method 1: Direct ASCII from k values")
k_values = [b['k'] for b in sorted_bits]
ascii_text = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_values)
print(f"  {ascii_text[:200]}")

if 'Kaal{' in ascii_text or 'kaal{' in ascii_text.lower():
    print(f"\n{'='*60}")
    print(f"FLAG FOUND!")
    print(f"{'='*60}")
    # Find and extract the flag
    import re
    flag = re.search(r'Kaal\{[^}]+\}', ascii_text, re.IGNORECASE)
    if flag:
        print(flag.group(0))

# Method 2: Sort by k value
print("\n[*] Method 2: Sort by k value")
sorted_by_k = sorted(bits, key=lambda b: b['k'])
k_values_sorted = [b['k'] for b in sorted_by_k]
ascii_sorted = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_values_sorted)
print(f"  {ascii_sorted[:200]}")

if 'Kaal{' in ascii_sorted or 'kaal{' in ascii_sorted.lower():
    print(f"\n{'='*60}")
    print(f"FLAG FOUND!")
    print(f"{'='*60}")
    import re
    flag = re.search(r'Kaal\{[^}]+\}', ascii_sorted, re.IGNORECASE)
    if flag:
        print(flag.group(0))

# Method 3: High opacity only
print("\n[*] Method 3: High opacity bits only")
high_opacity = [b for b in sorted_bits if b['opacity'] > 0.8]
k_high = [b['k'] for b in high_opacity]
ascii_high = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_high)
print(f"  {ascii_high[:200]}")

if 'Kaal{' in ascii_high or 'kaal{' in ascii_high.lower():
    print(f"\n{'='*60}")
    print(f"FLAG FOUND!")
    print(f"{'='*60}")
    import re
    flag = re.search(r'Kaal\{[^}]+\}', ascii_high, re.IGNORECASE)
    if flag:
        print(flag.group(0))

# Method 4: By color
print("\n[*] Method 4: By color channel")
by_color = {}
for b in bits:
    color = b['fill']
    if color not in by_color:
        by_color[color] = []
    by_color[color].append(b)

for color, color_bits in sorted(by_color.items()):
    sorted_color = sorted(color_bits, key=lambda b: (b['y'], b['x']))
    k_vals = [b['k'] for b in sorted_color]
    ascii_color = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_vals)
    print(f"\n  {color}: {ascii_color[:100]}")
    
    if 'Kaal{' in ascii_color or 'kaal{' in ascii_color.lower():
        print(f"\n{'='*60}")
        print(f"FLAG FOUND in {color}!")
        print(f"{'='*60}")
        import re
        flag = re.search(r'Kaal\{[^}]+\}', ascii_color, re.IGNORECASE)
        if flag:
            print(flag.group(0))

print("\n" + "="*60)
