#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# Search for patterns that might be the flag
# Pattern 1: Look for "Lbbm{" and see what follows
print("[*] Searching for 'Lbbm{' pattern...")
idx = data.find(b'Lbbm{')
if idx != -1:
    # Get more context
    context = data[idx:idx+50]
    print(f"  Found at {hex(idx)}: {context}")
    
    # Try ROT25 on the whole thing
    for length in [10, 20, 30, 40]:
        chunk = data[idx:idx+length]
        try:
            decoded = chunk.decode('latin1')
            rot25 = ''
            for c in decoded:
                if c.isalpha():
                    if c.islower():
                        rot25 += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
                    else:
                        rot25 += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
                else:
                    rot25 += c
            if 'Kaal{' in rot25:
                print(f"  Length {length}: {decoded} -> {rot25}")
        except:
            pass

# Pattern 2: Look for anything starting with 'K' or 'L' followed by lowercase letters
print("\n[*] Searching for potential ROT-encoded flags...")
for i in range(len(data) - 30):
    chunk = data[i:i+30]
    try:
        s = chunk.decode('latin1')
        # Check if it starts with L and has { in it (ROT25 of K is L)
        if s.startswith('L') and '{' in s[:10]:
            # Try ROT25
            rot25 = ''
            for c in s:
                if c.isalpha():
                    if c.islower():
                        rot25 += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
                    else:
                        rot25 += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
                else:
                    rot25 += c
            if rot25.startswith('Kaal{'):
                # Find the closing brace
                end = rot25.find('}')
                if end != -1:
                    flag = rot25[:end+1]
                    print(f"  Found at {hex(i)}: {s[:end+1]} -> {flag}")
    except:
        pass

# Pattern 3: XOR search - look for patterns that XOR to "Kaal{"
print("\n[*] Searching for XOR-encoded 'Kaal{' patterns...")
target = b'Kaal{'
for key in [0x0e, 0x0f, 0x10, 0x20, 0x21]:
    encrypted = bytes([b ^ key for b in target])
    idx = data.find(encrypted)
    if idx != -1:
        # Get the next 40 bytes
        enc_chunk = data[idx:idx+40]
        dec_chunk = bytes([b ^ key for b in enc_chunk])
        try:
            decoded = dec_chunk.decode('latin1')
            end = decoded.find('}')
            if end != -1:
                flag = decoded[:end+1]
                print(f"  Key 0x{key:02x} at {hex(idx)}: {flag}")
        except:
            pass

# Let me also check what comes after "Lbbm{BsfH"
print("\n[*] Checking what comes after 'Lbbm{BsfH'...")
idx = data.find(b'Lbbm{BsfH')
if idx != -1:
    # Get 100 bytes after it
    after = data[idx:idx+100]
    print(f"  Raw bytes: {after.hex()}")
    print(f"  As string: {after}")
    
    # Try to find where the string ends
    for i in range(len(after)):
        if after[i] == 0:
            actual_string = after[:i]
            print(f"  Null-terminated at position {i}")
            print(f"  String: {actual_string}")
            
            # Try ROT25 on it
            try:
                decoded = actual_string.decode('latin1')
                rot25 = ''
                for c in decoded:
                    if c.isalpha():
                        if c.islower():
                            rot25 += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
                        else:
                            rot25 += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
                    else:
                        rot25 += c
                print(f"  ROT25: {rot25}")
            except:
                pass
            break
