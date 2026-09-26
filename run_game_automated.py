#!/usr/bin/env python3
"""
Try to automate running the game and capturing flag
"""
import subprocess
import time

print("="*60)
print("RUNNING PATCHED GAME")
print("="*60)

# Try to run the patched game
try:
    # Run with timeout
    result = subprocess.run(
        ['game\\game_patched.exe'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    print("\n[STDOUT]")
    print(result.stdout)
    
    print("\n[STDERR]")
    print(result.stderr)
    
    print(f"\n[Return code: {result.returncode}]")
    
    # Look for flag in output
    output = result.stdout + result.stderr
    if 'Kaal{' in output:
        import re
        flag = re.search(r'Kaal\{[^}]+\}', output)
        if flag:
            print(f"\n[+] FLAG FOUND: {flag.group(0)}")
    
except subprocess.TimeoutExpired:
    print("\n[!] Game timed out (expected for GUI game)")
except Exception as e:
    print(f"\n[!] Error: {e}")

print("\n" + "="*60)
