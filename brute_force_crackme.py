#!/usr/bin/env python3
import subprocess
import string

# Try common keys
common_keys = [
    "password",
    "admin",
    "key",
    "flag",
    "secret",
    "1234",
    "test",
    "crackme",
    "reverse",
    "kaal",
    "Kaal",
    "KAAL",
]

print("[*] Trying common keys...")
for key in common_keys:
    try:
        result = subprocess.run(
            [r".\challenge_mystery\crackme.exe"],
            input=key + "\n",
            capture_output=True,
            text=True,
            timeout=2
        )
        
        output = result.stdout + result.stderr
        if "Flag:" in output or "Kaal{" in output:
            print(f"\n[+] KEY FOUND: {key}")
            print(f"[+] Output:\n{output}")
            break
        elif "Wrong" not in output and output.strip():
            print(f"  {key}: {output.strip()[:100]}")
    except Exception as e:
        pass

# If that doesn't work, let's just use the flag we extracted
print("\n[*] Based on binary analysis, the flag appears to be ROT25 encoded")
print("[*] The encrypted string in the binary is: Lbbm{...}")

# Let me try to find the complete string by looking at all "Lbbm" occurrences
exe = r".\challenge_mystery\crackme.exe"
with open(exe, 'rb') as f:
    data = f.read()

# Find all occurrences of "Lbbm{"
import re
matches = []
for match in re.finditer(b'Lbbm\{[^\x00]{5,50}\}', data):
    matches.append(match.group())

print(f"\n[*] Found {len(matches)} potential flag patterns:")
for m in matches:
    try:
        s = m.decode('latin1')
        # Filter out non-printable
        filtered = ''.join([c for c in s if c.isprintable()])
        
        # Apply ROT25
        dec = ''
        for c in filtered:
            if c.isalpha():
                if c.islower():
                    dec += chr((ord(c) - ord('a') + 25) % 26 + ord('a'))
                else:
                    dec += chr((ord(c) - ord('A') + 25) % 26 + ord('A'))
            else:
                dec += c
        
        if dec.startswith('Kaal{'):
            print(f"  {filtered} -> {dec}")
    except:
        pass
