#!/usr/bin/env python3

# Test different flag possibilities
candidates = [
    "Kaal{Are_you_getting_f4ke_fl4g}",
    "Kaal{Are_you_getting_fake_flag}",
    "Kaal{R3v3rs3_3ng1n33r1ng}",
]

print("[*] Testing flag candidates...")
for flag in candidates:
    # Encrypt with ROT1 (reverse of ROT25)
    enc = ''
    for c in flag:
        if c.isalpha():
            if c.islower():
                enc += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))
            else:
                enc += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
        else:
            enc += c
    
    print(f"\n  Flag: {flag}")
    print(f"  ROT1: {enc}")
    
    # Check if this matches what we found in the binary
    if "Lbbm{Bsf" in enc:
        print(f"  ✓ Matches 'Lbbm{{Bsf' pattern!")

# Now let's check what we actually found in the binary
print("\n[*] What we found in the binary:")
print("  Hex: 4c62626d7b42736648...607a7076...6675...67346c...663162687d")
print("  Strings: Lbbm{BsfH...`zpv...fu...g4l...f1bh}")

# The pieces suggest:
# Lbbm{Bsf -> Kaal{Are
# zpv -> you  
# hfu -> get
# g4lf -> f4ke
# gm4h -> fl4g

# So the encrypted string is: Lbbm{Bsf_zpv_hfu_g4lf_gm4h}
# Wait, that's not quite right. Let me check each piece:

print("\n[*] Decoding each piece with ROT25:")
pieces = ["Lbbm{Bsf", "zpv", "hfu", "g4lf", "gm4h}"]
for piece in pieces:
    dec = ''
    for c in piece:
        if c.isalpha():
            if c.islower():
                dec += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
            else:
                dec += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
        else:
            dec += c
    print(f"  {piece:15} -> {dec}")

# Hmm, "hfu" -> "get" but we need "getting"
# Let me check what "getting" would be in ROT1
test = "getting"
rot1 = ''.join([chr((ord(c) - ord('a') + 1) % 26 + ord('a')) for c in test])
print(f"\n[*] 'getting' in ROT1: {rot1}")

# So we should be looking for "hfuujoh" in the binary
# But we only found "fu" which is part of "hfu" (get)

# Let me check the actual hex bytes again
hex_str = "4c62626d7b42736648ba607a707622486675488945d0488955d848b8224866752267346c48ba3422663162687d"
bytes_data = bytes.fromhex(hex_str)

print("\n[*] Extracting all printable ASCII from hex:")
printable = ''.join([chr(b) for b in bytes_data if 32 <= b < 127])
print(f"  {printable}")

# Apply ROT25
dec = ''
for c in printable:
    if c.isalpha():
        if c.islower():
            dec += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
        else:
            dec += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
    else:
        dec += c
print(f"  ROT25: {dec}")
