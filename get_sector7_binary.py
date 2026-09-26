#!/usr/bin/env python3
"""
Try to get the SECTOR-7 binary for analysis
"""

import socket
import time
import requests

TARGET_IP = "13.206.58.35"
WEB_URL = "http://13.206.58.35:8080"
KNOCK_SEQUENCE = [9000, 2600, 1337]
SERVICE_PORT = 9999

def knock_ports():
    """Perform port knocking"""
    for port in KNOCK_SEQUENCE:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((TARGET_IP, port))
            sock.close()
        except:
            pass
        time.sleep(0.3)
    time.sleep(1)

def check_web_after_knock():
    """Check if web service provides download after knocking"""
    print("[*] Checking web service after knocking...")
    
    try:
        r = requests.get(f"{WEB_URL}/challenge", timeout=3)
        print(f"    /challenge status: {r.status_code}")
        if r.status_code == 200:
            print(f"    Content: {r.text}")
            return r.text
        
        # Try other paths
        for path in ['/download', '/binary', '/kaal', '/sector7', '/file']:
            r = requests.get(f"{WEB_URL}{path}", timeout=3)
            if r.status_code == 200:
                print(f"[+] Found: {WEB_URL}{path}")
                print(f"    Content-Type: {r.headers.get('Content-Type')}")
                
                # Save if it's a binary
                if 'application' in r.headers.get('Content-Type', ''):
                    with open('sector7_binary', 'wb') as f:
                        f.write(r.content)
                    print(f"[+] Saved binary to sector7_binary")
                else:
                    print(f"    Content: {r.text[:500]}")
                return r.text
    except Exception as e:
        print(f"    Error: {e}")
    
    return None

def try_service_commands():
    """Try commands on the service to get binary"""
    print("\n[*] Trying service commands...")
    
    knock_ports()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((TARGET_IP, SERVICE_PORT))
        
        # Receive banner
        banner = sock.recv(4096)
        print(f"[+] Connected to service")
        
        # Try commands that might give us the binary or more info
        commands = [
            b"download\n",
            b"binary\n",
            b"file\n",
            b"help\n",
            b"info\n",
            b"version\n",
            b"?\n",
            b"get\n",
            b"fetch\n",
        ]
        
        for cmd in commands:
            sock.send(cmd)
            time.sleep(0.5)
            try:
                response = sock.recv(4096)
                if response and len(response) > 50:
                    print(f"\n[+] Command {cmd.strip()} gave response:")
                    print(response.decode('utf-8', errors='ignore')[:200])
            except:
                pass
        
        sock.close()
    except Exception as e:
        print(f"    Error: {e}")

def main():
    print("[*] SECTOR-7 Binary Retrieval")
    print(f"[*] Target: {TARGET_IP}\n")
    
    # Try knocking then checking web
    knock_ports()
    result = check_web_after_knock()
    
    # Try service commands
    try_service_commands()
    
    print("\n[*] If no binary found, we need to:")
    print("    1. Brute force the password")
    print("    2. Or exploit the buffer overflow blind")

if __name__ == "__main__":
    main()
