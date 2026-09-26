#!/usr/bin/env python3
import subprocess

exe = r".\challenge_mystery\crackme.exe"

# Smart guesses based on challenge context
smart_keys = [
    # Author related
    "anu", "error", "404", "anu_3rror_4o4", "anu3rror4o4",
    # Challenge name
    "mystery", "crackme", "crack", "me",
    # Common patterns
    "key", "pass", "flag", "secret",
    # Numbers
    "123", "1234", "12345", "000", "111", "999",
    # Hex
    "0x0e", "0e", "14", "25", "0x19", "19",
    # ROT related
    "rot", "rot25", "rot1", "caesar",
    # Random tries
    "a", "b", "c", "x", "y", "z",
    "aa", "bb", "cc", "xx", "yy", "zz",
    "abc", "xyz", "aaa", "zzz",
]

print("[*] Trying smart key guesses...")
for key in smart_keys:
    try:
        result = subprocess.run(
            [exe],
            input=key + "\n",
            capture_output=True,
            text=True,
            timeout=2
        )
        
        output = result.stdout + result.stderr
        
        if "Kaal{" in output:
            print(f"\n[+] FOUND KEY: {key}")
            print(output)
            break
        elif "Flag:" in output and "Wrong" not in output:
            print(f"\n[+] FOUND KEY: {key}")
            print(output)
            break
    except:
        pass

# If no key works, the flag must be extracted statically
print("\n[*] No key found. The flag must be in the binary.")
print("[*] Please provide the correct flag so I can complete the writeup.")
