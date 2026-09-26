#!/usr/bin/env python3
from pwn import *

HOST = "212.2.248.184"
PORT = 31718

r = remote(HOST, PORT)

# Receive all initial data
print("[*] Receiving initial data...")
try:
    data = r.recv(timeout=2)
    print(f"Initial: {data}")
except:
    print("No initial data")

# Try simple commands
commands = [
    b"help",
    b"let x = 1",
    b"print x",
    b"let flag = 1",
    b"print flag",
]

for cmd in commands:
    print(f"\n[*] Sending: {cmd}")
    r.sendline(cmd)
    try:
        resp = r.recv(timeout=1)
        print(f"Response: {resp}")
    except:
        print("No response")

# Keep connection open for manual interaction
print("\n[*] Switching to interactive mode...")
r.interactive()
