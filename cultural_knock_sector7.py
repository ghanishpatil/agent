#!/usr/bin/env python3
"""
SECTOR-7 Cultural Reference Knocking
Try sequences based on 90s hacker/phone culture
"""

import socket
import time
import requests

TARGET_IP = "13.206.58.35"
WEB_URL = "http://13.206.58.35:8080"

def knock_sequence(ports, description=""):
    """Knock on ports in sequence"""
    print(f"[*] Trying: {description}")
    print(f"    Sequence: {ports}")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((TARGET_IP, port))
            sock.close()
        except:
            pass
        time.sleep(0.3)

def check_access():
    """Check if access is granted"""
    try:
        r = requests.get(f"{WEB_URL}/challenge", timeout=3)
        if r.status_code == 200:
            print(f"\n[+] SUCCESS! Access granted!")
            print(f"{r.text}\n")
            return True
        return False
    except:
        return False

def main():
    print("[*] SECTOR-7 Cultural Reference Solver\n")
    
    sequences = [
        # 2600 Hz - phone phreaking frequency (THE hacker number)
        ([2600, 9000, 9001], "2600 Hz phreaking frequency"),
        ([26, 00, 9000], "2600 split"),
        ([2, 6, 9000], "2600 digits"),
        
        # 867-5309 (famous phone number)
        ([867, 5309, 9000], "867-5309 Tommy Tutone"),
        ([8675, 309, 9000], "867-5309 split"),
        
        # Blue Box tones (2600 + others)
        ([2600, 2400, 9000], "Blue box tones"),
        
        # Captain Crunch whistle (2600 Hz)
        ([2600, 1337, 9000], "Cap'n Crunch + leet"),
        
        # Phone keypad sequences
        ([2, 3, 9000], "ABC on phone"),
        ([4, 5, 6], "DEF-GHI-MNO"),
        ([7, 8, 9], "PQRS-TUV-WXYZ"),
        
        # IMEI related
        ([0, 6, 9000], "#06# IMEI code"),
        ([3, 5, 9000], "#35# IMEI code variant"),
        
        # 90s BBS/IRC ports
        ([6667, 31337, 9000], "IRC + elite"),
        ([23, 110, 9000], "Telnet + POP3"),
        
        # War Games reference (1983 but influential)
        ([1, 9, 83], "War Games year"),
        ([1983, 9000, 9001], "War Games full"),
        
        # Matrix reference (1999)
        ([1, 9, 99], "Matrix year"),
        ([1999, 9000, 9001], "Matrix full"),
        
        # Hackers movie (1995)
        ([1, 9, 95], "Hackers year"),
        ([1995, 9000, 9001], "Hackers full"),
        
        # Try all 2600 variations
        ([2600, 2600, 2600], "Triple 2600"),
        ([2600, 6002, 9000], "2600 reversed"),
    ]
    
    for seq, desc in sequences:
        knock_sequence(seq, desc)
        time.sleep(0.5)
        
        if check_access():
            print(f"[+] WINNING SEQUENCE: {seq} ({desc})")
            return
        
        time.sleep(1)
    
    print("\n[-] No cultural reference worked.")
    print("[*] May need to look for more specific clues in the challenge.")

if __name__ == "__main__":
    main()
