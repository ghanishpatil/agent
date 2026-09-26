#!/usr/bin/env python3
"""
Deep analysis of discovered endpoints
"""

import requests
import json

base_url = "http://fresh-start-267.emergent.host"

print("="*60)
print("DEEP ANALYSIS OF CRITICAL ENDPOINTS")
print("="*60)

# Check .env file
print("\n[1] Checking .env file...")
try:
    resp = requests.get(f"{base_url}/.env", timeout=5)
    if resp.status_code == 200:
        print(f"[!] .env file is accessible!")
        print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")

# Check .git/HEAD
print("\n[2] Checking .git/HEAD...")
try:
    resp = requests.get(f"{base_url}/.git/HEAD", timeout=5)
    if resp.status_code == 200:
        print(f"[!] .git directory is exposed!")
        print(resp.text[:200])
except Exception as e:
    print(f"Error: {e}")

# Check phpinfo
print("\n[3] Checking phpinfo.php...")
try:
    resp = requests.get(f"{base_url}/phpinfo.php", timeout=5)
    if resp.status_code == 200 and 'PHP Version' in resp.text:
        print(f"[!] phpinfo.php is accessible!")
        print("Contains sensitive PHP configuration")
except Exception as e:
    print(f"Error: {e}")

# Check GraphQL
print("\n[4] Checking GraphQL endpoint...")
try:
    # Try introspection query
    query = {"query": "{__schema{types{name}}}"}
    resp = requests.post(f"{base_url}/graphql", json=query, timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Response preview:")
        print(json.dumps(resp.json(), indent=2)[:500])
except Exception as e:
    print(f"Error: {e}")

# Check Swagger/API docs
print("\n[5] Checking Swagger/API documentation...")
try:
    resp = requests.get(f"{base_url}/swagger", timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Swagger UI accessible - API documentation exposed")
except Exception as e:
    print(f"Error: {e}")

# Check admin panel
print("\n[6] Checking /admin endpoint...")
try:
    resp = requests.get(f"{base_url}/admin", timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Content length: {len(resp.text)}")
    if 'login' in resp.text.lower() or 'admin' in resp.text.lower():
        print("[!] Admin panel found")
except Exception as e:
    print(f"Error: {e}")

# Check database endpoints
print("\n[7] Checking /database endpoint...")
try:
    resp = requests.get(f"{base_url}/database", timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Response preview:")
        print(resp.text[:300])
except Exception as e:
    print(f"Error: {e}")

# Check backup
print("\n[8] Checking /backup endpoint...")
try:
    resp = requests.get(f"{base_url}/backup", timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Response preview:")
        print(resp.text[:300])
except Exception as e:
    print(f"Error: {e}")

# Check config
print("\n[9] Checking /config endpoint...")
try:
    resp = requests.get(f"{base_url}/config", timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Response preview:")
        print(resp.text[:300])
except Exception as e:
    print(f"Error: {e}")

# Try to access the main app
print("\n[10] Analyzing main application...")
try:
    resp = requests.get(base_url, timeout=5)
    print(f"Status: {resp.status_code}")
    
    # Look for API endpoints in JavaScript
    if '/static/js/' in resp.text:
        import re
        api_patterns = re.findall(r'["\']/(api|graphql|v1|v2)/[^"\']+["\']', resp.text)
        if api_patterns:
            print(f"[+] Found API endpoints in JS: {set(api_patterns)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
