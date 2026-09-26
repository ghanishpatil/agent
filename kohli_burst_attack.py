#!/usr/bin/env python3
"""
Kohli Challenge - Burst Attack
Send many requests quickly to trigger detection before rate limiting kicks in
"""
import requests
import concurrent.futures
import time

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def send_request(session, cmd, attempt_num):
    """Send a single request"""
    try:
        r = session.post(
            f"{BASE_URL}/run",
            json={"cmd": cmd},
            timeout=5
        )
        data = r.json()
        output = data.get('output', '')
        
        if 'Kaal{' in output or 'FLAG{' in output:
            return (attempt_num, output, True)
        return (attempt_num, output, False)
    except Exception as e:
        return (attempt_num, str(e), False)

def burst_attack():
    print("="*80)
    print("KOHLI BURST ATTACK")
    print("Sending rapid requests to trigger detection")
    print("="*80)
    
    session = requests.Session()
    cmd = 'help'
    
    # Strategy 1: Send many requests very quickly
    print("\n[Strategy 1: Rapid burst - 50 requests with minimal delay]")
    for i in range(1, 51):
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=5)
            data = r.json()
            output = data.get('output', '')
            
            if 'Kaal{' in output or 'FLAG{' in output:
                print(f"\n✓ FLAG FOUND at attempt {i}!")
                print(f"Output: {output}")
                return output
            
            if i % 10 == 0:
                print(f"  Attempt {i}: {output[:30]}")
            
            time.sleep(0.05)  # Very short delay
        except Exception as e:
            if i % 10 == 0:
                print(f"  Attempt {i}: Error - {e}")
    
    # Strategy 2: Try different commands
    print("\n[Strategy 2: Different commands with repetition]")
    for cmd in ['flag', 'check', 'status', 'pitch', 'ball', 'read']:
        print(f"\nTrying '{cmd}'...")
        for i in range(1, 31):
            try:
                r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=5)
                data = r.json()
                output = data.get('output', '')
                
                if 'Kaal{' in output or 'FLAG{' in output:
                    print(f"\n✓ FLAG FOUND with '{cmd}' at attempt {i}!")
                    print(f"Output: {output}")
                    return output
                
                time.sleep(0.1)
            except Exception as e:
                pass
    
    # Strategy 3: Parallel requests
    print("\n[Strategy 3: Parallel requests]")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(1, 101):
            future = executor.submit(send_request, session, 'help', i)
            futures.append(future)
            time.sleep(0.02)
        
        for future in concurrent.futures.as_completed(futures):
            attempt_num, output, found_flag = future.result()
            if found_flag:
                print(f"\n✓ FLAG FOUND at attempt {attempt_num}!")
                print(f"Output: {output}")
                return output
            if attempt_num % 20 == 0:
                print(f"  Attempt {attempt_num}: {output[:30]}")
    
    print("\nNo flag found with any strategy")
    return None

if __name__ == "__main__":
    result = burst_attack()
    if result:
        print(f"\n{'='*80}")
        print(f"FINAL FLAG: {result}")
        print('='*80)
