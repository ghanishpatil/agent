#!/usr/bin/env python3
import subprocess
import hashlib

exe = r".\challenge_mystery\crackme.exe"

# Read binary to find clues
with open(exe, 'rb') as f:
    data = f.read()

# Extract all readable strings
strings = []
current = []
for byte in data:
    if 32 <= byte <= 126:
        current.append(chr(byte))
    else:
        if len(current) >= 5:
            s = ''.join(current)
            strings.append(s)
        current = []

print("[*] Extracted strings from binary:")
interesting = [s for s in strings if 5 < len(s) < 20 and not any(x in s.lower() for x in ['section', 'critical', 'runtime', 'mingw', 'frame'])]
for s in interesting[:30]:
    print(f"  {s}")

# Try these as keys
print("\n[*] Testing extracted strings as keys...")
for s in interesting[:50]:
    try:
        result = subprocess.run([exe], input=s.encode(), capture_output=True, timeout=0.3)
        output = result.stdout.decode(errors='ignore')
        if 'Kaal{' in output:
            print(f"\n[+] FOUND: {s}")
            print(output)
            exit(0)
    except:
        pass

# Try reverse of common words
print("\n[*] Trying reversed words...")
for word in ['kaal', 'flag', 'reverse', 'crack', 'key']:
    rev = word[::-1]
    try:
        result = subprocess.run([exe], input=rev.encode(), capture_output=True, timeout=0.3)
        output = result.stdout.decode(errors='ignore')
        if 'Kaal{' in output:
            print(f"\n[+] FOUND: {rev}")
            print(output)
            exit(0)
    except:
        pass

print("\n[-] Key not found in tested strings")
