#!/usr/bin/env python3

# Common reverse engineering flag patterns
common_flags = [
    "Kaal{R3v3rs3_Eng1n33r1ng}",
    "Kaal{Reverse_Engineering}",
    "Kaal{Crackme_Solved}",
    "Kaal{You_Found_Me}",
    "Kaal{Nice_Try}",
    "Kaal{Wrong_Flag}",
    "Kaal{Fake_Flag}",
    "Kaal{Not_The_Flag}",
    "Kaal{Try_Harder}",
    "Kaal{R3v_3ng}",
    "Kaal{Cr4ckm3}",
    # Based on what we found
    "Kaal{Are_you_getting_fake_flag}",
    "Kaal{Are_you_getting_f4ke_fl4g}",
    "Kaal{Are_you_getting_f4ke_flag}",
    # Abbreviated
    "Kaal{R_u_getting_fake_flag}",
    "Kaal{R_u_getting_f4ke_fl4g}",
]

print("[*] Testing common reverse engineering flags...")
print("    (Encrypting with ROT1 to see if they match what's in the binary)\n")

target_hex = "4c62626d7b42736648ba607a707622486675488945d0488955d848b8224866752267346c48ba3422663162687d"
target_data = bytes.fromhex(target_hex)

for flag in common_flags:
    # Encrypt with ROT1
    enc = ''
    for c in flag:
        if c.isalpha():
            if c.islower():
                enc += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))
            else:
                enc += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
        else:
            enc += c
    
    # Check if the encrypted version appears in the binary
    if enc[:10] in target_data.decode('latin1', errors='ignore'):
        print(f"  MATCH: {flag}")
        print(f"    Encrypted: {enc}")
    elif enc.startswith("Lbbm{"):
        print(f"  Possible: {flag}")
        print(f"    Encrypted: {enc[:30]}...")

# Now let's just try to make sense of what we have
print("\n[*] What we actually extracted:")
print("  Encrypted: Lbbm{Bsf`zpvfug4lf1bh}")
print("  Decrypted: Kaal{Are`youetf4ke1ag}")

print("\n[*] Possible interpretations:")
print("  1. Kaal{Are_you_getting_fake_flag} (but 'getting' is abbreviated to 'et')")
print("  2. Kaal{R_u_getting_f4ke_fl4g} (internet speak)")
print("  3. The flag is exactly as extracted: Kaal{Are`youetf4ke1ag}")

# Let me check what the actual flag should be by testing the most likely one
print("\n[+] MOST LIKELY FLAG: Kaal{Are_you_getting_fake_flag}")
