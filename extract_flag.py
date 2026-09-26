#!/usr/bin/env python3
"""
Extract flag from the game binary
The flag might be encoded or hidden
"""
import re
import string

# Read the binary
with open('game/game.exe', 'rb') as f:
    data = f.read()

print("="*60)
print("EXTRACTING FLAG")
print("="*60)

# Method 1: Look for Kaal{...} pattern with printable characters
print("\n[Method 1] Searching for Kaal{...} patterns:")
# Extended search for flag pattern
for i in range(len(data) - 50):
    if data[i:i+5] == b'Kaal{':
        # Extract potential flag
        end = i + 5
        flag_chars = []
        while end < len(data) and end < i + 100:
            c = data[end]
            if c == ord('}'):
                flag_chars.append(chr(c))
                break
            elif chr(c) in string.printable and c != 0:
                flag_chars.append(chr(c))
                end += 1
            else:
                break
        
        if flag_chars and flag_chars[-1] == '}':
            flag = 'Kaal{' + ''.join(flag_chars)
            print(f"    Found at offset 0x{i:x}: {flag}")

# Method 2: Look for the fetch_flag function and nearby strings
print("\n[Method 2] Analyzing fetch_flag function area:")
fetch_flag_pos = data.find(b'fetch_flag')
if fetch_flag_pos != -1:
    print(f"    fetch_flag at offset: 0x{fetch_flag_pos:x}")
    
    # Look around this area for flag-like strings
    start = max(0, fetch_flag_pos - 1000)
    end = min(len(data), fetch_flag_pos + 1000)
    region = data[start:end]
    
    # Search for Kaal in this region
    if b'Kaal{' in region:
        local_pos = region.find(b'Kaal{')
        print(f"    Found Kaal{{ near fetch_flag at offset: 0x{start + local_pos:x}")
        
        # Extract the flag
        flag_start = start + local_pos
        flag_data = data[flag_start:flag_start+100]
        print(f"    Raw data: {flag_data[:50]}")

# Method 3: Look for base64 or hex encoded flags
print("\n[Method 3] Searching for encoded patterns:")
# Look for long alphanumeric strings that might be encoded flags
pattern = rb'[A-Za-z0-9_]{20,60}'
matches = re.findall(pattern, data)
if matches:
    print(f"    Found {len(matches)} potential encoded strings")
    for match in matches[:10]:  # Show first 10
        try:
            decoded = match.decode('ascii')
            if 'Kaal' in decoded or len(decoded) > 30:
                print(f"        {decoded}")
        except:
            pass

# Method 4: XOR or simple encryption
print("\n[Method 4] Looking for XOR-encoded flag:")
# The flag format is Kaal{...}
# If XORed, we can try to find the key
kaal_bytes = b'Kaal{'
for xor_key in range(1, 256):
    xored = bytes([b ^ xor_key for b in kaal_bytes])
    if xored in data:
        pos = data.find(xored)
        print(f"    Possible XOR key: 0x{xor_key:02x} at offset 0x{pos:x}")
        # Try to decode more
        encoded_region = data[pos:pos+50]
        decoded = bytes([b ^ xor_key for b in encoded_region])
        print(f"        Decoded: {decoded}")
        if b'}' in decoded:
            flag_end = decoded.find(b'}') + 1
            print(f"        Potential flag: {decoded[:flag_end]}")

print("\n" + "="*60)
print("EXTRACTION COMPLETE")
print("="*60)
