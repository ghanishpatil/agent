#!/usr/bin/env python3
import subprocess
import string

exe = r".\challenge_mystery\crackme.exe"

# First, let's try to run it and see what happens
print("[*] Testing the binary with various inputs...")

test_inputs = [
    "",
    "test",
    "password",
    "key",
    "1234",
    "admin",
    "Kaal",
    "flag",
    "crackme",
]

for inp in test_inputs:
    try:
        result = subprocess.run(
            [exe],
            input=inp + "\n",
            capture_output=True,
            text=True,
            timeout=2
        )
        
        output = result.stdout + result.stderr
        if output.strip():
            print(f"\nInput: '{inp}'")
            print(f"Output: {output[:200]}")
            
            if "Kaal{" in output:
                print(f"\n[+] FOUND FLAG WITH INPUT: {inp}")
                print(output)
                break
    except Exception as e:
        print(f"Error with input '{inp}': {e}")

# Let's also try to extract all strings from the binary more carefully
print("\n[*] Extracting all strings from binary...")
with open(exe, 'rb') as f:
    data = f.read()

# Find all printable strings of length 5+
strings_found = []
current = b''
for b in data:
    if 32 <= b < 127:
        current += bytes([b])
    else:
        if len(current) >= 5:
            try:
                s = current.decode('ascii')
                if 'Kaal' in s or 'flag' in s.lower() or '{' in s:
                    strings_found.append(s)
            except:
                pass
        current = b''

print(f"\n[*] Found {len(strings_found)} interesting strings:")
for s in strings_found[:20]:
    print(f"  {s}")

# Try different cipher approaches on suspicious strings
print("\n[*] Trying different decryption methods on suspicious strings...")

suspicious = [s for s in strings_found if '{' in s or 'Lbbm' in s or 'Kaal' in s]

for s in suspicious:
    print(f"\n  String: {s}")
    
    # Try ROT
    for rot in [1, 13, 25]:
        dec = ''
        for c in s:
            if c.isalpha():
                if c.islower():
                    dec += chr((ord(c) - ord('a') + rot) % 26 + ord('a'))
                else:
                    dec += chr((ord(c) - ord('A') + rot) % 26 + ord('A'))
            else:
                dec += c
        if 'Kaal{' in dec:
            print(f"    ROT{rot}: {dec}")
    
    # Try XOR
    for key in [0x0e, 0x20, 0x42]:
        try:
            dec = ''.join([chr(ord(c) ^ key) for c in s])
            if 'Kaal{' in dec and all(c.isprintable() for c in dec):
                print(f"    XOR 0x{key:02x}: {dec}")
        except:
            pass
