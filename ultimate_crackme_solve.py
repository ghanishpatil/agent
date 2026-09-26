#!/usr/bin/env python3
import subprocess
import string

exe = r".\challenge_mystery\crackme.exe"

# Read the binary
with open(exe, 'rb') as f:
    data = f.read()

# The description says "protected message won't be immediately readable"
# This suggests the flag is encrypted and we need the right key to decrypt it

# Let's try systematic brute force with longer keys
print("[*] Testing 4-character lowercase keys...")
import itertools

count = 0
for combo in itertools.product(string.ascii_lowercase, repeat=4):
    if count > 10000:  # Limit for speed
        break
    
    key = ''.join(combo)
    count += 1
    
    if count % 1000 == 0:
        print(f"  Tested {count} keys...")
    
    try:
        result = subprocess.run([exe], input=key.encode(), capture_output=True, timeout=0.2)
        output = result.stdout.decode(errors='ignore')
        
        if 'Kaal{' in output:
            print(f"\n[+] FOUND KEY: {key}")
            print(f"    Output: {output}")
            exit(0)
        elif 'Flag:' in output and 'Wrong' not in output:
            print(f"\n[?] Interesting: {key} -> {output[:100]}")
    except:
        pass

print(f"\n[-] Tested {count} keys, none worked")
print("\n[*] The key might be longer or use special characters")
print("[*] Trying common CTF patterns...")

patterns = [
    'kaal', 'Kaal', 'KAAL',
    'ctf', 'CTF',
    'flag', 'FLAG',
    'reverse', 'REVERSE',
    'crack', 'CRACK',
    'password', 'PASSWORD',
    'secret', 'SECRET',
    'admin', 'ADMIN',
    '1234', '12345', '123456',
    'kaalchakra', 'KaalChakra',
]

for p in patterns:
    try:
        result = subprocess.run([exe], input=p.encode(), capture_output=True, timeout=0.5)
        output = result.stdout.decode(errors='ignore')
        if 'Kaal{' in output:
            print(f"[+] FOUND: {p}")
            print(output)
            exit(0)
    except:
        pass
