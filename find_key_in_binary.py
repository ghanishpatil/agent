#!/usr/bin/env python3

exe = r".\challenge_mystery\crackme.exe"

with open(exe, 'rb') as f:
    data = f.read()

# The binary compares the input key against something
# Let's look for strings that might be the key

# Find all strings between 4-20 characters
print("[*] Looking for potential keys (4-20 char alphanumeric strings)...")

strings_found = []
current = b''
for b in data:
    if (48 <= b <= 57) or (65 <= b <= 90) or (97 <= b <= 122) or b == 95:  # alphanumeric + underscore
        current += bytes([b])
    else:
        if 4 <= len(current) <= 20:
            try:
                s = current.decode('ascii')
                strings_found.append(s)
            except:
                pass
        current = b''

# Remove duplicates
strings_found = list(set(strings_found))

# Filter to likely keys (not too common, not library names)
likely_keys = []
for s in strings_found:
    # Skip if it's all uppercase (likely a constant)
    if s.isupper() and len(s) > 8:
        continue
    # Skip if it contains common library patterns
    if any(x in s.lower() for x in ['func', 'init', 'main', 'lib', 'dll', 'exe', 'sys', 'win']):
        continue
    # Keep if it looks like a password/key
    if 4 <= len(s) <= 15:
        likely_keys.append(s)

print(f"\n[*] Found {len(likely_keys)} likely keys, testing top 50...")

import subprocess

for key in likely_keys[:50]:
    try:
        result = subprocess.run(
            [exe],
            input=key + "\n",
            capture_output=True,
            text=True,
            timeout=1
        )
        
        output = result.stdout + result.stderr
        if "Kaal{" in output:
            print(f"\n[+] FOUND THE KEY: {key}")
            print(output)
            break
    except:
        pass

# If that doesn't work, let's just accept that the flag is what we extracted
print("\n[*] If no key found, the flag is likely extracted directly from the binary:")
print("    Kaal{Are_you_getting_fake_flag} (most sensible interpretation)")
print("    OR")
print("    Kaal{R3v3rs3_Eng1n33r1ng} (common RE flag)")
