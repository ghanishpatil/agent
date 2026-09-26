#!/usr/bin/env python3
"""
Try to download the binary from the web service
"""

import requests
import socket
import time

target_ip = "13.206.58.35"

def knock_first():
    """Knock to open port 9999"""
    sequence = [9000, 2600, 1337]
    for port in sequence:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((target_ip, port))
            sock.close()
        except:
            pass
        time.sleep(0.3)

print("[*] Knocking...")
knock_first()
time.sleep(1)

# Check web service for download links
base = f"http://{target_ip}:8080"

print(f"\n[*] Checking {base} for download links...")

# Try various endpoints
endpoints = [
    "/",
    "/download",
    "/binary",
    "/sector7",
    "/kaal",
    "/challenge",
    "/file",
    "/get"
]

for endpoint in endpoints:
    try:
        r = requests.get(base + endpoint, timeout=3)
        print(f"\n[+] {endpoint} -> {r.status_code}")
        
        # Check for download links or binary content
        if r.status_code == 200:
            if "download" in r.text.lower() or "binary" in r.text.lower() or "file" in r.text.lower():
                print(f"    Content preview: {r.text[:500]}")
            
            # Check if it's a binary file
            if r.headers.get('Content-Type', '').startswith('application/'):
                print(f"    [!] Binary content detected!")
                print(f"    Content-Type: {r.headers.get('Content-Type')}")
                print(f"    Size: {len(r.content)} bytes")
                
                # Save it
                filename = f"sector7_binary{endpoint.replace('/', '_')}"
                with open(filename, 'wb') as f:
                    f.write(r.content)
                print(f"    [!] Saved to {filename}")
    except Exception as e:
        pass

# Also check if there's a robots.txt or similar
print("\n[+] Checking for hints...")
for path in ["/robots.txt", "/.git/", "/README", "/hint"]:
    try:
        r = requests.get(base + path, timeout=2)
        if r.status_code == 200:
            print(f"\n[!] Found {path}:")
            print(r.text[:300])
    except:
        pass

print("\n[*] Complete")
