#!/usr/bin/env python3
"""
Brute force all possible decode methods on the encoded string
"""
import base64
import itertools

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

print("="*80)
print("BRUTE FORCE DECODE")
print("="*80)

# Get the base64 decoded bytes (most promising version)
decoded_bytes = base64.urlsafe_b64decode(encoded + '=')
print(f"\nBase64 decoded (URL-safe): {decoded_bytes.hex()}")
print(f"Length: {len(decoded_bytes)} bytes")

# Try XOR with all possible 2-byte keys
print("\n[Trying 2-byte XOR keys...]")
found_flags = []

for key1 in range(256):
    for key2 in range(256):
        key = bytes([key1, key2])
        try:
            xored = bytes([decoded_bytes[i] ^ key[i % 2] for i in range(len(decoded_bytes))])
            # Check if it looks like text
            decoded_str = xored.decode('utf-8', errors='ignore')
            if 'Kaal{' in decoded_str:
                print(f"\n✓ FOUND FLAG with key {key.hex()}:")
                print(f"   {decoded_str}")
                found_flags.append(decoded_str)
        except:
            pass
    
    if key1 % 50 == 0:
        print(f"   Progress: {key1}/256...", end='\r')

if not found_flags:
    print("\n\nNo flags found with 2-byte XOR. Trying 1-byte XOR...")
    
    # Try single byte XOR
    for key in range(256):
        try:
            xored = bytes([b ^ key for b in decoded_bytes])
            decoded_str = xored.decode('utf-8', errors='ignore')
            if 'Kaal{' in decoded_str:
                print(f"\n✓ FOUND FLAG with key 0x{key:02x}:")
                print(f"   {decoded_str}")
                found_flags.append(decoded_str)
        except:
            pass

if not found_flags:
    print("\n\nTrying different base64 interpretations...")
    
    # Try all possible character substitutions for _
    for replacement in ['+', '/', '-', '=']:
        modified = encoded.replace('_', replacement)
        for padding in ['', '=', '==', '===']:
            try:
                decoded = base64.b64decode(modified + padding)
                # Try XOR on this
                for key in range(256):
                    xored = bytes([b ^ key for b in decoded])
                    try:
                        decoded_str = xored.decode('utf-8', errors='ignore')
                        if 'Kaal{' in decoded_str:
                            print(f"\n✓ FOUND FLAG:")
                            print(f"   Replacement: _ -> {replacement}")
                            print(f"   Padding: {padding}")
                            print(f"   XOR key: 0x{key:02x}")
                            print(f"   Flag: {decoded_str}")
                            found_flags.append(decoded_str)
                    except:
                        pass
            except:
                pass

if not found_flags:
    print("\n\nTrying reverse + decode...")
    reversed_enc = encoded[::-1]
    try:
        for padding in ['', '=', '==']:
            decoded = base64.urlsafe_b64decode(reversed_enc + padding)
            for key in range(256):
                xored = bytes([b ^ key for b in decoded])
                try:
                    decoded_str = xored.decode('utf-8', errors='ignore')
                    if 'Kaal{' in decoded_str:
                        print(f"\n✓ FOUND FLAG (reversed):")
                        print(f"   XOR key: 0x{key:02x}")
                        print(f"   Flag: {decoded_str}")
                        found_flags.append(decoded_str)
                except:
                    pass
    except:
        pass

print("\n" + "="*80)
if found_flags:
    print(f"FOUND {len(found_flags)} FLAG(S)!")
    for flag in set(found_flags):
        print(f"   {flag}")
else:
    print("NO FLAGS FOUND")
    print("\nThe decode algorithm is likely more complex.")
    print("You need to either:")
    print("1. Run the patched game with SDL2 DLLs")
    print("2. Use IDA/Ghidra to reverse engineer the decode function")
print("="*80)
