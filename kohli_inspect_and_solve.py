#!/usr/bin/env python3
"""
Inspect the Kohli server and find the right trigger
"""
import requests
import time
import re

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def inspect_server():
    """First, let's understand what the server actually does"""
    print("="*80)
    print("KOHLI SERVER INSPECTION")
    print("="*80)
    
    session = requests.Session()
    
    # Check main page
    print("\n[1] Fetching main page...")
    r = session.get(BASE_URL, timeout=10)
    print(f"Status: {r.status_code}")
    
    # Save HTML
    with open('kohli_current.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print("Saved to: kohli_current.html")
    
    # Check for app.js
    print("\n[2] Fetching app.js...")
    try:
        r = session.get(f"{BASE_URL}/app.js", timeout=10)
        if r.status_code == 200:
            with open('kohli_current_app.js', 'w', encoding='utf-8') as f:
                f.write(r.text)
            print(f"Saved to: kohli_current_app.js ({len(r.text)} bytes)")
            
            # Look for flag-related code
            if 'FLAG{' in r.text or 'Kaal{' in r.text:
                print("⚠ Found flag reference in JS!")
                matches = re.findall(r'(FLAG|Kaal)\{[^}]+\}', r.text)
                for m in matches:
                    print(f"  Found: {m}")
            
            # Look for detection logic
            if 'repetition' in r.text.lower() or 'detect' in r.text.lower():
                print("⚠ Found detection-related code")
                
        else:
            print(f"app.js not found (HTTP {r.status_code})")
    except Exception as e:
        print(f"Error fetching app.js: {e}")
    
    # Test basic command
    print("\n[3] Testing basic command...")
    r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    return session

def try_specific_patterns(session):
    """Try specific patterns that might trigger the flag"""
    print("\n" + "="*80)
    print("TRYING SPECIFIC PATTERNS")
    print("="*80)
    
    patterns = [
        # Maybe it needs a specific number of requests
        ("Exactly 100 requests", "help", 100),
        ("Exactly 150 requests", "help", 150),
        ("Exactly 200 requests", "help", 200),
    ]
    
    for name, cmd, count in patterns:
        print(f"\n[{name}]")
        print(f"Sending '{cmd}' exactly {count} times...")
        
        for i in range(1, count + 1):
            try:
                r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
                
                if r.status_code == 200:
                    data = r.json()
                    output = data.get('output', '')
                    
                    if 'Kaal{' in output or 'FLAG{' in output:
                        print(f"\n✓ FLAG FOUND at request #{i}!")
                        print(f"Output: {output}")
                        return output
                    
                    # Check if output changes at specific counts
                    if i in [50, 100, 150, 200] or output != '0x00':
                        print(f"  Request {i}: {output}")
                
                time.sleep(0.1)
                
            except Exception as e:
                if i % 50 == 0:
                    print(f"  Request {i}: Error - {e}")
        
        print(f"Completed {count} requests, no flag")
        time.sleep(2)
    
    return None

def try_encoded_commands(session):
    """Maybe the command needs to be encoded somehow"""
    print("\n" + "="*80)
    print("TRYING ENCODED/SPECIAL COMMANDS")
    print("="*80)
    
    special_cmds = [
        "cat flag.txt",
        "cat /flag",
        "cat /flag.txt",
        "/flag",
        "flag.txt",
        "getflag",
        "get_flag",
        "show_flag",
        "reveal",
        "secret",
        "admin",
        "root",
    ]
    
    for cmd in special_cmds:
        print(f"\nTrying: {cmd}")
        for i in range(1, 51):
            try:
                r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
                
                if r.status_code == 200:
                    data = r.json()
                    output = data.get('output', '')
                    
                    if output and output != '0x00' and '[ERR]' not in output:
                        print(f"  Attempt {i}: {output}")
                    
                    if 'Kaal{' in output or 'FLAG{' in output:
                        print(f"\n✓ FLAG FOUND with '{cmd}' at attempt {i}!")
                        print(f"Output: {output}")
                        return output
                
                time.sleep(0.15)
                
            except Exception as e:
                pass
    
    return None

def main():
    # Step 1: Inspect the server
    session = inspect_server()
    
    # Step 2: Try specific patterns
    result = try_specific_patterns(session)
    if result:
        flag = re.search(r'Kaal\{[^}]+\}', result)
        if flag:
            print(f"\n{'='*80}")
            print(f"FINAL FLAG: {flag.group(0)}")
            print('='*80)
            return flag.group(0)
    
    # Step 3: Try encoded commands
    result = try_encoded_commands(session)
    if result:
        flag = re.search(r'Kaal\{[^}]+\}', result)
        if flag:
            print(f"\n{'='*80}")
            print(f"FINAL FLAG: {flag.group(0)}")
            print('='*80)
            return flag.group(0)
    
    print("\n" + "="*80)
    print("No flag found. Check kohli_current.html and kohli_current_app.js")
    print("for clues about the detection mechanism.")
    print("="*80)

if __name__ == "__main__":
    main()
