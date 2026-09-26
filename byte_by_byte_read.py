#!/usr/bin/env python3
"""
Read byte by byte like Kohli reads ball by ball
"""
import requests
import time
import re

BASE = "http://chall-35f0557e.evt-207.glabs.ctf7.com"

print("="*80)
print("BYTE BY BYTE READING (BALL BY BALL)")
print("="*80)

session = requests.Session()

# Try reading with different commands
commands_to_try = [
    lambda i: {"cmd": f"read {i}"},
    lambda i: {"cmd": f"read", "offset": i},
    lambda i: {"cmd": f"read", "pos": i},
    lambda i: {"cmd": f"read", "byte": i},
    lambda i: {"cmd": f"byte {i}"},
    lambda i: {"cmd": f"get {i}"},
    lambda i: {"cmd": f"fetch {i}"},
]

flag_chars = []

for cmd_func in commands_to_try:
    print(f"\n[Trying command pattern: {cmd_func(0)}]")
    
    for i in range(200):
        time.sleep(0.15)
        
        try:
            payload = cmd_func(i)
            r = session.post(f"{BASE}/run", json=payload, timeout=10)
            d = r.json()
            out = d.get("output", "").strip()
            
            # Check if we got a character/byte
            if out and out != "0x00" and not out.startswith("[ERR]"):
                print(f"  [{i}] {payload} => {out}")
                
                # Check if it's a hex byte
                if out.startswith("0x"):
                    try:
                        byte_val = int(out, 16)
                        char = chr(byte_val)
                        flag_chars.append(char)
                        print(f"    Decoded: '{char}' (byte {byte_val})")
                        
                        # Check if we're building a flag
                        current_flag = ''.join(flag_chars)
                        if 'Kaal{' in current_flag or 'FLAG{' in current_flag:
                            print(f"\n    Building flag: {current_flag}")
                        
                        if '}' in current_flag and ('Kaal{' in current_flag or 'FLAG{' in current_flag):
                            print(f"\n{'='*80}")
                            print(f"✓✓✓ COMPLETE FLAG FOUND!")
                            print(f"{'='*80}")
                            print(f"Flag: {current_flag}")
                            
                            flag_match = re.search(r'(Kaal|FLAG)\{[^}]+\}', current_flag)
                            if flag_match:
                                print(f"\nExtracted: {flag_match.group(0)}")
                            print('='*80)
                            exit(0)
                    except:
                        pass
                
                # Check if output contains flag directly
                if "Kaal{" in out or "FLAG{" in out:
                    print(f"\n{'='*80}")
                    print(f"✓✓✓ FOUND FLAG!")
                    print(f"{'='*80}")
                    print(f"Output: {out}")
                    
                    flag_match = re.search(r'(Kaal|FLAG)\{[^}]+\}', out)
                    if flag_match:
                        print(f"\nFLAG: {flag_match.group(0)}")
                    print('='*80)
                    exit(0)
            
            if i % 20 == 0 and i > 0:
                print(f"  [{i}] Checked {i} positions...")
                
        except Exception as e:
            if i % 20 == 0:
                print(f"  [{i}] Error: {e}")

print("\n" + "="*80)
print("No flag found with byte-by-byte reading")
print("="*80)
