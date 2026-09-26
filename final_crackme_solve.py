#!/usr/bin/env python3

# All encrypted strings found in the binary
encrypted_strings = [
    "obuhboiQH",
    "ha{`jQmaH",
    "`i|oz{boH",
    "zga`}Ql{H",
    "zQya|`iQH",
    "`iQl|as",
    "Lbbm{BsfH",
]

# XOR key is 0x0e (14)
key = 0x0e

print("[*] Decrypting all strings with XOR key 0x0e...")
decrypted = []
for enc_str in encrypted_strings:
    dec = ''.join([chr(ord(c) ^ key) for c in enc_str])
    decrypted.append(dec)
    print(f"  {enc_str:15} -> {dec}")

# Concatenate to get the full message
full_message = ''.join(decrypted)
print(f"\n[*] Concatenated: {full_message}")

# The last string looks different - try ROT cipher on it
last_enc = "Lbbm{BsfH"
for shift in range(26):
    dec = ''
    for c in last_enc:
        if c.isalpha():
            if c.islower():
                dec += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
            else:
                dec += chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
        else:
            dec += c
    if 'Kaal' in dec:
        print(f"\n[*] ROT{shift} on '{last_enc}': {dec}")
        
# Try combining the patterns
print("\n[*] Analyzing the decrypted strings...")
print("  Strings 1-6 XOR decrypted:")
for i, s in enumerate(decrypted[:6]):
    print(f"    {i+1}. {s}")

# It looks like: "al{flag_F" + "found_coF" + "ngratulaF" + "tions_buF" + "t_worng_F" + "ng_bro}"
# The 'F' at the end might be padding or part of the encryption
# Let's remove the last character from each and see
cleaned = [s[:-1] for s in decrypted[:6]]
print("\n[*] Removing last char from each:")
for i, s in enumerate(cleaned):
    print(f"    {i+1}. {s}")

reconstructed = ''.join(cleaned)
print(f"\n[*] Reconstructed: {reconstructed}")

# The 7th string is different - it's ROT25 encoded
# "Lbbm{BsfH" with ROT25 = "Kaal{AreG"
print("\n[*] The 7th string 'Lbbm{BsfH' uses ROT25 cipher")
print("    ROT25: Kaal{AreG")

# Let's try to find the actual flag
# Pattern suggests: Kaal{flag_found_congratulations_but_worng_bro}
# But there's also "Kaal{AreG" from ROT25

# Let me check if the strings form a different pattern
print("\n[*] Possible flag patterns:")
print(f"    1. Kaal{{flag_found_congratulations_but_worng_bro}}")
print(f"    2. Kaal{{Are_you_sure_this_is_the_right_flag?}}")

# Actually, looking at the XOR results more carefully:
# "al{flag_F" suggests this is part of "Kaal{flag_..."
# Let me prepend "Ka" to the first string
flag_attempt = "Ka" + reconstructed
print(f"\n[*] Adding 'Ka' prefix: {flag_attempt}")
