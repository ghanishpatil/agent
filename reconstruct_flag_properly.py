#!/usr/bin/env python3

# From the analysis, the encrypted sequences are:
# Lbbm{BsfH`zpv"HfuH"Hfu"g4lH4"f1bh}

# But there's assembly code mixed in. Let me look at the pattern:
# The 'H' characters appear to be part of x64 assembly (REX prefix)
# Let's filter those out and keep only the actual string data

encrypted = "Lbbm{Bsf_`zpv_fu_g4l_f1bh}"

# Wait, let me look at the hex again more carefully
# 4c62626d7b42736648 = Lbbm{BsfH
# ba = separator
# 607a7076 = `zpv  
# 22 = "
# 486675 = Hfu
# ...

# The pattern suggests: Lbbm{Bsf_`zpv_fu_g4l_f1bh}
# But we need to figure out the actual structure

# Let me try different combinations
candidates = [
    "Lbbm{Bsf_`zpv_fu_g4l_f1bh}",
    "Lbbm{Bsf`zpvfug4lf1bh}",
    "Lbbm{Bsf_`zpv_Hfu_g4l_f1bh}",
    "Lbbm{Are_you_getting_flag}",  # Guessing based on the pattern
]

print("[*] Trying different flag reconstructions...")
for enc in candidates:
    # Apply ROT25
    dec = ''
    for c in enc:
        if c.isalpha():
            if c.islower():
                dec += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
            else:
                dec += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
        else:
            dec += c
    
    print(f"  {enc:40} -> {dec}")

# Based on the sequences we extracted:
# "Kaal{AreG" + "`you" + "et" + "f4k" + "e1ag}"
# This could be: "Kaal{Are_you_getting_fake_flag}"

# Let me reverse engineer what the encrypted version would be
test_flags = [
    "Kaal{Are_you_getting_fake_flag}",
    "Kaal{Are_you_getting_the_flag}",
    "Kaal{Are_you_getting_real_flag}",
]

print("\n[*] Reverse engineering - what would these encrypt to with ROT25?")
for flag in test_flags:
    enc = ''
    for c in flag:
        if c.isalpha():
            if c.islower():
                enc += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))  # ROT1 = reverse of ROT25
            else:
                enc += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
        else:
            enc += c
    print(f"  {flag:40} -> {enc}")

# Actually, looking at the extracted pieces again:
# Kaal{AreG + `you + Get + f4k + e1ag}
# Could be: "Kaal{Are_you_getting_fake_flag}" or similar

# Let me check what "getting" would be in ROT1
test = "getting"
rot1 = ''.join([chr((ord(c) - ord('a') + 1) % 26 + ord('a')) for c in test])
print(f"\n[*] 'getting' in ROT1: {rot1}")

# And "fake"
test = "fake"
rot1 = ''.join([chr((ord(c) - ord('a') + 1) % 26 + ord('a')) for c in test])
print(f"[*] 'fake' in ROT1: {rot1}")

# And "flag"
test = "flag"
rot1 = ''.join([chr((ord(c) - ord('a') + 1) % 26 + ord('a')) for c in test])
print(f"[*] 'flag' in ROT1: {rot1}")

# So the encrypted string should contain "hfuujoh" for "getting"
# and "gblf" for "fake"
# and "gmbh" for "flag"

# Looking at our hex: "fu" appears, and "g4l" and "f1bh"
# "g4l" doesn't match "gblf" (fake)
# "f1bh" is close to "gmbh" (flag) but with numbers

# Maybe the flag is: Kaal{Are_you_getting_f4ke_fl4g}
# Where 'a' is replaced with '4' and 'a' with '4'

print("\n[*] Testing with leet speak...")
test_flag = "Kaal{Are_you_getting_f4ke_fl4g}"
print(f"  Possible flag: {test_flag}")

# Encrypt it with ROT1
enc = ''
for c in test_flag:
    if c.isalpha():
        if c.islower():
            enc += chr((ord(c) - ord('a') + 1) % 26 + ord('a'))
        else:
            enc += chr((ord(c) - ord('A') + 1) % 26 + ord('A'))
    else:
        enc += c
print(f"  Would encrypt to: {enc}")

# Check if this matches what we found
print("\n[*] Checking against extracted sequences...")
print("  Expected: Lbbm{Bsf_zpv_hfuujoh_g4lf_gm4h}")
print("  Found pieces: Lbbm{BsfH`zpv...fu...g4l...f1bh}")
