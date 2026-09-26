#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# The strings we found are at specific locations
# Let's find them and see what's around them
strings_to_find = [
    b"obuhboiQH",
    b"ha{`jQmaH",
    b"`i|oz{boH",
    b"zga`}Ql{H",
    b"zQya|`iQH",
    b"`iQl|as",
    b"Lbbm{BsfH",
]

print("[*] Finding encrypted strings in binary...")
positions = []
for s in strings_to_find:
    idx = data.find(s)
    if idx != -1:
        positions.append((idx, s))
        print(f"  {s.decode('latin1'):15} at offset {hex(idx)}")

# Sort by position
positions.sort()

print("\n[*] Strings in order of appearance:")
for pos, s in positions:
    print(f"  {hex(pos)}: {s.decode('latin1')}")

# Check if they're consecutive
print("\n[*] Checking if strings are consecutive...")
for i in range(len(positions)-1):
    pos1, s1 = positions[i]
    pos2, s2 = positions[i+1]
    gap = pos2 - (pos1 + len(s1))
    print(f"  Gap between string {i+1} and {i+2}: {gap} bytes")
    if gap > 0 and gap < 10:
        between = data[pos1+len(s1):pos2]
        print(f"    Data between: {between.hex()} ({between})")

# XOR decrypt with key 0x0e
key = 0x0e
print("\n[*] XOR decrypting with key 0x0e:")
decrypted_parts = []
for pos, s in positions:
    dec = ''.join([chr(b ^ key) for b in s])
    decrypted_parts.append(dec)
    print(f"  {s.decode('latin1'):15} -> {dec}")

# Try to reconstruct the flag
print("\n[*] Attempting to reconstruct flag...")

# The decrypted parts suggest: "al{flag_" + "found_co" + "ngratula" + "tions_bu" + "t_worng_" + "ng_bro}"
# This looks like: "Kaal{flag_found_congratulations_but_worng_ng_bro}"
# But that doesn't make sense. Let me look at the actual message

# Maybe the strings form a sentence when decrypted
full_decrypt = ''.join(decrypted_parts)
print(f"  Full concatenation: {full_decrypt}")

# Let's try removing the 'F' characters that appear at the end of each part
cleaned = []
for dec in decrypted_parts[:-1]:  # Skip the last one
    if dec.endswith('F'):
        cleaned.append(dec[:-1])
    else:
        cleaned.append(dec)

# Add the last one as-is
cleaned.append(decrypted_parts[-1])

reconstructed = ''.join(cleaned)
print(f"  Cleaned: {reconstructed}")

# Add "Ka" prefix to make it "Kaal{...}"
flag = "Ka" + reconstructed
print(f"\n[*] Possible flag: {flag}")

# But wait - the last string "Lbbm{BsfH" might be separate
# Let's check if it's actually the real flag with ROT cipher
last_string = b"Lbbm{BsfH"
print(f"\n[*] Analyzing last string separately: {last_string.decode()}")

# Try ROT on it
for shift in range(26):
    dec = ''
    for c in last_string.decode():
        if c.isalpha():
            if c.islower():
                dec += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
            else:
                dec += chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
        else:
            dec += c
    if 'Kaal' in dec or 'flag' in dec.lower():
        print(f"  ROT{shift}: {dec}")
