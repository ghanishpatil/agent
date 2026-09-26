#!/usr/bin/env python3
"""
Check what's running on port 8080
"""

import requests
import socket

target = "http://13.206.58.35:8080"

print(f"[*] Checking {target}")

try:
    # Try basic GET request
    print("\n[+] Sending GET request to /")
    r = requests.get(target, timeout=5)
    print(f"    Status: {r.status_code}")
    print(f"    Headers: {dict(r.headers)}")
    print(f"    Content:\n{r.text[:500]}")
    
    # Try common paths
    paths = ["/KAAL", "/kaal", "/sector-7", "/SECTOR-7", "/gate", "/knock"]
    print("\n[+] Trying common paths...")
    for path in paths:
        try:
            r = requests.get(target + path, timeout=3)
            if r.status_code != 404:
                print(f"  [!] {path} -> {r.status_code}")
                print(f"      {r.text[:200]}")
        except:
            pass
    
    # Try sending KAAL as POST data
    print("\n[+] Trying POST with KAAL...")
    r = requests.post(target, data={"name": "KAAL"}, timeout=3)
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.text[:200]}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# Also try raw socket connection
print("\n[+] Trying raw socket connection to port 8080...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect(("13.206.58.35", 8080))
    
    # Send HTTP request
    request = b"GET / HTTP/1.1\r\nHost: 13.206.58.35\r\n\r\n"
    sock.send(request)
    response = sock.recv(4096)
    print(f"Response:\n{response.decode('utf-8', errors='ignore')[:500]}")
    
    sock.close()
except Exception as e:
    print(f"[-] Socket error: {e}")
