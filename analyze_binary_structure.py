#!/usr/bin/env python3
import struct

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

print("[*] Analyzing binary structure...")
print(f"  File size: {len(data)} bytes")

# Check if it's a PE file
if data[:2] == b'MZ':
    print("  Format: PE (Windows executable)")
    
    # Get PE header offset
    pe_offset = struct.unpack('<I', data[0x3c:0x40])[0]
    print(f"  PE header at: 0x{pe_offset:x}")
    
    # Check PE signature
    if data[pe_offset:pe_offset+4] == b'PE\x00\x00':
        print("  Valid PE signature")

# Look for the main function or key validation
print("\n[*] Searching for key validation logic...")

# Find references to "Wrong key!" and "Flag:"
wrong_idx = data.find(b'Wrong key!')
flag_idx = data.find(b'Flag:')

print(f"  'Wrong key!' at: 0x{wrong_idx:x}")
print(f"  'Flag:' at: 0x{flag_idx:x}")

# Look for code that references these strings
# In x64, strings are often loaded with LEA instruction
# Look for the addresses in little-endian

# Search for comparison instructions near these strings
print("\n[*] Looking for comparison/validation code...")

# Find "Enter key:" and look at code after it
enter_idx = data.find(b'Enter key:')
if enter_idx != -1:
    print(f"  'Enter key:' at: 0x{enter_idx:x}")
    
    # Look for code patterns that might be the key check
    # Common patterns: CMP, JE, JNE, TEST
    search_start = max(0, enter_idx - 500)
    search_end = min(len(data), enter_idx + 500)
    
    chunk = data[search_start:search_end]
    
    # Look for immediate values that might be the key
    print("\n[*] Looking for potential key values in nearby code...")
    
    # Search for ASCII strings that might be the key
    for i in range(len(chunk) - 10):
        # Check if it's a printable ASCII string
        test_str = chunk[i:i+10]
        if all(32 <= b < 127 for b in test_str):
            s = test_str.decode('ascii')
            if s.isalnum() and len(s) >= 4:
                print(f"    Possible key at 0x{search_start+i:x}: {s}")

# Let's also look for the encrypted flag and see if we can find the decryption key
print("\n[*] Analyzing encrypted flag location...")
lbbm_idx = data.find(b'Lbbm{BsfH')
if lbbm_idx != -1:
    print(f"  Encrypted flag at: 0x{lbbm_idx:x}")
    
    # Look for code that might decrypt it
    # Look backwards for the decryption routine
    search_start = max(0, lbbm_idx - 1000)
    chunk = data[search_start:lbbm_idx]
    
    # Look for XOR or ROT operations
    # XOR is often: 0x31 (XOR reg, reg) or 0x35 (XOR eax, imm32)
    # ROT/shift: 0xC0, 0xC1, 0xD0, 0xD1, 0xD2, 0xD3
    
    print("  Looking for crypto operations near flag...")
    
    # Look for the value 0x0e (14) or 25 (ROT25) as immediate values
    for i in range(len(chunk) - 4):
        # Check for immediate value 0x0e
        if chunk[i] == 0x0e:
            print(f"    Found 0x0e at offset 0x{search_start+i:x}")
        # Check for immediate value 25 (0x19)
        if chunk[i] == 0x19:
            print(f"    Found 0x19 (25) at offset 0x{search_start+i:x}")
        # Check for immediate value 1 (ROT1)
        if chunk[i] == 0x01 and i > 0 and chunk[i-1] in [0xb0, 0xb1, 0xb2, 0xb3]:  # MOV reg, imm8
            print(f"    Found MOV with 0x01 at offset 0x{search_start+i:x}")

# Try to find what the correct key might be by looking at the validation
print("\n[*] Searching for key comparison values...")

# Look for string comparisons (strcmp, memcmp, etc.)
# Or look for character-by-character comparison

# Search for potential keys in the binary
potential_keys = []
for i in range(len(data) - 20):
    chunk = data[i:i+20]
    # Look for printable strings of length 4-15
    if all(32 <= b < 127 for b in chunk[:10]):
        s = chunk[:10].decode('ascii')
        # Check if it looks like a key (alphanumeric, no spaces)
        if s.replace('_', '').replace('-', '').isalnum() and 4 <= len(s.strip()) <= 15:
            potential_keys.append(s.strip())

# Remove duplicates and filter
potential_keys = list(set(potential_keys))
potential_keys = [k for k in potential_keys if len(k) >= 4 and not k.startswith('_')]

print(f"\n[*] Found {len(potential_keys)} potential key strings:")
for k in potential_keys[:30]:
    print(f"    {k}")
