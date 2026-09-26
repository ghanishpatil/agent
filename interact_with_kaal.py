#!/usr/bin/env python3
"""
Interact with KAAL on port 9999
"""

import socket
import time

target_ip = "13.206.58.35"
target_port = 9999

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

def interact():
    """Connect and interact with the service"""
    print("[*] Knocking first...")
    knock_first()
    time.sleep(1)
    
    print(f"[*] Connecting to {target_ip}:{target_port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((target_ip, target_port))
        
        # Receive initial banner
        print("\n[+] Receiving banner...")
        banner = sock.recv(4096)
        print(banner.decode('utf-8', errors='ignore'))
        
        # Try to interact
        print("\n[+] Sending test input...")
        sock.send(b"test\n")
        response = sock.recv(4096)
        print(response.decode('utf-8', errors='ignore'))
        
        # Try sending KAAL
        print("\n[+] Sending 'KAAL'...")
        sock.send(b"KAAL\n")
        response = sock.recv(4096)
        print(response.decode('utf-8', errors='ignore'))
        
        # Try to get more info
        print("\n[+] Sending various inputs to understand the protocol...")
        test_inputs = [b"help\n", b"?\n", b"info\n", b"menu\n", b"1\n", b"A"*100 + b"\n"]
        
        for inp in test_inputs:
            try:
                sock.send(inp)
                time.sleep(0.5)
                response = sock.recv(4096)
                if response:
                    print(f"\nInput: {inp[:50]}")
                    print(f"Response: {response.decode('utf-8', errors='ignore')[:300]}")
            except:
                pass
        
        sock.close()
        
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    interact()
