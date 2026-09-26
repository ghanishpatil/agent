#!/usr/bin/env python3
"""
Interactive exploration of note-taking service
Use this to understand the service behavior before exploitation
"""

from pwn import *
import sys

def explore(host, port):
    """Connect and explore the service"""
    print(f"[*] Connecting to {host}:{port}...")
    io = remote(host, port)
    
    print("\n" + "="*60)
    print("INITIAL BANNER AND LEAKED ADDRESSES")
    print("="*60)
    
    # Receive and display initial output
    try:
        initial = io.recvuntil(b'>', timeout=5)
        print(initial.decode(errors='ignore'))
    except:
        print("[!] Timeout receiving initial banner")
        
    print("\n" + "="*60)
    print("EXPLORING SERVICE FUNCTIONALITY")
    print("="*60)
    
    # Test create
    print("\n[*] Testing CREATE function...")
    io.sendline(b'1')
    io.recvuntil(b':', timeout=2)
    io.sendline(b'64')  # Size
    io.recvuntil(b':', timeout=2)
    io.sendline(b'AAAA')  # Content
    response = io.recvuntil(b'>', timeout=2)
    print(response.decode(errors='ignore'))
    
    # Test show
    print("\n[*] Testing SHOW function...")
    io.sendline(b'4')
    io.recvuntil(b':', timeout=2)
    io.sendline(b'0')  # Index
    response = io.recvuntil(b'>', timeout=2)
    print(response.decode(errors='ignore'))
    
    # Test edit
    print("\n[*] Testing EDIT function...")
    io.sendline(b'2')
    io.recvuntil(b':', timeout=2)
    io.sendline(b'0')  # Index
    io.recvuntil(b':', timeout=2)
    io.sendline(b'BBBB')  # New content
    response = io.recvuntil(b'>', timeout=2)
    print(response.decode(errors='ignore'))
    
    # Verify edit
    print("\n[*] Verifying edit...")
    io.sendline(b'4')
    io.recvuntil(b':', timeout=2)
    io.sendline(b'0')
    response = io.recvuntil(b'>', timeout=2)
    print(response.decode(errors='ignore'))
    
    # Test off-by-one
    print("\n[*] Testing OFF-BY-ONE vulnerability...")
    io.sendline(b'2')
    io.recvuntil(b':', timeout=2)
    io.sendline(b'0')
    io.recvuntil(b':', timeout=2)
    # Send exactly size+1 bytes
    io.sendline(b'C' * 65)  # 64 + 1
    response = io.recvuntil(b'>', timeout=2)
    print(response.decode(errors='ignore'))
    
    # Create another note to see if we corrupted anything
    print("\n[*] Creating second note to check corruption...")
    io.sendline(b'1')
    io.recvuntil(b':', timeout=2)
    io.sendline(b'64')
    io.recvuntil(b':', timeout=2)
    io.sendline(b'DDDD')
    response = io.recvuntil(b'>', timeout=2)
    print(response.decode(errors='ignore'))
    
    # Show both notes
    print("\n[*] Showing all notes...")
    for i in range(2):
        io.sendline(b'4')
        io.recvuntil(b':', timeout=2)
        io.sendline(str(i).encode())
        response = io.recvuntil(b'>', timeout=2)
        print(f"Note {i}:")
        print(response.decode(errors='ignore'))
    
    print("\n" + "="*60)
    print("DROPPING TO INTERACTIVE MODE")
    print("="*60)
    print("Commands:")
    print("  1 - Create note")
    print("  2 - Edit note")
    print("  3 - Delete note")
    print("  4 - Show note")
    print("\nTry to trigger the vulnerability and get a shell!")
    
    io.interactive()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python explore_note_service.py <host> <port>")
        print("\nThis script helps you understand the service before exploitation")
        sys.exit(1)
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    explore(host, port)
