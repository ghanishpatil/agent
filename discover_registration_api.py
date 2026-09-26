#!/usr/bin/env python3
"""
Discover the actual registration API and requirements
"""

import requests
from bs4 import BeautifulSoup
import json
import re

TARGET = "https://cyberspacevr.in"

def analyze_register_page():
    """Analyze the registration page to find API endpoints"""
    print("[*] Analyzing registration page...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # Get the registration page
        resp = session.get(f"{TARGET}/register", timeout=10)
        print(f"[+] Status: {resp.status_code}")
        
        # Save for analysis
        with open('register_page_full.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        
        # Parse HTML
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script')
        print(f"\n[*] Found {len(scripts)} script tags")
        
        # Look for API endpoints in scripts
        api_endpoints = set()
        for i, script in enumerate(scripts):
            if script.string:
                # Look for fetch/axios calls
                fetch_calls = re.findall(r'fetch\(["\']([^"\']+)["\']', script.string)
                axios_calls = re.findall(r'axios\.(post|get)\(["\']([^"\']+)["\']', script.string)
                api_calls = re.findall(r'["\']/(api/[^"\']+)["\']', script.string)
                
                api_endpoints.update(fetch_calls)
                api_endpoints.update([call[1] for call in axios_calls])
                api_endpoints.update(api_calls)
        
        if api_endpoints:
            print("\n[+] Found API endpoints:")
            for endpoint in sorted(api_endpoints):
                print(f"    {endpoint}")
        
        # Look for forms
        forms = soup.find_all('form')
        print(f"\n[*] Found {len(forms)} forms")
        for form in forms:
            print(f"    Action: {form.get('action')}")
            print(f"    Method: {form.get('method')}")
            inputs = form.find_all('input')
            print(f"    Inputs: {[inp.get('name') or inp.get('type') for inp in inputs]}")
        
        # Check for Next.js data
        next_data = soup.find('script', {'id': '__NEXT_DATA__'})
        if next_data:
            print("\n[+] Found Next.js data")
            try:
                data = json.loads(next_data.string)
                print(json.dumps(data, indent=2)[:500])
            except:
                pass
        
        return resp.text
        
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

def test_api_endpoints():
    """Test various API endpoint patterns"""
    print("\n[*] Testing API endpoints...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    endpoints = [
        '/api/auth/register',
        '/api/register',
        '/api/users/register',
        '/api/signup',
        '/api/auth/signup',
        '/register',
        '/signup',
        '/api/v1/register',
        '/api/v1/auth/register',
    ]
    
    test_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password': 'TestPass123!'
    }
    
    for endpoint in endpoints:
        try:
            # Try JSON
            resp = session.post(f"{TARGET}{endpoint}", json=test_data, timeout=5)
            if resp.status_code != 404:
                print(f"  [+] {endpoint} -> {resp.status_code}")
                print(f"      Response: {resp.text[:200]}")
                
                if resp.status_code in [200, 201]:
                    print(f"      ✓ SUCCESS! This is the endpoint!")
                    return endpoint
            
            # Try form data
            resp = session.post(f"{TARGET}{endpoint}", data=test_data, timeout=5)
            if resp.status_code != 404 and resp.status_code != resp.status_code:
                print(f"  [+] {endpoint} (form) -> {resp.status_code}")
                print(f"      Response: {resp.text[:200]}")
                
        except Exception as e:
            pass
    
    return None

def check_nextjs_api():
    """Check Next.js API routes"""
    print("\n[*] Checking Next.js API structure...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Next.js typically uses /api/* routes
    # Check if there's a trpc or similar API
    test_routes = [
        '/api/trpc/auth.register',
        '/api/trpc/user.create',
        '/_next/data',
    ]
    
    for route in test_routes:
        try:
            resp = session.get(f"{TARGET}{route}", timeout=5)
            if resp.status_code != 404:
                print(f"  [+] {route} -> {resp.status_code}")
        except:
            pass

def intercept_browser_request():
    """Instructions for intercepting actual browser request"""
    print("\n" + "="*60)
    print("MANUAL TESTING REQUIRED")
    print("="*60)
    print("""
To find the exact API endpoint and payload format:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to: https://cyberspacevr.in/register
4. Fill out the registration form with test data
5. Click Register
6. Look for the POST request in Network tab
7. Check:
   - Request URL (the endpoint)
   - Request Headers (Content-Type, etc.)
   - Request Payload (JSON structure)
   - Response (success/error format)

Common patterns:
- Next.js: /api/auth/register or /api/register
- tRPC: /api/trpc/auth.register
- REST: /api/v1/users or /api/users

Once you have the exact endpoint and format, update the script.
    """)

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         REGISTRATION API DISCOVERY                        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Analyze the page
    analyze_register_page()
    
    # Step 2: Test common endpoints
    endpoint = test_api_endpoints()
    
    # Step 3: Check Next.js patterns
    check_nextjs_api()
    
    # Step 4: Manual instructions
    intercept_browser_request()
    
    if endpoint:
        print(f"\n[+] Found working endpoint: {endpoint}")
        print("[+] Update mass_register_5000_accounts.py with this endpoint")
    else:
        print("\n[-] Could not automatically find endpoint")
        print("[-] Manual browser inspection required")

if __name__ == "__main__":
    main()
