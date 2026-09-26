#!/usr/bin/env python3
"""
Try POST request or other HTTP methods
"""

import requests
import time

BASE_URL = "http://138.199.163.92:12669"
SECRET = "Th1s_is_4_Str0ng_M4ster_Secret_Key_2026!!"

def try_different_methods():
    """Try different HTTP methods and parameters"""
    
    time.sleep(3)
    
    # Try POST with secret
    print("[*] Trying POST to /svg.php...")
    try:
        resp = requests.post(f"{BASE_URL}/svg.php", data={'secret': SECRET}, timeout=10)
        print(f"    Status: {resp.status_code}, Length: {len(resp.text)}")
        if "Kaal{" in resp.text:
            print(f"[+] FLAG in POST response!")
            print(resp.text)
    except Exception as e:
        print(f"    Error: {e}")
    
    time.sleep(3)
    
    # Try GET with different parameter names
    print("\n[*] Trying /flag endpoint with secret...")
    try:
        resp = requests.get(f"{BASE_URL}/flag?secret={SECRET}", timeout=10)
        print(f"    Status: {resp.status_code}")
        if resp.status_code == 200:
            print(resp.text)
    except:
        pass
    
    time.sleep(3)
    
    # Try /lore with secret
    print("\n[*] Trying /lore with secret parameter...")
    try:
        resp = requests.get(f"{BASE_URL}/lore?secret={SECRET}", timeout=10)
        print(f"    Status: {resp.status_code}, Length: {len(resp.text)}")
        if "Kaal{" in resp.text:
            print(f"[+] FLAG found!")
            print(resp.text)
    except Exception as e:
        print(f"    Error: {e}")
    
    time.sleep(3)
    
    # Check if there's a /submit or /verify endpoint
    print("\n[*] Trying /submit endpoint...")
    try:
        resp = requests.post(f"{BASE_URL}/submit", data={'secret': SECRET}, timeout=10)
        print(f"    Status: {resp.status_code}")
        if resp.status_code == 200:
            print(resp.text[:500])
    except:
        pass

if __name__ == "__main__":
    try_different_methods()
