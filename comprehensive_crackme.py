#!/usr/bin/env python3
import subprocess
import itertools
import string

exe = r".\challenge_mystery\crackme.exe"

# Try all 2-character combinations of common chars
print("[*] Testing 2-char combinations...")
chars = string.ascii_letters + string.digits
for combo in itertools.islice(itertools.product(chars, repeat=2), 500):
    key = ''.join(combo)
    try:
        result = subprocess.run([exe], input=key.encode(), capture_output=True, timeout=0.3)
        output = result.stdout.decode(errors='ignore')
        if 'Kaal{' in output:
            print(f"[+] FOUND: {key}")
            print(output)
            exit(0)
    except:
        pass

# Try 3-char
print("\n[*] Testing 3-char combinations...")
for combo in itertools.islice(itertools.product(string.ascii_lowercase, repeat=3), 1000):
    key = ''.join(combo)
    try:
        result = subprocess.run([exe], input=key.encode(), capture_output=True, timeout=0.3)
        output = result.stdout.decode(errors='ignore')
        if 'Kaal{' in output:
            print(f"[+] FOUND: {key}")
            print(output)
            exit(0)
    except:
        pass

print("[-] Not found in tested combinations")
