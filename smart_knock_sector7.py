#!/usr/bin/env python3
"""
SECTOR-7 Smart Port Knocking
Based on deeper analysis of clues
"""

import socket
import time
import requests

TARGET_IP = "13.206.58.35"
WEB_URL = "http://13.206.58.35:8080"

def knock_sequence(ports):
    """Knock on ports in sequence"""
    print(f"[*] Knocking: {ports}")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((TARGET_IP, port))
            sock.close()
        except:
            pass
        time.sleep(0.3)

def check_challenge_endpoint():
    """Check if /challenge endpoint is now accessible"""
    try:
        r = requests.get(f"{WEB_URL}/challenge", timeout=3)
        print(f"[*] /challenge status: {r.status_code}")
        if r.status_code == 200:
            print(f"[+] SUCCESS! Content:\n{r.text}")
            return True
        elif r.status_code != 403:
            print(f"[?] Unexpected status: {r.text[:200]}")
    except Exception as e:
        print(f"[-] Error: {e}")
    return False

def main():
    print("[*] SECTOR-7 Smart Knock Solver")
    print("[*] Analyzing clues:")
    print("    - 'His number' = IMEI or #06# (phone code)")
    print("    - 'over 9000' = Port 9000+")
    print("    - 'Three echoes' = 3 ports")
    print("    - '90s era' = 1990s references\n")
    
    # New sequences based on deeper analysis
    sequences = [
        # #06# reference (0, 6, and something over 9000)
        [0, 6, 9000],
        [6, 0, 9001],
        [60, 90, 9000],
        
        # IMEI-related (15 digits, use parts)
        [15, 90, 9000],
        [1, 5, 9000],
        
        # Dragon Ball Z "over 9000" meme from 90s
        [9000, 9001, 9002],
        [8999, 9000, 9001],
        
        # Phone dial codes
        [0, 6, 9001],
        [6, 9000, 9001],
        
        # 1337 speak + 9000
        [1, 3, 9000],
        [13, 37, 9000],
        [1337, 9000, 9001],
        
        # DTMF + 9000
        [697, 9000, 9001],
        [770, 9000, 9001],
        
        # Try reverse
        [9000, 6, 0],
        [9001, 90, 60],
        
        # Classic sequences
        [7000, 8000, 9000],
        [6000, 7000, 8000],
    ]
    
    for seq in sequences:
        knock_sequence(seq)
        time.sleep(0.5)
        
        if check_challenge_endpoint():
            print(f"\n[+] WINNING SEQUENCE: {seq}")
            return
        
        time.sleep(1)
    
    print("\n[-] No sequence worked. Need more clues.")

if __name__ == "__main__":
    main()
