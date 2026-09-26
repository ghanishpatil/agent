#!/usr/bin/env python3
"""
Decode the real flag using the KEY found in the MP3 file
"""

import base64
import binascii

# The key found at the end of the file
encoded_key = "V1JPTkdLRVk="

print("[*] Decoding Base64 key...")
decoded_key = base64.b64decode(encoded_key)
print(f"[+] Decoded key: {decoded_key}")
print(f"[+] Decoded key (string): {decoded_key.decode('utf-8', errors='ignore')}")

# Now let's use this key to decode something
# The fake flag was: Kaal{1_th1nk_th15_15_wr0ng}
# Let's check if there's XOR or other encoding

print("\n[*] Analyzing the MP3 file with the key...")

with open('chall_media/chall_media.mp3', 'rb') as f:
    data = f.read()

# Search for the key in the file
key_position = data.find(b'KEY____________:V1JPTkdLRVk=')
print(f"[*] Key found at position: {key_position}")

# Check what's around the key
if key_position != -1:
    context_start = max(0, key_position - 500)
    context_end = min(len(data), key_position + 500)
    context = data[context_start:context_end]
    
    print(f"\n[*] Context around key (500 bytes before and after):")
    print(context)
    
    # Look for other patterns
    import re
    
    # Search for any other Kaal{} patterns
    all_flags = re.findall(b'Kaal\\{[^}]+\\}', data)
    print(f"\n[*] All Kaal{{}} patterns found: {len(all_flags)}")
    for i, flag in enumerate(all_flags):
        print(f"    [{i}] {flag.decode('utf-8', errors='ignore')}")
    
    # Try XOR decoding with the key
    print(f"\n[*] Trying XOR with key '{decoded_key.decode()}'...")
    
    # XOR the fake flag with the key
    fake_flag = b"1_th1nk_th15_15_wr0ng"
    key_bytes = decoded_key
    
    xor_result = []
    for i, byte in enumerate(fake_flag):
        xor_byte = byte ^ key_bytes[i % len(key_bytes)]
        xor_result.append(xor_byte)
    
    xor_decoded = bytes(xor_result)
    print(f"[+] XOR result: {xor_decoded}")
    print(f"[+] XOR result (string): {xor_decoded.decode('utf-8', errors='ignore')}")
    
    # Try different approaches
    print("\n[*] Checking if WRONGKEY is a hint...")
    
    # Maybe we need to look for data encoded with this key
    # Let's search for encoded data near the key
    
    # Check bytes before the KEY marker
    before_key = data[key_position-1000:key_position]
    print(f"\n[*] 1000 bytes before KEY:")
    print(before_key[-200:])
    
    # Try to find hidden data
    # Look for patterns that might be XOR'd
    print("\n[*] Searching for XOR'd patterns...")
    
    # The key is "WRONGKEY" - maybe the real flag is XOR'd somewhere
    # Let's search the entire file for XOR'd "Kaal{" pattern
    
    target = b"Kaal{"
    key = decoded_key
    
    # XOR the target with key to get what we should search for
    xor_target = bytes([target[i % len(target)] ^ key[i % len(key)] for i in range(len(target))])
    print(f"[*] XOR'd 'Kaal{{' pattern to search: {xor_target.hex()}")
    
    # Search for this pattern
    xor_positions = []
    for i in range(len(data) - len(xor_target)):
        if data[i:i+len(xor_target)] == xor_target:
            xor_positions.append(i)
    
    if xor_positions:
        print(f"[+] Found XOR'd pattern at positions: {xor_positions}")
        for pos in xor_positions:
            # Try to decode ~50 bytes from this position
            encoded_data = data[pos:pos+50]
            decoded_data = bytes([encoded_data[i] ^ key[i % len(key)] for i in range(len(encoded_data))])
            print(f"    Position {pos}: {decoded_data}")
            
            # Check if it's a valid flag
            if b'Kaal{' in decoded_data and b'}' in decoded_data:
                flag_match = re.search(b'Kaal\\{[^}]+\\}', decoded_data)
                if flag_match:
                    print(f"\n[+] REAL FLAG FOUND: {flag_match.group().decode('utf-8', errors='ignore')}")

print("\n[*] Analysis complete!")
