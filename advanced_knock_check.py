#!/usr/bin/env python3
"""
Advanced port knocking with immediate checks
"""

import socket
import time
import requests
from threading import Thread

target_ip = "13.206.58.35"

def knock_sequence(ports):
    """Knock on a sequence of ports"""
    print(f"[*] Knocking sequence: {ports}")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((target_ip, port))
            sock.close()
            print(f"    ✓ Port {port}")
        except:
            print(f"    ✗ Port {port} (knocked)")
        time.sleep(0.3)

def check_all_endpoints():
    """Check various endpoints after knocking"""
    base = f"http://{target_ip}:8080"
    
    endpoints = [
        "/",
        "/download",
        "/flag",
        "/KAAL",
        "/kaal",
        "/sector7",
        "/entry",
        "/access",
        "/gate",
        "/unlock"
    ]
    
    print("\n[+] Checking endpoints...")
    for endpoint in endpoints:
        try:
            r = requests.get(base + endpoint, timeout=2)
            if r.status_code == 200 and len(r.text) > 100:
                print(f"  [!] {endpoint} -> {r.status_code}")
                if "flag" in r.text.lower() or "kaal{" in r.text.lower() or "download" in r.text.lower():
                    print(f"      Content: {r.text[:300]}")
        except:
            pass

def scan_new_ports():
    """Scan for newly opened ports after knocking"""
    print("\n[+] Scanning for newly opened ports...")
    interesting_ports = [7777, 31337, 1234, 4321, 5555, 6666, 7890, 8888, 9999, 10000]
    
    for port in interesting_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                print(f"  [!] Port {port} is NOW OPEN!")
                # Try to interact
                try:
                    sock.send(b"KAAL\n")
                    response = sock.recv(4096)
                    if response:
                        print(f"      Response: {response.decode('utf-8', errors='ignore')[:200]}")
                except:
                    pass
            sock.close()
        except:
            pass

# Try the most likely sequence
sequences = [
    [9000, 2600, 1337],
    [9001, 2600, 1337],  # "over 9000" could mean 9001
    [1337, 2600, 9000],
    [2600, 9000, 1337],
]

for seq in sequences:
    print(f"\n{'='*70}")
    print(f"Testing sequence: {seq}")
    print(f"{'='*70}")
    
    knock_sequence(seq)
    
    # Immediately check for changes
    check_all_endpoints()
    scan_new_ports()
    
    time.sleep(3)

print("\n[*] Complete")
