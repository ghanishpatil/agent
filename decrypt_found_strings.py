#!/usr/bin/env python3

# Found these suspicious strings in the binary
encrypted_strings = [
    "obuhboiQH",
    "ha{`jQmaH",
    "`i|oz{boH",
    "zga`}Ql{H",
    "zQya|`iQH",
    "`iQl|as",
    "Lbbm{BsfH",
]

print("[*] Trying to decrypt suspicious strings...")

# Try XOR with common keys
for enc_str in encrypted_strings:
    print(f"\n  Encrypted: {enc_str}")
    
    # Try single-byte XOR
    for key in range(1, 256):
        try:
            dec = ''.join([chr(ord(c) ^ key) for c in enc_str])
            # Check if it looks like readable text or contains "Kaal"
            if 'Kaal' in dec or 'flag' in dec.lower() or all(32 <= ord(c) < 127 for c in dec):
                if any(c.isalpha() for c in dec):
                    print(f"    Key 0x{key:02x} ('{chr(key) if 32 <= key < 127 else '?'}'): {dec}")
        except:
            pass

# The pattern suggests these might be ROT or Caesar cipher
print("\n[*] Trying ROT/Caesar cipher...")
for enc_str in encrypted_strings:
    for shift in range(1, 26):
        dec = ''
        for c in enc_str:
            if c.isalpha():
                if c.islower():
                    dec += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
                else:
                    dec += chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
            else:
                dec += c
        
        if 'Kaal' in dec or 'flag' in dec.lower():
            print(f"  {enc_str} -> ROT{shift}: {dec}")
