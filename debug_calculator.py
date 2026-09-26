#!/usr/bin/env python3
from pwn import *

host = '212.2.250.33'
port = 30968

io = remote(host, port)

# Get initial prompt
initial = io.recvuntil(b'>', timeout=2)
print("Initial:", initial.decode())

# Test 1: Simple math
print("\n[Test 1] Simple math: 2+2")
io.sendline(b'2+2')
time.sleep(0.5)
response = io.recvall(timeout=2).decode()
print("Response:", repr(response))

io.close()

# New connection for test 2
io = remote(host, port)
io.recvuntil(b'>', timeout=2)

print("\n[Test 2] String operation: 'hello'")
io.sendline(b"'hello'")
time.sleep(0.5)
response = io.recvall(timeout=2).decode()
print("Response:", repr(response))

io.close()

# New connection for test 3
io = remote(host, port)
io.recvuntil(b'>', timeout=2)

print("\n[Test 3] List dir: dir()")
io.sendline(b"dir()")
time.sleep(0.5)
response = io.recvall(timeout=2).decode()
print("Response:", repr(response))

io.close()

# New connection for test 4
io = remote(host, port)
io.recvuntil(b'>', timeout=2)

print("\n[Test 4] Globals: globals()")
io.sendline(b"globals()")
time.sleep(0.5)
response = io.recvall(timeout=2).decode()
print("Response:", repr(response))

io.close()
