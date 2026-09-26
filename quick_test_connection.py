#!/usr/bin/env python3
import socket
import sys

# Try different possible IPs based on what we saw
possible_ips = [
    "212.2.250.33",
    "212.2.258.33",
    "212.2.25.33",
    "212.2.2.33",
]

port = 32384

print("Testing possible IP addresses...")
for ip in possible_ips:
    try:
        print(f"\n[*] Trying {ip}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"[+] SUCCESS! Connection to {ip}:{port} works!")
            print(f"\nUse this: python auto_pwn_notes.py {ip}:{port}")
            sock.close()
            sys.exit(0)
        else:
            print(f"[-] Failed to connect (error {result})")
        sock.close()
    except Exception as e:
        print(f"[-] Error: {e}")

print("\n[!] None of the IPs worked. Please verify the exact IP from your screen.")
