#!/usr/bin/env python3
"""
Analyze the React app bundle to find API endpoints and vulnerabilities
"""

import requests
import re
import json

BASE_URL = "https://team-t1-wargames.vercel.app"

def download_and_analyze_js():
    """Download and analyze the main JS bundle"""
    print("[*] Downloading JavaScript bundle...")
    
    r = requests.get(f"{BASE_URL}/assets/index-DrEneAB6.js", timeout=10)
    js_content = r.text
    
    print(f"[*] JS bundle size: {len(js_content)} bytes")
    
    # Find API endpoints
    print("\n[*] Searching for API endpoints...")
    api_patterns = [
        r'["\']/(api/[^"\']+)["\']',
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.[a-z]+\(["\']([^"\']+)["\']',
        r'\.get\(["\']([^"\']+)["\']',
        r'\.post\(["\']([^"\']+)["\']',
    ]
    
    endpoints = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, js_content)
        endpoints.update(matches)
    
    print(f"[+] Found {len(endpoints)} potential endpoints:")
    for ep in sorted(endpoints):
        if 'api' in ep.lower() or ep.startswith('/'):
            print(f"  - {ep}")
    
    # Find authentication/token handling
    print("\n[*] Searching for authentication patterns...")
    auth_keywords = ['token', 'jwt', 'auth', 'bearer', 'session', 'cookie', 'localStorage', 'sessionStorage']
    for keyword in auth_keywords:
        if keyword in js_content.lower():
            # Find context around keyword
            idx = js_content.lower().find(keyword)
            if idx != -1:
                context = js_content[max(0, idx-100):min(len(js_content), idx+100)]
                print(f"[+] Found '{keyword}': ...{context}...")
                break
    
    # Find admin/role checks
    print("\n[*] Searching for role/admin checks...")
    role_patterns = [
        r'role["\']?\s*[=:]\s*["\']([^"\']+)["\']',
        r'isAdmin',
        r'admin["\']?\s*[=:]\s*(true|false)',
        r'userRole',
        r'permissions',
    ]
    
    for pattern in role_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            print(f"[+] Found role pattern '{pattern}': {matches[:5]}")
    
    # Save JS for manual analysis
    with open('team_t1_bundle.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("\n[*] Saved bundle to team_t1_bundle.js for manual analysis")
    
    return js_content

def test_actual_api():
    """Test actual API endpoints based on common patterns"""
    print("\n[*] Testing actual API endpoints...")
    
    session = requests.Session()
    
    # Try login with different methods
    login_endpoints = [
        "/api/auth/login",
        "/api/login",
        "/api/user/login",
        "/api/v1/auth/login",
    ]
    
    login_data = {
        "email": "ashishtest1@gmail.com",
        "password": "123456789"
    }
    
    for endpoint in login_endpoints:
        try:
            # Try POST with JSON
            r = session.post(f"{BASE_URL}{endpoint}", json=login_data, timeout=10)
            if r.status_code != 404:
                print(f"[+] {endpoint} (POST JSON): {r.status_code}")
                print(f"    Response: {r.text[:300]}")
                if r.status_code == 200:
                    return session, r.json() if r.headers.get('content-type', '').startswith('application/json') else None
        except Exception as e:
            pass
        
        try:
            # Try POST with form data
            r = session.post(f"{BASE_URL}{endpoint}", data=login_data, timeout=10)
            if r.status_code != 404:
                print(f"[+] {endpoint} (POST form): {r.status_code}")
                print(f"    Response: {r.text[:300]}")
                if r.status_code == 200:
                    return session, r.json() if r.headers.get('content-type', '').startswith('application/json') else None
        except Exception as e:
            pass
    
    return session, None

def main():
    print("=" * 60)
    print("Team T1 Wargames - Deep Analysis")
    print("=" * 60)
    
    js_content = download_and_analyze_js()
    session, auth_data = test_actual_api()
    
    if auth_data:
        print(f"\n[+] Authentication successful!")
        print(f"[*] Auth data: {json.dumps(auth_data, indent=2)}")

if __name__ == "__main__":
    main()
