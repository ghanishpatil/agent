#!/usr/bin/env python3
"""
Complete SECTOR-7 Solution
Based on previous attempts: knock [9000, 2600, 1337] then connect to port 9999
"""

import socket
import time

TARGET_IP = "13.206.58.35"
KNOCK_SEQUENCE = [9000, 2600, 1337]
SERVICE_PORT = 9999

def knock_ports():
    """Perform the port knocking sequence"""
    print(f"[*] Knocking sequence: {KNOCK_SEQUENCE}")
    for port in KNOCK_SEQUENCE:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((TARGET_IP, port))
            sock.close()
            print(f"    ✓ Knocked port {port}")
        except:
            print(f"    ✓ Knocked port {port} (no response expected)")
        time.sleep(0.3)
    
    print("[*] Waiting for service to open...")
    time.sleep(1)

def connect_to_service():
    """Connect to the KAAL service after knocking"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((TARGET_IP, SERVICE_PORT))
        print(f"[+] Connected to service on port {SERVICE_PORT}!")
        return sock
    except Exception as e:
        print(f"[-] Failed to connect: {e}")
        return None

def interact_with_service(sock):
    """Interact with the KAAL service"""
    try:
        # Receive initial banner/prompt
        sock.settimeout(2)
        banner = sock.recv(4096)
        if banner:
            print(f"\n[+] Service banner:")
            print(banner.decode('utf-8', errors='ignore'))
        
        # Try different interactions
        commands = [
            b"KAAL\n",
            b"help\n",
            b"flag\n",
            b"download\n",
            b"challenge\n",
            b"9000\n",
            b"2600\n",
            b"1337\n",
        ]
        
        for cmd in commands:
            print(f"\n[*] Sending: {cmd.strip()}")
            sock.send(cmd)
            time.sleep(0.5)
            
            try:
                response = sock.recv(4096)
                if response:
                    resp_text = response.decode('utf-8', errors='ignore')
                    print(f"[+] Response:")
                    print(resp_text)
                    
                    # Check for flag or download link
                    if "kaal{" in resp_text.lower() or "flag" in resp_text.lower():
                        print("\n[!!!] FOUND FLAG OR IMPORTANT INFO!")
                        return resp_text
            except socket.timeout:
                print("    (no response)")
        
        # Keep connection open for manual interaction
        print("\n[*] Entering interactive mode (type 'quit' to exit)...")
        sock.settimeout(None)
        
        while True:
            try:
                user_input = input("> ")
                if user_input.lower() == 'quit':
                    break
                
                sock.send((user_input + "\n").encode())
                response = sock.recv(4096)
                if response:
                    print(response.decode('utf-8', errors='ignore'))
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        
    except Exception as e:
        print(f"[-] Error during interaction: {e}")
    finally:
        sock.close()

def main():
    print("[*] SECTOR-7 Complete Solver")
    print(f"[*] Target: {TARGET_IP}\n")
    
    # Step 1: Port knocking
    knock_ports()
    
    # Step 2: Connect to service
    sock = connect_to_service()
    if not sock:
        print("\n[-] Could not connect to service after knocking")
        print("[*] The service might not be running or knock sequence is wrong")
        return
    
    # Step 3: Interact with service
    interact_with_service(sock)

if __name__ == "__main__":
    main()
