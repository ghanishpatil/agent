#!/usr/bin/env python3
"""
Final solve for Stones RSA Challenge
Extract n, c, e from each WAV file and perform Håstad's attack
"""

import re
import struct

def extract_all_numbers_from_wav(filename):
    """Extract all potential RSA parameters from WAV file"""
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {filename}")
    print('='*60)
    
    # Decode as latin-1 to preserve all bytes
    text = data.decode('latin-1', errors='ignore')
    
    # Find all long numbers (potential RSA params)
    all_numbers = re.findall(r'\d{10,}', text)
    
    # Find e= specifically
    e_match = re.search(r'[^a-zA-Z]e\s*=\s*(\d+)', text, re.IGNORECASE)
    
    # Find n= and c= with numbers
    n_matches = re.findall(r'[^a-zA-Z]n\s*=\s*(\d+)', text, re.IGNORECASE)
    c_matches = re.findall(r'[^a-zA-Z]c\s*=\s*(\d+)', text, re.IGNORECASE)
    
    result = {
        'e': None,
        'n': None,
        'c': None,
        'all_numbers': all_numbers
    }
    
    if e_match:
        result['e'] = int(e_match.group(1))
        print(f"Found e = {result['e']}")
    
    if n_matches:
        result['n'] = int(n_matches[0])
        print(f"Found n = {result['n']}")
    
    if c_matches:
        result['c'] = int(c_matches[0])
        print(f"Found c = {result['c']}")
    
    # Check INFO/ICMT chunk for numbers
    if b'ICMT' in data:
        idx = data.find(b'ICMT')
        # ICMT chunk format: ICMT + size (4 bytes) + data
        chunk_size = struct.unpack('<I', data[idx+4:idx+8])[0]
        chunk_data = data[idx+8:idx+8+chunk_size]
        comment = chunk_data.decode('ascii', errors='ignore').strip('\x00')
        print(f"Found ICMT comment: {comment}")
        if comment.isdigit():
            result['comment_number'] = int(comment)
    
    print(f"\nAll long numbers found: {len(all_numbers)}")
    for i, num in enumerate(all_numbers[:10]):
        print(f"  {i+1}. {num[:80]}{'...' if len(num) > 80 else ''}")
    
    return result

# Extract from all three files
stones = {}
for stone_name in ['soul_stone_1st', 'time_stone_2nd', 'mind_stone_3rd']:
    filename = f'stones_extracted/{stone_name}.wav'
    stones[stone_name] = extract_all_numbers_from_wav(filename)

print("\n" + "="*60)
print("SUMMARY OF EXTRACTED PARAMETERS")
print("="*60)

for stone_name, params in stones.items():
    print(f"\n{stone_name}:")
    print(f"  e = {params.get('e')}")
    print(f"  n = {params.get('n')}")
    print(f"  c = {params.get('c')}")
    if 'comment_number' in params:
        print(f"  comment = {params.get('comment_number')}")
    print(f"  Total numbers found: {len(params['all_numbers'])}")

# Now let's try to solve
print("\n" + "="*60)
print("ATTEMPTING HÅSTAD'S BROADCAST ATTACK")
print("="*60)

# Check if we have e=3 for all (classic Håstad attack)
# Or if we need to adapt for different exponents

# First, let's see if the largest numbers in each file are n and c
for stone_name, params in stones.items():
    print(f"\n{stone_name} - Largest numbers:")
    sorted_nums = sorted([int(n) for n in params['all_numbers']], reverse=True)
    for i, num in enumerate(sorted_nums[:5]):
        print(f"  {i+1}. {num}")
        print(f"      Bit length: {num.bit_length()}")
