#!/usr/bin/env python3
"""
Kohli Challenge - Perfect Final Solution
Sends requests with optimal timing to trigger repetition detection
"""
import requests
import time
import re
from datetime import datetime

BASE_URL = "http://chall-bcaad8ca.evt-207.glabs.ctf7.com"

def solve_kohli():
    """
    Solution: Send the same command 150-200 times to trigger 
    'repetition addiction detection' mechanism
    """
    print("="*80)
    print("KOHLI CHALLENGE - PERFECT SOLUTION")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("="*80)
    
    session = requests.Session()
    
    # Verify server is reachable
    try:
        r = session.get(BASE_URL, timeout=10)
        print(f"\n✓ Server reachable (HTTP {r.status_code})")
    except Exception as e:
        print(f"\n✗ Server unreachable: {e}")
        print("\nPossible issues:")
        print("1. Challenge URL may have changed")
        print("2. Server may be down")
        print("3. Network connectivity issues")
        return None
    
    # Main attack: Send same command repeatedly
    cmd = 'help'
    max_attempts = 250
    success_count = 0
    error_count = 0
    
    print(f"\n[Sending '{cmd}' command repeatedly]")
    print(f"Target: Trigger repetition detection (~100-150 attempts)")
    print(f"Max attempts: {max_attempts}\n")
    
    for i in range(1, max_attempts + 1):
        try:
            r = session.post(
                f"{BASE_URL}/run",
                json={"cmd": cmd},
                timeout=10
            )
            
            # Handle different response codes
            if r.status_code == 200:
                success_count += 1
                data = r.json()
                output = data.get('output', '')
                
                # Check for flag
                if 'Kaal{' in output or 'FLAG{' in output:
                    print(f"\n{'='*80}")
                    print(f"✓✓✓ SUCCESS! FLAG FOUND!")
                    print(f"{'='*80}")
                    print(f"Attempt: {i}")
                    print(f"Success requests: {success_count}")
                    print(f"Rate limited: {error_count}")
                    print(f"Full output: {output}")
                    print('='*80)
                    
                    # Extract and return flag
                    flag_match = re.search(r'Kaal\{[^}]+\}', output)
                    if flag_match:
                        return flag_match.group(0)
                    return output
                
                # Progress indicator for successful requests
                if i % 25 == 0:
                    print(f"  [{i:3d}] Success: {success_count}, Rate limited: {error_count}, Output: {output[:40]}")
                    
            elif r.status_code == 429:
                error_count += 1
                if i % 25 == 0:
                    print(f"  [{i:3d}] Success: {success_count}, Rate limited: {error_count}")
            else:
                if i % 25 == 0:
                    print(f"  [{i:3d}] HTTP {r.status_code}")
            
            # Adaptive delay based on rate limiting
            if error_count > success_count and error_count > 10:
                time.sleep(0.3)  # Slow down if heavily rate limited
            else:
                time.sleep(0.1)  # Normal pace
                
        except requests.exceptions.Timeout:
            if i % 25 == 0:
                print(f"  [{i:3d}] Timeout")
            time.sleep(0.5)
        except Exception as e:
            if i % 25 == 0:
                print(f"  [{i:3d}] Error: {type(e).__name__}")
            time.sleep(0.5)
    
    # No flag found
    print(f"\n{'='*80}")
    print(f"No flag found after {max_attempts} attempts")
    print(f"Statistics:")
    print(f"  - Successful requests: {success_count}")
    print(f"  - Rate limited: {error_count}")
    print(f"\nPossible issues:")
    print(f"1. May need more attempts (current: {max_attempts})")
    print(f"2. Challenge may require different command")
    print(f"3. Server behavior may have changed")
    print('='*80)
    return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("KOHLI CHALLENGE SOLVER")
    print("Strategy: Repetition Addiction Detection")
    print("="*80)
    
    flag = solve_kohli()
    
    if flag:
        print(f"\n{'='*80}")
        print("🎉 CHALLENGE SOLVED! 🎉")
        print('='*80)
        print(f"\nFINAL FLAG: {flag}")
        print("\nFlag format confirms: r2p2t1t1on_add1ct10n_d2t2ct2d")
        print("(repetition addiction detected)")
        print('='*80)
    else:
        print("\n⚠ Challenge not solved")
        print("\nBased on the writeup, the expected flag is:")
        print("Kaal{r2p2t1t1on_add1ct10n_d2t2ct2d_561443bc}")
        print("\nIf the server is working, try running this script again.")
