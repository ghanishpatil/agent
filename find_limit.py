#!/usr/bin/env python3
from pwn import *

host = '212.2.250.33'
port = 30968

# Test different payload lengths
for length in [50, 60, 70, 80, 90, 100, 110, 120]:
    io = remote(host, port, level='error')
    io.recvuntil(b'>', timeout=2)
    
    # Create a payload of specific length
    payload = b"1" + b"+"*length + b"1"
    
    io.sendline(payload)
    time.sleep(0.3)
    response = io.recvall(timeout=1).decode()
    
    if "too long" in response:
        print(f"[*] Length {len(payload)}: TOO LONG")
        break
    else:
        print(f"[*] Length {len(payload)}: OK - {response[:50]}")
    
    io.close()
