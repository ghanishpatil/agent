import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://cyberspacevr.in"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
})

print("="*80)
print("SPACECTF - DEEP RECONNAISSANCE")
print("="*80)

# Get homepage and analyze
print("\n[1] Analyzing homepage...")
try:
    r = session.get(BASE_URL, timeout=10)
    print(f"Status: {r.status_code}")
    
    # Save HTML
    with open("spacectf_home.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find all forms
    forms = soup.find_all('form')
    print(f"\n[+] Found {len(forms)} forms")
    for i, form in enumerate(forms, 1):
        action = form.get('action', 'N/A')
        method = form.get('method', 'GET')
        print(f"  Form {i}: {method} {action}")
        inputs = form.find_all('input')
        for inp in inputs:
            print(f"    - {inp.get('name', 'unnamed')}: {inp.get('type', 'text')}")
    
    # Find all links
    links = soup.find_all('a', href=True)
    unique_links = set()
    for link in links:
        href = link['href']
        if href.startswith('/') or 'cyberspacevr' in href:
            unique_links.add(href)
    
    print(f"\n[+] Found {len(unique_links)} unique internal links:")
    for link in sorted(unique_links):
        print(f"  - {link}")
    
    # Find all scripts
    scripts = soup.find_all('script', src=True)
    print(f"\n[+] Found {len(scripts)} external scripts:")
    for script in scripts:
        src = script['src']
        print(f"  - {src}")
        
        # Download and analyze JS files
        if src.startswith('/'):
            try:
                js_r = session.get(f"{BASE_URL}{src}", timeout=5)
                if js_r.status_code == 200:
                    # Look for API endpoints
                    api_patterns = re.findall(r'["\']/(api/[^"\']+)["\']', js_r.text)
                    api_patterns += re.findall(r'["\']/(auth/[^"\']+)["\']', js_r.text)
                    api_patterns += re.findall(r'["\']/(admin/[^"\']+)["\']', js_r.text)
                    
                    if api_patterns:
                        print(f"    API endpoints found in {src}:")
                        for ep in set(api_patterns):
                            print(f"      - {ep}")
            except:
                pass
    
    # Look for API endpoints in HTML
    print("\n[2] Searching for API endpoints in HTML...")
    api_refs = re.findall(r'["\']/(api/[^"\']+)["\']', r.text)
    api_refs += re.findall(r'["\']/(auth/[^"\']+)["\']', r.text)
    api_refs += re.findall(r'fetch\(["\']([^"\']+)["\']', r.text)
    
    if api_refs:
        print(f"[+] Found {len(set(api_refs))} API references:")
        for ref in sorted(set(api_refs)):
            print(f"  - {ref}")
    
except Exception as e:
    print(f"Error: {e}")

# Try common authentication endpoints
print("\n[3] Testing authentication endpoints...")
auth_endpoints = [
    "/login",
    "/signin",
    "/auth/login",
    "/auth/signin",
    "/api/login",
    "/api/auth/login",
    "/api/signin",
    "/user/login",
    "/users/login",
]

for ep in auth_endpoints:
    try:
        r = session.get(f"{BASE_URL}{ep}", timeout=5)
        if r.status_code in [200, 405]:  # 405 means endpoint exists but wrong method
            print(f"[+] {ep}: {r.status_code}")
            if r.status_code == 200:
                print(f"    Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    except:
        pass

# Try to find registration page
print("\n[4] Looking for registration...")
reg_endpoints = [
    "/register",
    "/signup",
    "/auth/register",
    "/auth/signup",
    "/api/register",
    "/api/auth/register",
]

for ep in reg_endpoints:
    try:
        r = session.get(f"{BASE_URL}{ep}", timeout=5)
        if r.status_code in [200, 405]:
            print(f"[+] {ep}: {r.status_code}")
    except:
        pass

# Check robots.txt and sitemap
print("\n[5] Checking robots.txt and sitemap...")
for file in ["/robots.txt", "/sitemap.xml", "/.well-known/security.txt"]:
    try:
        r = session.get(f"{BASE_URL}{file}", timeout=5)
        if r.status_code == 200:
            print(f"[+] {file} exists:")
            print(r.text[:500])
    except:
        pass

print("\n[+] Reconnaissance complete!")
