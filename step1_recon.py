#!/usr/bin/env python3
"""Step 1: Understand the service behavior"""
from pwn import *
import time

io = remote('212.2.250.33', 32384)

print("="*60)
print("STEP 1: RECONNAISSANCE")
print("="*60)

# Get banner and leaked addresses
banner = io.recvuntil(b'>')
print("\n[BANNER]")
print(banner.decode())

import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

print(f"\n[LEAKED ADDRESSES]")
print(f"heap:  0x{heap:016x}")
print(f"win(): 0x{win:016x}")
print(f"hook:  0x{hook:016x}")

# Test 1: Create a note and see the output
print("\n[TEST 1: Create note]")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'24')
io.recvuntil(b':')
io.sendline(b'AAAA')
response = io.recvuntil(b'>')
print(response.decode())

# Test 2: Print the note
print("\n[TEST 2: Print note]")
io.sendline(b'4')
io.recvuntil(b':')
io.sendline(b'0')
response = io.recvuntil(b'>')
print(response.decode())

# Test 3: Edit the note (this is where off-by-one happens)
print("\n[TEST 3: Edit note - append content]")
io.sendline(b'2')
io.recvuntil(b':')
io.sendline(b'0')
io.recvuntil(b':')
io.sendline(b'BBBB')
response = io.recvuntil(b'>')
print(response.decode())

# Test 4: Print again to see the edit
print("\n[TEST 4: Print after edit]")
io.sendline(b'4')
io.recvuntil(b':')
io.sendline(b'0')
response = io.recvuntil(b'>')
print(response.decode())

# Test 5: Delete
print("\n[TEST 5: Delete note]")
io.sendline(b'3')
io.recvuntil(b':')
io.sendline(b'0')
response = io.recvuntil(b'>')
print(response.decode())

io.close()

print("\n" + "="*60)
print("RECONNAISSANCE COMPLETE")
print("="*60)
