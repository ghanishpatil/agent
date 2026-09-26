#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# Find "Lbbm{BsfH" and look at the hex
idx = data.find(b'Lbbm{BsfH')
print(f"[*] Found at offset {hex(idx)}")

# Get 60 bytes
chunk = data[idx:idx+60]
print(f"[*] Hex dump:")
print(f"  {chunk.hex()}")

# Let's manually parse this
# 4c62626d7b42736648 = "Lbbm{BsfH"
# ba = non-printable (separator?)
# 607a7076 = "`zpv"
# 22 = '"'
# 486675 = "Hfu"
# 48 = "H"
# ...

# It looks like there are assembly instructions mixed in
# Let's try to extract only consecutive printable ASCII sequences

print("\n[*] Extracting printable sequences...")
sequences = []
current_seq = ''

for b in chunk:
    if 32 <= b < 127:  # Printable ASCII
        current_seq += chr(b)
    else:
        if len(current_seq) > 0:
            sequences.append(current_seq)
            current_seq = ''

if current_seq:
    sequences.append(current_seq)

print(f"  Sequences: {sequences}")

# The first sequence should be the flag
# Let's try ROT25 on each
print("\n[*] Applying ROT25 to each sequence:")
for seq in sequences:
    rot25 = ''
    for c in seq:
        if c.isalpha():
            if c.islower():
                rot25 += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
            else:
                rot25 += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
        else:
            rot25 += c
    print(f"  {seq:30} -> {rot25}")

# Actually, looking at the hex more carefully:
# The string might be: Lbbm{Bsf_H`zpv_Hfu_H...}
# Where the non-printable bytes are just padding/separators

# Let me try a different approach - look for the pattern in strings output
print("\n[*] Looking for complete flag pattern...")

# Search for anything that looks like L[a-z]+{[^}]+}
import re

# Convert chunk to string, replacing non-printable with space
chunk_str = ''
for b in chunk:
    if 32 <= b < 127:
        chunk_str += chr(b)
    else:
        chunk_str += ' '

print(f"  Chunk as string: {chunk_str}")

# Now let's manually reconstruct based on what we see
# From the hex: 4c62626d7b427366 = "Lbbm{Bsf"
# Then we have: 48 = "H"
# Then: ba (non-printable)
# Then: 607a7076 = "`zpv"
# Then: 22 = '"'

# Let me look at the actual binary with strings command simulation
print("\n[*] Trying to find the actual flag string...")

# Look for the longest alphanumeric sequence starting with "Lbbm{"
for i in range(len(data) - 50):
    if data[i:i+5] == b'Lbbm{':
        # Extract until we find }
        flag_bytes = [data[i]]
        j = i + 1
        depth = 1
        
        while j < len(data) and j < i + 100:
            b = data[j]
            c = chr(b)
            
            # Include alphanumeric, underscore, and some special chars
            if c.isalnum() or c == '_':
                flag_bytes.append(b)
            elif c == '{':
                flag_bytes.append(b)
                depth += 1
            elif c == '}':
                flag_bytes.append(b)
                depth -= 1
                if depth == 0:
                    break
            
            j += 1
        
        if depth == 0:  # Found complete flag
            encrypted = ''.join([chr(b) for b in flag_bytes])
            
            # Apply ROT25
            decrypted = ''
            for c in encrypted:
                if c.isalpha():
                    if c.islower():
                        decrypted += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
                    else:
                        decrypted += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
                else:
                    decrypted += c
            
            if decrypted.startswith('Kaal{') and decrypted.endswith('}'):
                print(f"\n[+] FOUND FLAG!")
                print(f"  Encrypted: {encrypted}")
                print(f"  Decrypted: {decrypted}")
                break
