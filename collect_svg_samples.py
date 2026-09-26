#!/usr/bin/env python3
"""
Collect multiple SVG samples and look for consistent patterns
"""

import requests
import time
from xml.etree import ElementTree as ET

TARGET_URL = "http://138.199.163.92:12669/"
SECRET_KEY = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

print("="*60)
print("COLLECTING SVG SAMPLES")
print("="*60)

# Collect 3 samples with delays
samples = []
for i in range(3):
    print(f"\n[*] Fetching sample {i+1}/3...")
    time.sleep(25)  # Long delay to avoid rate limit
    
    resp = requests.get(TARGET_URL + "svg.php", params={'secret': SECRET_KEY})
    if resp.status_code != 200:
        print(f"  Error: {resp.status_code}")
        continue
    
    print(f"  Got {len(resp.text)} bytes")
    
    # Parse
    root = ET.fromstring(resp.text)
    rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
    
    bits = []
    for rect in rects:
        if rect.get('class') == 'bit':
            data_k = int(rect.get('data-k', 0))
            x = int(rect.get('x', 0))
            y = int(rect.get('y', 0))
            opacity = float(rect.get('opacity', 0))
            bits.append({'k': data_k, 'x': x, 'y': y, 'opacity': opacity})
    
    sorted_bits = sorted(bits, key=lambda b: (b['y'], b['x']))
    samples.append(sorted_bits)
    print(f"  Found {len(bits)} bits")

# Look for consistent bits across samples
if len(samples) >= 2:
    print("\n[*] Analyzing consistency across samples...")
    
    # Find bits that appear in same position with same k value
    consistent = []
    min_len = min(len(s) for s in samples)
    
    for i in range(min_len):
        k_values = [s[i]['k'] for s in samples]
        if len(set(k_values)) == 1:  # All same
            consistent.append(samples[0][i])
    
    print(f"  Found {len(consistent)} consistent bits")
    
    if consistent:
        k_vals = [b['k'] for b in consistent]
        ascii_text = ''.join(chr(k % 128) if 32 <= k % 128 <= 126 else '.' for k in k_vals)
        print(f"  ASCII: {ascii_text[:200]}")
        
        if 'Kaal{' in ascii_text or 'kaal{' in ascii_text.lower():
            print(f"\n{'='*60}")
            print(f"FLAG FOUND!")
            print(f"{'='*60}")
            import re
            flag = re.search(r'Kaal\{[^}]+\}', ascii_text, re.IGNORECASE)
            if flag:
                print(flag.group(0))

print("\n" + "="*60)
