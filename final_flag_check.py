#!/usr/bin/env python3

# Check what "fl4g" encrypts to with ROT1
test = "fl4g"
rot1 = ''
for c in test:
    if c.isalpha():
        if c.islower():
            rot1 += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))
        else:
            rot1 += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
    else:
        rot1 += c
print(f"'fl4g' with ROT1: {rot1}")

# Check what "f1ag" encrypts to
test2 = "f1ag"
rot1_2 = ''
for c in test2:
    if c.isalpha():
        if c.islower():
            rot1_2 += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))
        else:
            rot1_2 += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
    else:
        rot1_2 += c
print(f"'f1ag' with ROT1: {rot1_2}")

# So "f1bh" with ROT25 gives "e1ag"
# This means the flag is: Kaal{Are_you_getting_f4ke_f1ag}

# Let me verify by encrypting this
flag = "Kaal{Are_you_getting_f4ke_f1ag}"
enc = ''
for c in flag:
    if c.isalpha():
        if c.islower():
            enc += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))
        else:
            enc += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
    else:
        enc += c

print(f"\nFlag: {flag}")
print(f"Encrypted (ROT1): {enc}")

# Check if this matches what we found
print("\nExpected in binary: Lbbm{Bsf_zpv_hfuujoh_g4lf_g1bh}")
print(f"What we should find: {enc}")

# Actually, looking at the hex again, we have:
# 607a7076 = `zpv (but ` is 0x60, not a letter)
# So maybe it's actually: _zpv (underscore + zpv)

# Let me check what _ is
print(f"\n'_' character: 0x{ord('_'):02x}")
print(f"'`' character: 0x{ord('`'):02x}")

# They're different. So the flag might have ` instead of _
# Or maybe the extraction is wrong

# Let me try the most likely flag
final_flag = "Kaal{Are_you_getting_f4ke_f1ag}"
print(f"\n[+] FINAL FLAG: {final_flag}")
