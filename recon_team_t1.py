#!/usr/bin/env python3
"""
Team T1 Wargames - Initial Reconnaissance
Target: https://team-t1-wargames.vercel.app/
Credentials: ashishtest1@gmail.com / 123456789
"""

import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "https://team-t1-wargames.vercel.app"
EMAIL = "ashishtest1@gmail.com"
PASSWORD = "123456789"

def initial_recon():
    """Gather initial information about the site"""
    print("[*] Starting reconnaissance...")
    
    # Check robots.txt
    try:
        r = requests.get(f"{BASE_URL}/robots.txt", timeout=10)
        if r.status_code == 200:
            print(f"\n[+] robots.txt found:\n{r.text}")
    except:
        print("[-] No robots.txt")
    
    # Check sitemap
    try:
        r = requests.get(f"{BASE_URL}/sitemap.xml", timeout=10)
        if r.status_code == 200:
            print(f"\n[+] sitemap.xml found")
    except:
        print("[-] No sitemap.xml")
    
    # Get main page
    r = requests.get(BASE_URL, timeout=10)
    print(f"\n[*] Main page status: {r.status_code}")
    print(f"[*] Headers: {dict(r.headers)}")
    
    # Parse HTML
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find all links
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    print(f"\n[*] Found links: {links}")
    
    # Find all forms
    forms = soup.find_all('form')
    print(f"\n[*] Found {len(forms)} forms")
    for i, form in enumerate(forms):
        print(f"  Form {i}: action={form.get('action')}, method={form.get('method')}")
    
    # Find scripts
    scripts = [s.get('src') for s in soup.find_all('script', src=True)]
    print(f"\n[*] External scripts: {scripts}")

def login_and_explore():
    """Login and explore authenticated areas"""
    print("\n[*] Attempting login...")
    
    session = requests.Session()
    
    # Get login page first
    r = session.get(f"{BASE_URL}/login", timeout=10)
    print(f"[*] Login page status: {r.status_code}")
    
    # Try to login
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    r = session.post(f"{BASE_URL}/api/login", json=login_data, timeout=10)
    print(f"[*] Login response status: {r.status_code}")
    print(f"[*] Login response: {r.text[:500]}")
    
    if r.status_code == 200:
        print("[+] Login successful!")
        
        # Check cookies
        print(f"[*] Cookies: {session.cookies.get_dict()}")
        
        # Try to access dashboard/profile
        endpoints = [
            "/dashboard",
            "/profile",
            "/admin",
            "/api/user",
            "/api/users",
            "/api/profile",
            "/settings",
            "/account"
        ]
        
        for endpoint in endpoints:
            try:
                r = session.get(f"{BASE_URL}{endpoint}", timeout=10)
                print(f"[*] {endpoint}: {r.status_code}")
                if r.status_code == 200:
                    print(f"    Content preview: {r.text[:200]}")
            except Exception as e:
                print(f"[-] {endpoint}: Error - {e}")
    
    return session

def check_api_endpoints(session):
    """Check for API endpoints"""
    print("\n[*] Checking API endpoints...")
    
    api_endpoints = [
        "/api/admin",
        "/api/admin/users",
        "/api/admin/dashboard",
        "/api/users",
        "/api/user/profile",
        "/api/auth/verify",
        "/api/config",
        "/api/settings",
        "/api/debug",
        "/api/v1/admin",
        "/api/v2/admin",
    ]
    
    for endpoint in api_endpoints:
        try:
            r = session.get(f"{BASE_URL}{endpoint}", timeout=10)
            if r.status_code != 404:
                print(f"[+] {endpoint}: {r.status_code}")
                print(f"    Response: {r.text[:300]}")
        except Exception as e:
            pass

def check_jwt_token(session):
    """Check if JWT tokens are used and analyze them"""
    print("\n[*] Checking for JWT tokens...")
    
    cookies = session.cookies.get_dict()
    headers = {}
    
    # Check cookies for JWT
    for name, value in cookies.items():
        if len(value) > 50 and '.' in value:
            print(f"[+] Potential JWT in cookie '{name}': {value[:50]}...")
            # Try to decode (JWT is base64)
            try:
                import base64
                parts = value.split('.')
                if len(parts) == 3:
                    header = base64.urlsafe_b64decode(parts[0] + '==')
                    payload = base64.urlsafe_b64decode(parts[1] + '==')
                    print(f"    Header: {header}")
                    print(f"    Payload: {payload}")
            except:
                pass
    
    # Check localStorage/sessionStorage (need to check in browser)
    print("[*] Check browser DevTools for tokens in localStorage/sessionStorage")

def main():
    print("=" * 60)
    print("Team T1 Wargames - Security Assessment")
    print("=" * 60)
    
    initial_recon()
    session = login_and_explore()
    check_api_endpoints(session)
    check_jwt_token(session)
    
    print("\n[*] Initial reconnaissance complete!")
    print("[*] Next steps:")
    print("  1. Check for IDOR vulnerabilities")
    print("  2. Test for SQL injection")
    print("  3. Test for XSS")
    print("  4. Check JWT token manipulation")
    print("  5. Test for privilege escalation")
    print("  6. Check for CSRF")

if __name__ == "__main__":
    main()
