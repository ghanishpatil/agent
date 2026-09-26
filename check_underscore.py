#!/usr/bin/env python3

# Check what 0x60 is
print(f"0x60 = '{chr(0x60)}' (backtick)")
print(f"0x5f = '{chr(0x5f)}' (underscore)")

# So the encrypted string has 0x60 (backtick)
# In ROT25, backtick stays as backtick (it's not a letter)

# Let me check if maybe it should be underscore
# If the decrypted flag should have underscore, what would the encrypted version have?
# Underscore is not a letter, so it stays as underscore in ROT

# So the flag is: Kaal{Are`youetf4ke1ag}
# But that doesn't make sense

# Let me try different interpretations:
# Maybe the parts are: Lbbm{Bsf_`zpv_fu_g4l_f1bh}
# Where _ is used as separator

test_flags = [
    "Lbbm{Bsf`zpvfug4lf1bh}",
    "Lbbm{Bsf_`zpv_fu_g4l_f1bh}",
    "Lbbm{Bsf_zpv_fu_g4l_f1bh}",  # Remove backtick
]

print("\n[*] Testing different interpretations:")
for enc in test_flags:
    dec = ''
    for c in enc:
        if c.isalpha():
            if c.islower():
                dec += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
            else:
                dec += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
        else:
            dec += c
    print(f"  {enc:35} -> {dec}")

# Wait, maybe I'm extracting the wrong bytes
# Let me look at the hex again more carefully
# The pattern might be that certain bytes are part of the string and others are assembly

# Let me try to find the actual correct flag by looking at what makes sense
# "Are you et f4ke1ag" doesn't make sense
# "Are you getting fake flag" would make sense

# So the encrypted version should be:
# Kaal{Are_you_getting_fake_flag}
# ROT1: Lbbm{Bsf_zpv_hfuujoh_gblf_gmbh}

target_enc = "Lbbm{Bsf_zpv_hfuujoh_gblf_gmbh}"
print(f"\n[*] Expected encrypted string: {target_enc}")
print(f"  Length: {len(target_enc)}")

# Now let me check what we actually have in the hex
hex_str = "4c62626d7b42736648ba607a707622486675488945d0488955d848b8224866752267346c48ba3422663162687d"
data = bytes.fromhex(hex_str)

print(f"\n[*] Actual hex data length: {len(data)}")

# Let me search for the substrings:
# "hfuujoh" (getting) = 68 66 75 75 6a 6f 68
# "gblf" (fake) = 67 62 6c 66
# "gmbh" (flag) = 67 6d 62 68

print("\n[*] Searching for expected substrings in hex:")
if b'hfuujoh' in data:
    print("  Found 'hfuujoh' (getting)")
else:
    print("  NOT found 'hfuujoh' (getting)")

if b'gblf' in data:
    print("  Found 'gblf' (fake)")
else:
    print("  NOT found 'gblf' (fake)")

if b'gmbh' in data:
    print("  Found 'gmbh' (flag)")
else:
    print("  NOT found 'gmbh' (flag)")

# So the actual encrypted string is NOT "getting_fake_flag"
# It's something else

# Let me decode what we actually have:
# Lbbm{Bsf`zpvfug4lf1bh}
# Kaal{Are`youetf4ke1ag}

# Maybe it's leet speak: "Are you getting f4ke fl4g"?
# But we only have "et" not "getting"

# Or maybe: "Are you et f4ke f1ag" = "Are you eating fake flag"?

# Let me check if there's more data after the } that I'm missing
print("\n[*] Checking if there's more data after the closing brace...")
brace_idx = hex_str.find('7d')  # 0x7d = '}'
if brace_idx != -1:
    print(f"  '}}' found at position {brace_idx//2}")
    after_brace = hex_str[brace_idx+2:]
    print(f"  Data after: {after_brace}")
    
    if after_brace:
        after_bytes = bytes.fromhex(after_brace)
        print(f"  As ASCII: {after_bytes}")

# I think the flag is just: Kaal{Are_you_getting_f4ke_fl4g}
# But the binary has it abbreviated or with leet speak
# Let me just try submitting what we have

print("\n[+] BEST GUESS FLAG: Kaal{Are_you_getting_f4ke_fl4g}")
