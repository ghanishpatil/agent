#!/usr/bin/env python3
"""
Check the actual website for additional clues
"""

import requests
import re
import hashlib

url = "https://login-page-auqw.vercel.app/"
target_hash = "707b10ba2d8020957997e4127c99147091087a71"

print("="*70)
print("CHECKING WEBSITE FOR CLUES")
print("="*70)

try:
    # Get the page
    r = requests.get(url, timeout=10)
    print(f"\nStatus: {r.status_code}")
    print(f"Content-Length: {len(r.text)}")
    
    # Check for any differences from saved HTML
    with open('betrayal_page.html', 'r', encoding='utf-8') as f:
        saved_html = f.read()
    
    if r.text != saved_html:
        print("\n⚠️  Website content has changed!")
        print("\nDifferences:")
        
        # Find new content
        new_lines = set(r.text.split('\n')) - set(saved_html.split('\n'))
        if new_lines:
            print("\nNew lines:")
            for line in new_lines:
                if line.strip():
                    print(f"  + {line.strip()}")
    else:
        print("\n✓ Website content matches saved HTML")
    
    # Look for any hidden comments or data
    print("\n" + "="*70)
    print("SEARCHING FOR CLUES")
    print("="*70)
    
    # Check HTML comments
    comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
    if comments:
        print("\nHTML Comments:")
        for comment in comments:
            print(f"  {comment.strip()}")
    
    # Check for hidden divs or elements
    hidden_elements = re.findall(r'<[^>]*style=["\']display:\s*none["\'][^>]*>(.*?)</[^>]*>', r.text, re.DOTALL)
    if hidden_elements:
        print("\nHidden Elements:")
        for elem in hidden_elements:
            print(f"  {elem.strip()}")
    
    # Check for any data attributes
    data_attrs = re.findall(r'data-[a-z-]+=["\']([^"\']+)["\']', r.text)
    if data_attrs:
        print("\nData Attributes:")
        for attr in data_attrs:
            print(f"  {attr}")
    
    # Check for any base64 strings
    base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
    base64_strings = re.findall(base64_pattern, r.text)
    if base64_strings:
        print("\nBase64-like Strings:")
        for b64 in base64_strings[:10]:  # Limit to first 10
            print(f"  {b64}")
            
            # Try as password
            h = hashlib.sha1(b64.encode()).hexdigest()
            if h == target_hash:
                print(f"\n*** PASSWORD FOUND: {b64} ***")
    
    # Check for any JavaScript variables
    js_vars = re.findall(r'(?:var|let|const)\s+(\w+)\s*=\s*["\']([^"\']+)["\']', r.text)
    if js_vars:
        print("\nJavaScript Variables:")
        for var_name, var_value in js_vars:
            print(f"  {var_name} = {var_value}")
            
            # Try as password
            h = hashlib.sha1(var_value.encode()).hexdigest()
            if h == target_hash:
                print(f"\n*** PASSWORD FOUND: {var_value} ***")
    
    # Check response headers
    print("\n" + "="*70)
    print("RESPONSE HEADERS")
    print("="*70)
    for header, value in r.headers.items():
        print(f"  {header}: {value}")
        
        # Check if any header value is the password
        h = hashlib.sha1(value.encode()).hexdigest()
        if h == target_hash:
            print(f"\n*** PASSWORD FOUND IN HEADER: {value} ***")
    
    # Try to find any other endpoints
    print("\n" + "="*70)
    print("CHECKING OTHER ENDPOINTS")
    print("="*70)
    
    endpoints = [
        '/robots.txt',
        '/sitemap.xml',
        '/.well-known/security.txt',
        '/admin',
        '/api',
        '/flag',
        '/decrypt',
        '/token',
        '/login',
        '/dashboard',
        '/hint',
        '/password',
        '/secret',
    ]
    
    for endpoint in endpoints:
        try:
            r2 = requests.get(url.rstrip('/') + endpoint, timeout=5)
            if r2.status_code == 200:
                print(f"\n✓ {endpoint}: {r2.status_code} ({len(r2.text)} bytes)")
                
                # Check for flag
                if 'Kaal{' in r2.text:
                    print(f"  ⚠️  FLAG FOUND!")
                    flags = re.findall(r'Kaal\{[^}]+\}', r2.text)
                    for flag in flags:
                        print(f"  FLAG: {flag}")
                
                # Show first 200 chars
                if len(r2.text) < 500:
                    print(f"  Content: {r2.text[:200]}")
        except:
            pass
    
except Exception as e:
    print(f"\nError: {e}")

print("\nDone")
