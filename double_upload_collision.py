#!/usr/bin/env python3
"""
Upload BOTH collision files in the same session quickly
"""

import requests
import hashlib
import re

TARGET_URL = "http://138.199.163.92:12871/"

def create_collision_files():
    """Create the collision files"""
    block_a = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    )
    
    block_b = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    )
    
    with open('coll_a.bin', 'wb') as f:
        f.write(block_a)
    
    with open('coll_b.bin', 'wb') as f:
        f.write(block_b)
    
    return 'coll_a.bin', 'coll_b.bin'

def upload_both_quickly():
    """Upload both files in quick succession"""
    print("="*60)
    print("Double Upload Attack")
    print("="*60)
    
    file_a, file_b = create_collision_files()
    
    session = requests.Session()
    
    # Upload A
    print("\n[*] Uploading file A...")
    with open(file_a, 'rb') as f:
        resp_a = session.post(TARGET_URL + 'collision', files={'image': f})
    print(f"[+] Response A: {resp_a.text}")
    
    # Immediately upload B in same session
    print("\n[*] Uploading file B (same session)...")
    with open(file_b, 'rb') as f:
        resp_b = session.post(TARGET_URL + 'collision', files={'image': f})
    print(f"[+] Response B: {resp_b.text}")
    
    # Check for flag
    for resp in [resp_a, resp_b]:
        if 'kaal{' in resp.text.lower():
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                print(f"\n[!!!] FLAG: {flag.group(0)}")
                return flag.group(0)
    
    # Maybe we need to check a different endpoint after uploading?
    print("\n[*] Checking /flag endpoint...")
    resp_flag = session.get(TARGET_URL + 'flag')
    print(f"[+] /flag: {resp_flag.status_code} - {resp_flag.text[:200]}")
    
    if 'kaal{' in resp_flag.text.lower():
        flag = re.search(r'Kaal\{[^}]+\}', resp_flag.text, re.IGNORECASE)
        if flag:
            print(f"\n[!!!] FLAG: {flag.group(0)}")
            return flag.group(0)
    
    # Check /collision endpoint with GET
    print("\n[*] Checking /collision with GET...")
    resp_coll = session.get(TARGET_URL + 'collision')
    print(f"[+] /collision GET: {resp_coll.status_code} - {resp_coll.text[:200]}")
    
    if 'kaal{' in resp_coll.text.lower():
        flag = re.search(r'Kaal\{[^}]+\}', resp_coll.text, re.IGNORECASE)
        if flag:
            print(f"\n[!!!] FLAG: {flag.group(0)}")
            return flag.group(0)
    
    return None

def main():
    flag = upload_both_quickly()
    
    if flag:
        print(f"\n{'='*60}")
        print(f"SUCCESS! FLAG: {flag}")
        print(f"{'='*60}")
    else:
        print("\n[*] No flag found yet")
        print("[*] The server detected the collision but didn't give the flag")
        print("[*] Maybe the flag is in the bonus grid image")

if __name__ == "__main__":
    main()
