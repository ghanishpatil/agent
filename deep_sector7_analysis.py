#!/usr/bin/env python3
"""
Deep analysis of SECTOR-7 challenge
Try different interaction methods with KAAL
"""

import socket
import requests
import time

TARGET_IP = "13.206.58.35"
WEB_URL = "http://13.206.58.35:8080"

def try_tcp_kaal_service():
    """Try to connect to KAAL service on various ports"""
    print("[*] Looking for KAAL TCP service...")
    
    ports = [9000, 9001, 9002, 9003, 7777, 8888, 1337, 31337, 6667]
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((TARGET_IP, port))
            
            print(f"\n[+] Connected to port {port}")
            
            # Try to receive initial message
            try:
                sock.settimeout(1)
                data = sock.recv(4096)
                if data:
                    print(f"[+] Initial message: {data.decode('utf-8', errors='ignore')}")
            except socket.timeout:
                print("    No initial message")
            
            # Try sending KAAL
            messages = [
                b"KAAL\n",
                b"KAAL\r\n",
                b"kaal\n",
                b"SECTOR-7\n",
                b"9000\n",
                b"#06#\n",
                b"IMEI\n",
            ]
            
            for msg in messages:
                try:
                    sock.send(msg)
                    time.sleep(0.2)
                    sock.settimeout(1)
                    response = sock.recv(4096)
                    if response:
                        print(f"[+] Response to {msg.strip()}: {response.decode('utf-8', errors='ignore')}")
                        return port
                except socket.timeout:
                    pass
                except Exception as e:
                    pass
            
            sock.close()
        except:
            pass
    
    return None

def try_http_methods():
    """Try different HTTP methods and headers"""
    print("\n[*] Trying HTTP methods...")
    
    headers_list = [
        {'X-Knock': '9000,9001,9002'},
        {'X-KAAL': 'true'},
        {'X-IMEI': '123456789012345'},
        {'User-Agent': 'KAAL-Client/1.0'},
        {'Authorization': 'KAAL'},
    ]
    
    for headers in headers_list:
        try:
            r = requests.get(f"{WEB_URL}/challenge", headers=headers, timeout=3)
            if r.status_code != 403:
                print(f"[+] Headers {headers} -> Status: {r.status_code}")
                print(f"    Response: {r.text[:200]}")
        except:
            pass

def check_udp_services():
    """Check for UDP services"""
    print("\n[*] Checking UDP services...")
    
    ports = [9000, 9001, 9002, 53, 123]
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # Send KAAL message
            sock.sendto(b"KAAL", (TARGET_IP, port))
            
            try:
                data, addr = sock.recvfrom(4096)
                print(f"[+] UDP port {port} responded: {data.decode('utf-8', errors='ignore')}")
            except socket.timeout:
                pass
            
            sock.close()
        except:
            pass

def analyze_web_behavior():
    """Analyze web service behavior patterns"""
    print("\n[*] Analyzing web service behavior...")
    
    # Check if timing matters
    print("    Testing rapid requests...")
    for i in range(5):
        r = requests.get(f"{WEB_URL}/challenge", timeout=2)
        print(f"    Request {i+1}: {r.status_code}")
        time.sleep(0.1)
    
    # Check cookies/session
    print("\n    Testing with session...")
    session = requests.Session()
    r1 = session.get(WEB_URL)
    print(f"    Cookies after /: {session.cookies.get_dict()}")
    r2 = session.get(f"{WEB_URL}/challenge")
    print(f"    /challenge status: {r2.status_code}")

def main():
    print("[*] SECTOR-7 Deep Analysis")
    print(f"[*] Target: {TARGET_IP}\n")
    
    kaal_port = try_tcp_kaal_service()
    if kaal_port:
        print(f"\n[+] Found KAAL service on port {kaal_port}!")
    
    try_http_methods()
    check_udp_services()
    analyze_web_behavior()

if __name__ == "__main__":
    main()
