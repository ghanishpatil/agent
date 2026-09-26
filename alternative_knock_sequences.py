#!/usr/bin/env python3
"""
Try alternative port knocking sequences
"""

import socket
import time
import requests

target_ip = "13.206.58.35"

def knock_sequence(ports):
    """Knock on a sequence of ports"""
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((target_ip, port))
            sock.close()
        except:
            pass
        time.sleep(0.3)

def check_pwn_service():
    """Check if port 9999 responds differently"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((target_ip, 9999))
        
        banner = sock.recv(4096)
        sock.send(b"test\n")
        response = sock.recv(4096)
        
        sock.close()
        return banner.decode('utf-8', errors='ignore'), response.decode('utf-8', errors='ignore')
    except:
        return None, None

def check_web_service():
    """Check web service for changes"""
    try:
        r = requests.get(f"http://{target_ip}:8080", timeout=2)
        return r.text
    except:
        return None

print("[*] Testing alternative knock sequences\n")

# Different sequences based on the hints
sequences = [
    # Original
    ([9000, 2600, 1337], "Original sequence"),
    
    # Reverse
    ([1337, 2600, 9000], "Reverse sequence"),
    
    # Different orders
    ([2600, 1337, 9000], "Phreaking first"),
    ([1337, 9000, 2600], "Elite first"),
    
    # Repeated knocks
    ([9000, 9000, 2600, 1337], "Double 9000"),
    ([9000, 2600, 2600, 1337], "Double 2600"),
    ([9000, 2600, 1337, 1337], "Double 1337"),
    
    # All three repeated
    ([9000, 2600, 1337, 9000, 2600, 1337], "Sequence twice"),
    
    # Just one port multiple times
    ([9000, 9000, 9000], "Triple 9000"),
    ([2600, 2600, 2600], "Triple 2600"),
    ([1337, 1337, 1337], "Triple 1337"),
    
    # Over 9000 = 9001
    ([9001, 2600, 1337], "9001 instead of 9000"),
    
    # Add more ports
    ([9000, 2600, 1337, 31337], "With 31337"),
    ([9000, 2600, 1337, 7777], "With 7777"),
    
    # Knock on 8080 too
    ([9000, 2600, 1337, 8080], "With 8080"),
    ([8080, 9000, 2600, 1337], "8080 first"),
]

for seq, desc in sequences:
    print(f"\n[*] Testing: {desc}")
    print(f"    Sequence: {seq}")
    
    knock_sequence(seq)
    time.sleep(1)
    
    # Check if anything changed
    banner, response = check_pwn_service()
    web = check_web_service()
    
    if banner and "REDACTED" not in banner:
        print(f"    [!] Banner changed: {banner[:100]}")
    
    if response and "denied" not in response.lower():
        print(f"    [!] Response changed: {response[:100]}")
    
    if web and "restricted" not in web.lower():
        print(f"    [!] Web changed: {web[:100]}")
    
    time.sleep(2)

print("\n[*] Complete")
