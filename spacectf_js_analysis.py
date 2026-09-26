import requests
import re
import json
from bs4 import BeautifulSoup

WEB_BASE = "https://cyberspacevr.in"
API_BASE = "https://api.cyberspacevr.in"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
})

print("="*80)
print("SPACECTF - JAVASCRIPT & API ANALYSIS")
print("="*80)

# Check API base
print("\n[1] Checking API base URL...")
try:
    r = session.get(API_BASE, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Get all JavaScript files from main site
print("\n[2] Downloading and analyzing JavaScript files...")
try:
    r = session.get(WEB_BASE, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    scripts = soup.find_all('script', src=True)
    print(f"Found {len(scripts)} script tags")
    
    all_api_endpoints = set()
    all_api_calls = set()
    
    for i, script in enumerate(scripts, 1):
        src = script['src']
        if not src.startswith('http'):
            src = f"{WEB_BASE}{src}"
        
        print(f"\n[{i}/{len(scripts)}] Analyzing: {src}")
        
        try:
            js_r = session.get(src, timeout=10)
            if js_r.status_code == 200:
                js_content = js_r.text
                
                # Save large JS files for manual inspection
                if len(js_content) > 10000:
                    filename = f"spacectf_js_{i}.js"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(js_content)
                    print(f"    Saved to {filename} ({len(js_content)} bytes)")
                
                # Look for API endpoints
                patterns = [
                    r'["\']https?://api\.cyberspacevr\.in/([^"\']+)["\']',
                    r'["\']https?://cyberspacevr\.in/api/([^"\']+)["\']',
                    r'["\']/(api/[^"\']+)["\']',
                    r'["\']/(auth/[^"\']+)["\']',
                    r'fetch\(["\']([^"\']+)["\']',
                    r'axios\.[a-z]+\(["\']([^"\']+)["\']',
                    r'\.get\(["\']([^"\']+)["\']',
                    r'\.post\(["\']([^"\']+)["\']',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, js_content)
                    for match in matches:
                        if 'api' in match.lower() or 'auth' in match.lower():
                            all_api_endpoints.add(match)
                
                # Look for API base URLs
                api_bases = re.findall(r'["\']https?://[^"\']*api[^"\']*["\']', js_content)
                for base in api_bases:
                    print(f"    API Base: {base}")
                
                # Look for authentication patterns
                auth_patterns = re.findall(r'(login|register|signin|signup|auth)[^{]*\{[^}]{0,200}\}', js_content, re.IGNORECASE)
                if auth_patterns:
                    print(f"    Found {len(auth_patterns)} auth-related code blocks")
                
        except Exception as e:
            print(f"    Error: {e}")
    
    print(f"\n[+] Discovered API endpoints:")
    for ep in sorted(all_api_endpoints):
        print(f"    - {ep}")
    
    # Save endpoints
    with open("spacectf_api_endpoints.txt", "w") as f:
        for ep in sorted(all_api_endpoints):
            f.write(f"{ep}\n")
    
except Exception as e:
    print(f"Error: {e}")

# Check login and register pages
print("\n[3] Analyzing login/register pages...")
for page in ["/login", "/register"]:
    try:
        r = session.get(f"{WEB_BASE}{page}", timeout=10)
        if r.status_code == 200:
            print(f"\n{page}:")
            
            # Save page
            filename = f"spacectf_{page.strip('/')}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"    Saved to {filename}")
            
            # Look for API calls in page source
            api_refs = re.findall(r'["\']https?://[^"\']*api[^"\']*["\']', r.text)
            if api_refs:
                print(f"    API references:")
                for ref in set(api_refs):
                    print(f"      - {ref}")
            
            # Look for form actions
            soup = BeautifulSoup(r.text, 'html.parser')
            forms = soup.find_all('form')
            if forms:
                print(f"    Forms found: {len(forms)}")
                for form in forms:
                    action = form.get('action', 'N/A')
                    method = form.get('method', 'GET')
                    print(f"      - {method} {action}")
    except Exception as e:
        print(f"    Error: {e}")

# Try to access Next.js API routes
print("\n[4] Testing Next.js API routes...")
nextjs_routes = [
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/[...nextauth]",
    "/api/user",
    "/api/users",
    "/api/admin",
]

for route in nextjs_routes:
    try:
        r = session.get(f"{WEB_BASE}{route}", timeout=5)
        if r.status_code != 404:
            print(f"[+] {route}: {r.status_code}")
            if r.status_code == 200:
                print(f"    Response: {r.text[:200]}")
    except:
        pass

print("\n[+] Analysis complete!")
