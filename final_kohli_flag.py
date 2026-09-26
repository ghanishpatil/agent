#!/usr/bin/env python3
"""
Final Kohli Challenge Solution
Strategy: Send same command repeatedly to trigger "repetition addiction detection"
The flag appears after ~100-150 repetitions
"""
import requests
import time
import re

# Current challenge URL
BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def get_flag():
    print("="*80)
    print("KOHLI CHALLENGE - FINAL SOLUTION")
    print("Strategy: Trigger repetition detection by sending same command repeatedly")
    print("="*80)
    
    session = requests.Session()
    
    # Test connectivity
    print("\n[Testing connectivity]")
    try:
        r = session.get(BASE_URL, timeout=10)
        print(f"✓ Server reachable (HTTP {r.status_code})")
    except Exception as e:
        print(f"✗ Cannot reach server: {e}")
        return None
    
    # Send the same command repeatedly to trigger detection
    cmd = 'help'
    max_attempts = 200
    
    print(f"\n[Sending '{cmd}' command repeatedly to trigger detection]")
    print(f"Target: ~100-150 attempts to trigger 'repetition addiction detection'")
    print()
    
    for i in range(1, max_attempts + 1):
        try:
            r = session.post(
                f"{BASE_URL}/run",
                json={"cmd": cmd},
                timeout=10
            )
            
            if r.status_code != 200:
                if i % 20 == 0:
                    print(f"  Attempt {i}: HTTP {r.status_code}")
                time.sleep(0.2)
                continue
            
            data = r.json()
            output = data.get('output', '')
            
            # Check for flag
            if 'Kaal{' in output or 'FLAG{' in output:
                print(f"\n{'='*80}")
                print(f"✓✓✓ SUCCESS! Flag found after {i} attempts!")
                print(f"{'='*80}")
                print(f"Full response: {output}")
                print('='*80)
                
                # Extract flag
                flag_match = re.search(r'(Kaal|FLAG)\{[^}]+\}', output)
                if flag_match:
                    flag = flag_match.group(0)
                    print(f"\nFINAL FLAG: {flag}")
                    print('='*80)
                    return flag
                return output
            
            # Print progress every 10 attempts
            if i % 10 == 0:
                status = output[:50] if output else 'empty'
                print(f"  Attempt {i}: {status}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
            
        except requests.exceptions.Timeout:
            if i % 20 == 0:
                print(f"  Attempt {i}: Timeout")
            time.sleep(0.5)
        except Exception as e:
            if i % 20 == 0:
                print(f"  Attempt {i}: {type(e).__name__}: {e}")
            time.sleep(0.5)
    
    print(f"\n{'='*80}")
    print(f"No flag found after {max_attempts} attempts")
    print("Possible issues:")
    print("1. Challenge URL might have changed")
    print("2. May need more attempts (increase max_attempts)")
    print("3. Server might be down or rate limiting aggressively")
    print('='*80)
    return None

if __name__ == "__main__":
    flag = get_flag()
    
    if flag:
        print(f"\n{'='*80}")
        print("CHALLENGE SOLVED!")
        print(f"FLAG: {flag}")
        print('='*80)
    else:
        print("\nChallenge not solved. Check the URL and try again.")
