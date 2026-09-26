#!/usr/bin/env python3
import subprocess
import string
import itertools

exe = r".\challenge_mystery\crackme.exe"

print("[*] Brute forcing the key...")

# Try common patterns
patterns = [
    # Common words
    "secret", "password", "admin", "root", "key", "unlock",
    # Numbers
    "1234", "12345", "123456", "0000", "9999",
    # CTF related
    "flag", "kaal", "Kaal", "KAAL", "crackme", "reverse",
    # Hex patterns
    "0x0e", "0x42", "0xdead", "0xbeef",
    # Author hint
    "anu", "error", "404", "anu_3rror_4o4",
]

for key in patterns:
    try:
        result = subprocess.run(
            [exe],
            input=key + "\n",
            capture_output=True,
            text=True,
            timeout=2
        )
        
        output = result.stdout + result.stderr
        if "Wrong" not in output and output.strip() and "Enter key:" in output:
            # Check what comes after "Enter key:"
            after_prompt = output.split("Enter key:")[-1].strip()
            if after_prompt and after_prompt != "Wrong key!":
                print(f"\n[+] Possible key: {key}")
                print(f"Output: {output}")
                
                if "Kaal{" in output or "Flag:" in output:
                    print(f"\n[+] FOUND THE KEY: {key}")
                    break
    except Exception as e:
        pass

# Try single character keys
print("\n[*] Trying single character keys...")
for c in string.printable:
    try:
        result = subprocess.run(
            [exe],
            input=c + "\n",
            capture_output=True,
            text=True,
            timeout=1
        )
        
        output = result.stdout + result.stderr
        if "Wrong" not in output and "Enter key:" in output:
            after_prompt = output.split("Enter key:")[-1].strip()
            if after_prompt and after_prompt != "Wrong key!":
                print(f"  Char '{c}' (0x{ord(c):02x}): {after_prompt[:50]}")
                
                if "Kaal{" in output:
                    print(f"\n[+] FOUND KEY: '{c}'")
                    print(output)
                    break
    except:
        pass

# Try 2-character combinations of common chars
print("\n[*] Trying 2-character combinations...")
for combo in itertools.product(string.ascii_lowercase + string.digits, repeat=2):
    key = ''.join(combo)
    try:
        result = subprocess.run(
            [exe],
            input=key + "\n",
            capture_output=True,
            text=True,
            timeout=1
        )
        
        output = result.stdout + result.stderr
        if "Kaal{" in output or ("Wrong" not in output and "Flag:" in output):
            print(f"\n[+] FOUND KEY: {key}")
            print(output)
            break
    except:
        pass
    
    # Print progress every 100 attempts
    if (ord(combo[0]) * 36 + (ord(combo[1]) - ord('0') if combo[1].isdigit() else ord(combo[1]) - ord('a') + 10)) % 100 == 0:
        print(f"  Tried: {key}")

print("\n[*] Brute force complete")
