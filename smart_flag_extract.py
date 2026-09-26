#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# The pattern suggests the flag is ROT25 encoded
# Let's search for all strings that look like "L...{...}" and try ROT25

print("[*] Searching for ROT25-encoded flag patterns...")

# Search for "Lbbm{" which is ROT25 of "Kaal{"
idx = data.find(b'Lbbm{')
if idx != -1:
    print(f"  Found 'Lbbm{{' at {hex(idx)}")
    
    # Extract characters until we hit a closing brace or non-printable
    flag_chars = []
    i = idx
    brace_count = 0
    
    while i < len(data) and i < idx + 100:
        b = data[i]
        c = chr(b)
        
        # Only include printable ASCII letters, numbers, and special chars
        if c.isalnum() or c in '{}_-!@#$%^&*()':
            flag_chars.append(c)
            if c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found the closing brace
                    break
        
        i += 1
    
    encrypted_flag = ''.join(flag_chars)
    print(f"  Extracted: {encrypted_flag}")
    
    # Apply ROT25
    decrypted = ''
    for c in encrypted_flag:
        if c.isalpha():
            if c.islower():
                decrypted += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
            else:
                decrypted += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
        else:
            decrypted += c
    
    print(f"  ROT25: {decrypted}")
    
# Let's also try a different approach - look for the actual flag structure
# by searching for common CTF flag patterns

print("\n[*] Alternative approach - searching for flag-like patterns...")

# Try all single-byte ROT values on "Lbbm{"
for rot in range(1, 26):
    test = "Lbbm{"
    decoded = ''
    for c in test:
        if c.isalpha():
            if c.islower():
                decoded += chr((ord(c) - ord('a') + rot) % 26 + ord('a'))
            else:
                decoded += chr((ord(c) - ord('A') + rot) % 26 + ord('A'))
        else:
            decoded += c
    
    if decoded == "Kaal{":
        print(f"  ROT{rot} converts 'Lbbm{{' to 'Kaal{{'")
        
        # Now apply this to the full string
        idx = data.find(b'Lbbm{')
        if idx != -1:
            # Get a reasonable chunk
            chunk = data[idx:idx+60]
            
            # Filter to only alphanumeric and common flag chars
            filtered = ''
            for b in chunk:
                c = chr(b)
                if c.isalnum() or c in '{}_-':
                    filtered += c
                    if c == '}':
                        break
            
            print(f"  Filtered string: {filtered}")
            
            # Apply ROT
            final = ''
            for c in filtered:
                if c.isalpha():
                    if c.islower():
                        final += chr((ord(c) - ord('a') + rot) % 26 + ord('a'))
                    else:
                        final += chr((ord(c) - ord('A') + rot) % 26 + ord('A'))
                else:
                    final += c
            
            print(f"  Decoded: {final}")
            print(f"\n[+] FINAL FLAG: {final}")
