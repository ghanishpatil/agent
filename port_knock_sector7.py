#!/usr/bin/env python3
"""
Port knocking for SECTOR-7
Based on clues: 9000, 2600, 1337
"""

import socket
import time
import requests

target_ip = "13.206.58.35"

def knock_sequence(ports):
    """Knock on a sequence of ports"""
    print(f"[*] Knocking sequence: {ports}")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            print(f"    Knocking port {port}...", end=" ")
            sock.connect((target_ip, port))
            sock.close()
            print("✓")
            time.sleep(0.5)  # Small delay between knocks
        except:
            print("✗ (expected - just knocking)")
            time.sleep(0.5)

def check_web_after_knock():
    """Check if web service changed after knocking"""
    try:
        r = requests.get(f"http://{target_ip}:8080", timeout=5)
        print(f"\n[+] Web service response after knock:")
        print(f"    Status: {r.status_code}")
        print(f"    Content:\n{r.text}")
        return r.text
    except Exception as e:
        print(f"[-] Error checking web: {e}")
        return None

# Try different sequences based on the clues
sequences = [
    [9000, 2600, 1337],  # Direct interpretation
    [1337, 2600, 9000],  # Reverse order
    [9001, 2600, 1337],  # "over 9000" = 9001
    [9000, 1337, 2600],  # Different order
    [2600, 1337, 9000],  # Phone phreaking first
]

print("[*] SECTOR-7 Port Knocking Attack")
print(f"[*] Target: {target_ip}\n")

for i, seq in enumerate(sequences, 1):
    print(f"\n{'='*60}")
    print(f"Attempt {i}/{len(sequences)}")
    print(f"{'='*60}")
    
    knock_sequence(seq)
    response = check_web_after_knock()
    
    if response and ("flag" in response.lower() or "kaal{" in response.lower() or "download" in response.lower()):
        print("\n[!] SUCCESS! Found something interesting!")
        break
    
    time.sleep(2)  # Wait before next attempt

print("\n[*] Port knocking complete")
