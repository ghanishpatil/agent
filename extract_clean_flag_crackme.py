#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# Find the "Lbbm{BsfH" string and extract until null terminator
idx = data.find(b'Lbbm{BsfH')
if idx != -1:
    # Find the null terminator
    end_idx = data.find(b'\x00', idx)
    full_string = data[idx:end_idx]
    
    print(f"[*] Found encrypted string at {hex(idx)}")
    print(f"  Raw bytes: {full_string.hex()}")
    print(f"  Length: {len(full_string)} bytes")
    
    # Extract only printable ASCII characters
    printable = ''
    for b in full_string:
        if 32 <= b < 127:  # Printable ASCII range
            printable += chr(b)
    
    print(f"\n[*] Printable characters only: {printable}")
    
    # Apply ROT25 to get the flag
    rot25 = ''
    for c in printable:
        if c.isalpha():
            if c.islower():
                rot25 += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
            else:
                rot25 += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
        else:
            rot25 += c
    
    print(f"[*] ROT25 decoded: {rot25}")
    
    # Extract just the flag (between Kaal{ and })
    if 'Kaal{' in rot25:
        start = rot25.find('Kaal{')
        end = rot25.find('}', start)
        if end != -1:
            flag = rot25[start:end+1]
            print(f"\n[+] FLAG FOUND: {flag}")
    
    # Also try different approaches - maybe it's a different pattern
    print("\n[*] Trying alternative extraction methods...")
    
    # Method 2: Look for the pattern L...{...}
    import re
    matches = re.findall(r'L[a-zA-Z]+\{[^}]+\}', printable)
    for match in matches:
        rot25_match = ''
        for c in match:
            if c.isalpha():
                if c.islower():
                    rot25_match += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
                else:
                    rot25_match += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
            else:
                rot25_match += c
        print(f"  Pattern: {match} -> {rot25_match}")
