#!/usr/bin/env python3
"""
Smart decode - try all reasonable approaches
"""

import requests
import time
from xml.etree import ElementTree as ET

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

print("="*60)
print("SMART DECODE")
print("="*60)

time.sleep(25)

print("\n[*] Fetching SVG with secret...")
resp = requests.get(TARGET_URL + "svg.php", params={'secret': SECRET_KEY})

if resp.status_code != 200:
    print(f"Error: {resp.status_code}")
    exit(1)

root = ET.fromstring(resp.text)
rects = root.findall('.//{http://www.w3.org/2000/svg}rect')

bits = []
for rect in rects:
    if rect.get('class') == 'bit':
        data_k = int(rect.get('data-k', 0))
        x = int(rect.get('x', 0))
        y = int(rect.get('y', 0))
        opacity = float(rect.get('opacity', 0))
        fill = rect.get('fill', '')
        bits.append({'k': data_k, 'x': x, 'y': y, 'opacity': opacity, 'fill': fill})

print(f"Found {len(bits)} bits")

# Sort by position
sorted_bits = sorted(bits, key=lambda b: (b['y'], b['x']))

# Try decoding with different bit sizes
print("\n[*] Trying different bit interpretations...")

for bit_size in [7, 8]:
    print(f"\n  {bit_size}-bit ASCII:")
    k_values = [b['k'] for b in sorted_bits]
    
    # Method 1: Direct modulo
    text1 = ''.join(chr(k % (2**bit_size)) if 32 <= k % (2**bit_size) <= 126 else '.' for k in k_values)
    print(f"    Direct: {text1[:100]}")
    if 'Kaal{' in text1:
        print(f"    [!] FLAG: {text1}")
    
    # Method 2: Divide
    text2 = ''.join(chr(k // 100) if 32 <= k // 100 <= 126 else '.' for k in k_values)
    print(f"    Div 100: {text2[:100]}")
    if 'Kaal{' in text2:
        print(f"    [!] FLAG: {text2}")
    
    # Method 3: Last 2 digits
    text3 = ''.join(chr(k % 100) if 32 <= k % 100 <= 126 else '.' for k in k_values)
    print(f"    Mod 100: {text3[:100]}")
    if 'Kaal{' in text3:
        print(f"    [!] FLAG: {text3}")

# Try using opacity as additional data
print("\n[*] Using opacity as encoding...")
for b in sorted_bits[:50]:
    # Opacity ranges from 0-1, maybe it encodes additional bits
    opacity_val = int(b['opacity'] * 100)
    combined = (b['k'] << 7) | opacity_val
    if 32 <= combined <= 126:
        print(chr(combined), end='')
print()

# Try extracting specific bits from k values
print("\n[*] Extracting specific bit ranges...")
for shift in [0, 1, 2, 3, 4, 5, 6, 7]:
    k_values = [b['k'] for b in sorted_bits]
    text = ''.join(chr((k >> shift) & 0x7F) if 32 <= (k >> shift) & 0x7F <= 126 else '.' for k in k_values)
    if 'Kaal{' in text or 'kaal{' in text.lower():
        print(f"  Shift {shift}: FOUND FLAG!")
        print(f"  {text}")
        break
    elif shift == 0:
        print(f"  Shift {shift}: {text[:100]}")

print("\n" + "="*60)
