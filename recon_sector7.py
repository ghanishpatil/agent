#!/usr/bin/env python3
"""
SECTOR-7 Reconnaissance
Check for web services, downloadable binaries, and open ports
"""

import socket
import requests
import sys

TARGET_IP = "13.206.58.35"

def check_http_services():
    """Check common HTTP ports for web services"""
    print("[*] Checking HTTP services...")
    
    for port in [80, 443, 8080, 8000, 8888, 9000]:
        for protocol in ['http', 'https']:
            url = f"{protocol}://{TARGET_IP}:{port}"
            try:
                r = requests.get(url, timeout=3, verify=False)
                print(f"\n[+] Found service at {url}")
                print(f"    Status: {r.status_code}")
                print(f"    Headers: {dict(r.headers)}")
                if r.text:
                    print(f"    Content preview: {r.text[:500]}")
                
                # Check for common paths
                for path in ['/', '/kaal', '/sector-7', '/challenge', '/binary', '/download']:
                    try:
                        r2 = requests.get(f"{url}{path}", timeout=2, verify=False)
                        if r2.status_code == 200:
                            print(f"    [+] Found: {url}{path}")
                    except:
                        pass
                        
            except Exception as e:
                pass

def scan_ports():
    """Quick scan of interesting ports"""
    print("\n[*] Scanning ports...")
    
    interesting_ports = [
        21, 22, 23, 25, 53, 80, 443, 
        1337, 3000, 5000, 6667, 7000, 8000, 8080, 8888,
        9000, 9001, 9002, 9003, 31337
    ]
    
    open_ports = []
    for port in interesting_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((TARGET_IP, port))
            if result == 0:
                open_ports.append(port)
                print(f"[+] Port {port} is OPEN")
                
                # Try to grab banner
                try:
                    sock.send(b"\n")
                    banner = sock.recv(1024)
                    if banner:
                        print(f"    Banner: {banner.decode('utf-8', errors='ignore')}")
                except:
                    pass
            sock.close()
        except:
            pass
    
    return open_ports

def main():
    print(f"[*] SECTOR-7 Reconnaissance")
    print(f"[*] Target: {TARGET_IP}\n")
    
    open_ports = scan_ports()
    check_http_services()
    
    print(f"\n[*] Summary: Found {len(open_ports)} open ports")
    if open_ports:
        print(f"    Open ports: {open_ports}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
