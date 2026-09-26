#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# Look for the encrypted flag data
# It's likely stored as a byte array in the .data section

print("[*] Analyzing binary structure...")

# Find all byte sequences that could be encrypted flags
# Kaal{ = 0x4b 0x61 0x61 0x6c 0x7b
# If XORed with a key, we can try to find patterns

# Look for data sections with high entropy
print("\n[*] Looking for encrypted data sections...")

for offset in range(0x3000, min(len(data)-50, 0x6000), 4):
    chunk = data[offset:offset+40]
    
    # Check if this could be encrypted text
    # Encrypted text usually has moderate entropy
    if len(set(chunk)) > 15 and b'\x00' not in chunk[:20]:
        # Try common single-byte XOR keys
        for key in [0x01, 0x0a, 0x0d, 0x20, 0x42, 0x69, 0x6b]:  # Common XOR keys
            dec = bytes([b ^ key for b in chunk[:30]])
            if b'Kaal{' in dec or b'FLAG' in dec or b'flag' in dec:
                print(f"  Potential at {hex(offset)} with key 0x{key:02x}")
                print(f"    Decrypted: {dec}")

# Also look for the key validation code
print("\n[*] Looking for key comparison...")
# The binary likely compares input against a hardcoded string
# Look for sequences like "cmp" or string comparison

# Common crackme keys based on binary size and complexity
print("\n[*] Trying calculated keys based on binary analysis...")
import subprocess

# Based on the binary, try these
calculated_keys = [
    'r3v3rs3',  # Common reverse engineering key
    'cr4ckm3',  # Crackme pattern
    'k33y',     # Leet speak
    'xor',      # XOR reference found
    'K4al',     # Variation of Kaal
    '4dm1n',    # Admin in leet
]

for key in calculated_keys:
    try:
        result = subprocess.run([exe], input=key.encode(), capture_output=True, timeout=0.5)
        output = result.stdout.decode(errors='ignore')
        if 'Kaal{' in output:
            print(f"\n[+] SUCCESS: {key}")
            print(output)
            break
        elif 'Flag:' in output:
            print(f"  {key}: {output[:50]}")
    except:
        pass
