#!/usr/bin/env python3
import subprocess

exe = r".\challenge_mystery\crackme.exe"

# Keys found in the binary
test_keys = [
    "singularity",
    "significance",
    "VirtualQuery",
    "deregister",
    "represented",
    # Try variations
    "singular",
    "signific",
    # Try the author name
    "anu_3rror_4o4",
    "anu",
    "error",
    "404",
    # Try challenge related
    "mystery",
    "crackme",
    "reverse",
]

print("[*] Testing found keys...")
for key in test_keys:
    try:
        result = subprocess.run(
            [exe],
            input=key + "\n",
            capture_output=True,
            text=True,
            timeout=2
        )
        
        output = result.stdout + result.stderr
        if "Kaal{" in output or "Flag:" in output:
            print(f"\n[+] FOUND THE KEY: {key}")
            print(output)
            break
        elif "Wrong" not in output:
            print(f"  {key}: {output[:100]}")
    except Exception as e:
        pass

print("\n[*] Testing complete")

# If none work, let's just extract the flag directly from the binary
# We know it's at 0x145a and is ROT25 encoded

print("\n[*] Extracting flag directly from binary...")
with open(exe, 'rb') as f:
    data = f.read()

# Find the encrypted flag
idx = data.find(b'Lbbm{')
if idx != -1:
    # Extract until null or non-printable
    flag_bytes = []
    i = idx
    while i < len(data) and i < idx + 100:
        b = data[i]
        if b == 0:
            break
        if 32 <= b < 127:
            flag_bytes.append(b)
        i += 1
    
    encrypted = bytes(flag_bytes).decode('latin1')
    print(f"  Encrypted: {encrypted}")
    
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
    
    # Clean up - remove non-flag characters
    if 'Kaal{' in decrypted:
        start = decrypted.find('Kaal{')
        end = decrypted.find('}', start)
        if end != -1:
            flag = decrypted[start:end+1]
            # Remove any non-printable or weird characters
            flag_clean = ''.join([c for c in flag if c.isprintable()])
            print(f"  Decrypted: {flag_clean}")
            print(f"\n[+] FLAG (extracted): {flag_clean}")
