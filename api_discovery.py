#!/usr/bin/env python3
"""
API Discovery and Database Detection
"""

import requests
import re
import json

base_url = "http://fresh-start-267.emergent.host"

print("="*60)
print("API DISCOVERY & DATABASE DETECTION")
print("="*60)

# Get main page and extract JS
print("\n[1] Fetching main application...")
resp = requests.get(base_url)
html = resp.text

# Extract JS file URLs
js_files = re.findall(r'src="(/static/js/[^"]+)"', html)
print(f"[+] Found {len(js_files)} JavaScript files")

# Download and analyze JS
for js_file in js_files:
    print(f"\n[2] Analyzing {js_file}...")
    js_url = base_url + js_file
    js_resp = requests.get(js_url)
    js_content = js_resp.text
    
    # Look for API endpoints
    api_endpoints = re.findall(r'["\']/(api|graphql|v1|v2|auth|login|register|users|tasks|admin)[^"\']*["\']', js_content)
    if api_endpoints:
        print(f"[+] Found API endpoints:")
        for endpoint in set(api_endpoints):
            print(f"    {endpoint}")
    
    # Look for database references
    db_patterns = [
        r'mongodb', r'mongoose', r'postgres', r'postgresql', 
        r'mysql', r'sqlite', r'redis', r'firebase', r'firestore',
        r'dynamodb', r'cassandra', r'mariadb'
    ]
    
    for pattern in db_patterns:
        if re.search(pattern, js_content, re.IGNORECASE):
            print(f"[!] Found database reference: {pattern}")
    
    # Look for API base URLs
    api_bases = re.findall(r'baseURL["\']?\s*:\s*["\']([^"\']+)["\']', js_content)
    if api_bases:
        print(f"[+] Found API base URLs: {api_bases}")
    
    # Look for authentication tokens/keys
    if 'token' in js_content.lower() or 'jwt' in js_content.lower():
        print(f"[+] Found authentication references (JWT/Token)")
    
    # Look for environment variables
    env_vars = re.findall(r'process\.env\.([A-Z_]+)', js_content)
    if env_vars:
        print(f"[+] Found environment variables: {set(env_vars)}")

# Try common API endpoints
print("\n[3] Testing common API endpoints...")
common_apis = [
    '/api', '/api/v1', '/api/v2',
    '/api/users', '/api/tasks', '/api/auth',
    '/api/login', '/api/register',
    '/api/admin', '/api/config',
    '/graphql', '/api/graphql'
]

for endpoint in common_apis:
    try:
        url = base_url + endpoint
        resp = requests.get(url, timeout=3)
        if resp.status_code != 404:
            print(f"[+] {endpoint} - Status: {resp.status_code}")
            if resp.headers.get('content-type', '').startswith('application/json'):
                try:
                    print(f"    Response: {json.dumps(resp.json(), indent=2)[:200]}")
                except:
                    pass
    except:
        pass

# Try OPTIONS request to discover methods
print("\n[4] Testing HTTP methods on /api...")
try:
    resp = requests.options(f"{base_url}/api", timeout=3)
    if 'allow' in resp.headers:
        print(f"[+] Allowed methods: {resp.headers['allow']}")
except:
    pass

# Check for GraphQL introspection
print("\n[5] Testing GraphQL introspection...")
try:
    introspection_query = {
        "query": """
        {
            __schema {
                types {
                    name
                    kind
                    description
                }
            }
        }
        """
    }
    resp = requests.post(f"{base_url}/graphql", json=introspection_query, timeout=5)
    if resp.status_code == 200:
        try:
            data = resp.json()
            if 'data' in data:
                print("[!] GraphQL introspection is enabled!")
                types = data.get('data', {}).get('__schema', {}).get('types', [])
                print(f"[+] Found {len(types)} GraphQL types")
                for t in types[:10]:
                    print(f"    - {t.get('name')}: {t.get('kind')}")
        except:
            print("GraphQL response not JSON")
except Exception as e:
    print(f"Error: {e}")

# Check robots.txt for hints
print("\n[6] Checking robots.txt...")
try:
    resp = requests.get(f"{base_url}/robots.txt", timeout=3)
    if resp.status_code == 200:
        print(resp.text)
except:
    pass

print("\n" + "="*60)
