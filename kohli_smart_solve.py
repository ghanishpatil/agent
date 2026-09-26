#!/usr/bin/env python3
"""
Smart Kohli solver - handles rate limiting and checks for patterns
"""
import requests
import time
import re

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def solve_with_patience():
    """Solve with proper rate limiting handling"""
    print("="*80)
    print("KOHLI SMART SOLVER - Ball by Ball")
    print("="*80)
    
    session = requests.Session()
    
    # First, let's check what the server returns normally
    print("\n[Initial test]")
    r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    # Strategy: Send requests slowly to avoid rate limiting
    # "Ball by ball" might mean we need to read one byte at a time
    print("\n[Trying byte-by-byte read approach]")
    
    flag_chars = []
    for i in range(100):
        try:
            # Try different read formats
            for cmd_format in [str(i), f"read {i}", f"{i}"]:
                r = session.post(f"{BASE_URL}/run", json={"cmd": cmd_format}, timeout=10)
                
                if r.status_code == 429:
                    print(f"  Rate limited at offset {i}, waiting...")
                    time.sleep(2)
                    continue
                
                data = r.json()
                output = data.get('output', '').strip()
                
                # Check if we got a hex byte
                if output and output != '0x00' and output.startswith('0x'):
                    byte_val = int(output, 16)
                    char = chr(byte_val)
                    flag_chars.append(char)
                    print(f"  [{i}] {cmd_format} => {output} = '{char}'")
                    
                    # Check if we have the flag
                    current = ''.join(flag_chars)
                    if 'Kaal{' in current:
                        # Continue until we get the closing brace
                        if '}' in current:
                            flag_match = re.search(r'Kaal\{[^}]+\}', current)
                            if flag_match:
                                print(f"\n{'='*80}")
                                print(f"✓ FOUND FLAG: {flag_match.group(0)}")
                                print('='*80)
                                return flag_match.group(0)
                    
                    break  # Found valid output, move to next offset
                
                time.sleep(0.3)  # Slow down to avoid rate limiting
                
        except Exception as e:
            print(f"  Error at offset {i}: {e}")
            time.sleep(1)
    
    if flag_chars:
        result = ''.join(flag_chars)
        print(f"\n[Collected characters]: {result}")
        flag_match = re.search(r'Kaal\{[^}]+\}', result)
        if flag_match:
            return flag_match.group(0)
    
    # Alternative: Maybe the flag appears after many identical requests
    print("\n[Trying repetition approach with delays]")
    for cmd in ['help', 'flag', 'check']:
        print(f"\nCommand: {cmd}")
        for i in range(1, 51):
            try:
                r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
                
                if r.status_code == 429:
                    print(f"  Rate limited at attempt {i}, waiting 3s...")
                    time.sleep(3)
                    continue
                
                data = r.json()
                output = data.get('output', '')
                
                if 'Kaal{' in output:
                    print(f"\n{'='*80}")
                    print(f"✓ FOUND FLAG after {i} attempts!")
                    print(f"Output: {output}")
                    print('='*80)
                    flag_match = re.search(r'Kaal\{[^}]+\}', output)
                    if flag_match:
                        return flag_match.group(0)
                
                if i % 10 == 0:
                    print(f"  Attempt {i}: {output[:50]}")
                
                time.sleep(0.5)  # Slower pace
                
            except Exception as e:
                print(f"  Error at attempt {i}: {e}")
                time.sleep(1)
    
    return None

if __name__ == "__main__":
    flag = solve_with_patience()
    if flag:
        print(f"\n{'='*80}")
        print(f"FINAL FLAG: {flag}")
        print('='*80)
    else:
        print("\nNo flag found. The challenge might require a different approach.")
