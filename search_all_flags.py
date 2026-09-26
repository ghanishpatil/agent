#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

print("[*] Searching for all potential flags...")

# Method 1: Search for "Kaal{" directly
idx = data.find(b'Kaal{')
if idx != -1:
    print(f"\n[+] Found 'Kaal{{' directly at {hex(idx)}!")
    context = data[idx:idx+60]
    print(f"  {context}")
    
    # Extract until }
    end = context.find(b'}')
    if end != -1:
        flag = context[:end+1].decode('latin1')
        print(f"  FLAG: {flag}")

# Method 2: XOR search for "Kaal{"
print("\n[*] Searching for XOR-encoded 'Kaal{'...")
target = b'Kaal{'
for key in range(1, 256):
    encrypted = bytes([b ^ key for b in target])
    idx = data.find(encrypted)
    if idx != -1:
        # Get more context
        enc_chunk = data[idx:idx+50]
        dec_chunk = bytes([b ^ key for b in enc_chunk])
        
        # Find the closing brace
        try:
            decoded = dec_chunk.decode('latin1')
            end = decoded.find('}')
            if end != -1 and end < 45:
                flag = decoded[:end+1]
                # Check if it looks valid
                if all(c.isprintable() for c in flag):
                    print(f"  Key 0x{key:02x} at {hex(idx)}: {flag}")
        except:
            pass

# Method 3: ROT search
print("\n[*] Searching for ROT-encoded 'Kaal{'...")
for rot in range(1, 26):
    # Encrypt "Kaal{" with this ROT
    encrypted = ''
    for c in "Kaal{":
        if c.isalpha():
            if c.islower():
                encrypted += chr((ord(c) - ord('a') + rot) % 26 + ord('a'))
            else:
                encrypted += chr((ord(c) - ord('A') + rot) % 26 + ord('A'))
        else:
            encrypted += c
    
    # Search for it
    idx = data.find(encrypted.encode('latin1'))
    if idx != -1:
        # Get context
        chunk = data[idx:idx+50]
        
        # Find closing brace
        end = chunk.find(b'}')
        if end != -1 and end < 45:
            enc_flag = chunk[:end+1].decode('latin1')
            
            # Decrypt with reverse ROT
            dec_flag = ''
            for c in enc_flag:
                if c.isalpha():
                    if c.islower():
                        dec_flag += chr((ord(c) - ord('a') - rot) % 26 + ord('a'))
                    else:
                        dec_flag += chr((ord(c) - ord('A') - rot) % 26 + ord('A'))
                else:
                    dec_flag += c
            
            # Check if it's valid
            if all(c.isprintable() for c in dec_flag):
                print(f"  ROT{rot} at {hex(idx)}: {enc_flag} -> {dec_flag}")

# Method 4: Look for the pattern we found and clean it up manually
print("\n[*] Manual cleanup of found pattern...")
# We found: Lbbm{BsfH...`zpv...fu...g4l...f1bh}
# The 'H' characters and other bytes are assembly instructions

# Let me extract just the alphanumeric parts
encrypted_parts = ["Lbbm{Bsf", "`zpv", "fu", "g4l", "f1bh}"]
encrypted_clean = "Lbbm{Bsf_`zpv_fu_g4l_f1bh}"

# Apply ROT25 (which is ROT-1 in reverse)
decrypted = ''
for c in encrypted_clean:
    if c.isalpha():
        if c.islower():
            decrypted += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
        else:
            decrypted += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
    else:
        decrypted += c

print(f"  Cleaned: {encrypted_clean}")
print(f"  Decrypted: {decrypted}")

# Try another combination
encrypted_clean2 = "Lbbm{Bsf_zpv_hfu_g4lf_gm4h}"
decrypted2 = ''
for c in encrypted_clean2:
    if c.isalpha():
        if c.islower():
            decrypted2 += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
        else:
            decrypted2 += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
    else:
        decrypted2 += c

print(f"  Alt: {encrypted_clean2} -> {decrypted2}")
