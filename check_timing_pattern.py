#!/usr/bin/env python3
"""
Check if there's a timing pattern or if flag is in headers
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://138.199.163.92:12669"
SECRET = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

def check_headers_and_timing():
    """Check response headers for clues"""
    
    print("[*] Checking response headers...")
    time.sleep(3)
    
    url = f"{BASE_URL}/svg.php?secret={SECRET}"
    resp = requests.get(url, timeout=10)
    
    print(f"\n[*] Response Headers:")
    for header, value in resp.headers.items():
        print(f"  {header}: {value}")
    
    # Check for custom headers
    custom_headers = [h for h in resp.headers.keys() if h.startswith('X-') or 'Flag' in h or 'Kaal' in h]
    if custom_headers:
        print(f"\n[+] Custom headers found:")
        for h in custom_headers:
            print(f"  {h}: {resp.headers[h]}")
    
    # Check cookies
    if resp.cookies:
        print(f"\n[*] Cookies:")
        for cookie in resp.cookies:
            print(f"  {cookie.name}: {cookie.value}")
    
    # Maybe the flag is base64 encoded in a header
    import base64
    for header, value in resp.headers.items():
        try:
            decoded = base64.b64decode(value)
            if b'Kaal{' in decoded:
                print(f"\n[+] FLAG in base64-encoded header {header}!")
                print(decoded.decode())
        except:
            pass

def check_time_based_access():
    """Maybe need to access at specific second/minute"""
    
    print("\n[*] Checking if timing matters...")
    
    # Try accessing at different seconds
    current_time = datetime.now()
    print(f"[*] Current time: {current_time}")
    
    # Maybe need to access when second ends in 0 or 5
    target_seconds = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    
    print(f"[*] Waiting for next aligned second...")
    while True:
        now = datetime.now()
        if now.second in target_seconds:
            print(f"[*] Requesting at {now}")
            time.sleep(0.1)
            
            resp = requests.get(f"{BASE_URL}/svg.php?secret={SECRET}", timeout=10)
            print(f"    Response length: {len(resp.text)}")
            
            if "Kaal{" in resp.text:
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', resp.text)
                for flag in flags:
                    print(f"\n[+] FLAG FOUND: {flag}")
                    return flag
            
            break
        time.sleep(0.1)

def main():
    check_headers_and_timing()
    # check_time_based_access()

if __name__ == "__main__":
    main()
