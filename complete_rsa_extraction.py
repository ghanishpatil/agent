#!/usr/bin/env python3
"""
Complete extraction of all RSA parameters from the three stones
Based on what we found:
- soul_stone: e=7 (found in file)
- time_stone: e=9 (found in file)  
- mind_stone: number 2157869541235478521545895 and secret 83927465839274658392746583

The hint says "When the exponent is small, the message doesn't stay hidden for long"
and "Three fragments. Same pattern. Repetition was intentional."

This suggests Håstad's broadcast attack with e=3
"""

import re
import struct
import zipfile

def deep_search_for_rsa(filename):
    """Deep search for n, c, e in file"""
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"\n{'='*70}")
    print(f"Deep search in: {filename}")
    print('='*70)
    
    # Search in raw bytes
    text = data.decode('latin-1', errors='replace')
    
    # Find all numbers
    all_nums = re.findall(r'\d{20,}', text)
    print(f"Found {len(all_nums)} long numbers (20+ digits)")
    
    # Find e, n, c patterns
    e_matches = re.findall(r'[^a-z]e\s*=\s*(\d+)', text, re.IGNORECASE)
    n_matches = re.findall(r'[^a-z]n\s*=\s*(\d{50,})', text, re.IGNORECASE)
    c_matches = re.findall(r'[^a-z]c\s*=\s*(\d{50,})', text, re.IGNORECASE)
    
    result = {
        'e': e_matches,
        'n': n_matches,
        'c': c_matches,
        'long_numbers': all_nums[:10]  # First 10
    }
    
    print(f"e values: {e_matches}")
    print(f"n values: {len(n_matches)}")
    print(f"c values: {len(c_matches)}")
    
    if all_nums:
        print(f"\nFirst 10 long numbers:")
        for i, num in enumerate(all_nums[:10]):
            print(f"  {i+1}. {num[:80]}{'...' if len(num) > 80 else ''}")
    
    # Check for appended data
    riff_size = struct.unpack('<I', data[4:8])[0]
    if len(data) > riff_size + 8:
        extra = data[riff_size + 8:]
        print(f"\nExtra data: {len(extra)} bytes")
        
        # Check for ZIP
        if b'PK' in extra:
            print("  Contains ZIP file!")
            # Extract number before ZIP
            lines = extra.split(b'\n', 1)
            if lines:
                num = lines[0].decode('ascii', errors='ignore').strip()
                if num.isdigit():
                    result['appended_number'] = num
                    print(f"  Number before ZIP: {num}")
    
    return result

# Search all three files
results = {}
for stone in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    results[stone] = deep_search_for_rsa(f'stones_extracted/{stone}.wav')

# We know mind_stone has the secret
print("\n" + "="*70)
print("KNOWN VALUES")
print("="*70)
print("mind_stone appended number: 2157869541235478521545895")
print("mind_stone secret.txt: 83927465839274658392746583")
print("\nThis might be e=3 for all, and these are c values or n values")

# The hint mentions "small exponent" - typically e=3
# Let's assume e=3 for all three encryptions
# We need to find n1, n2, n3 and c1, c2, c3

print("\n" + "="*70)
print("HYPOTHESIS")
print("="*70)
print("Based on Håstad's broadcast attack:")
print("- Same message M encrypted with e=3 using three different moduli")
print("- We need: (n1, c1), (n2, c2), (n3, c3)")
print("\nThe numbers we found might be encoded in:")
print("1. The audio samples themselves")
print("2. Metadata or comments")
print("3. File structure")
print("\nLet me check if the long numbers in each file are n and c...")

for stone, data in results.items():
    print(f"\n{stone}:")
    if data['long_numbers']:
        print(f"  Longest number: {data['long_numbers'][0]}")
        print(f"  Length: {len(data['long_numbers'][0])} digits")
