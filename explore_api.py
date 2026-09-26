#!/usr/bin/env python3
"""
Explore the API endpoints
"""

import requests
import json
import time

BASE_URL = "http://138.199.163.92:16969"

def explore_api():
    """Explore API endpoints"""
    print("[*] Exploring API...")
    
    # Check /api/health
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"\n[+] /api/health:")
    print(f"  Status: {resp.status_code}")
    print(f"  Content: {resp.text}")
    print(f"  Headers: {dict(resp.headers)}")
    
    # Try other API paths
    api_paths = [
        '/api',
        '/api/',
        '/api/version',
        '/api/status',
        '/api/info',
        '/api/config',
        '/api/debug',
        '/api/docs',
        '/api/swagger',
        '/api/openapi',
        '/api/schema',
        '/api/endpoints',
        '/api/routes',
        '/api/login',
        '/api/auth',
        '/api/authenticate',
        '/api/token',
        '/api/session',
        '/api/user',
        '/api/users',
        '/api/admin',
        '/api/documents',
        '/api/document',
        '/api/files',
        '/api/file',
        '/api/vault',
        '/api/storage',
        '/api/upload',
        '/api/download',
        '/api/list',
        '/api/search',
        '/api/query',
        '/api/flag',
        '/api/secret',
        '/api/key',
        '/api/keys',
        '/api/credentials',
        '/api/backup',
        '/api/export',
        '/api/import',
        '/api/test',
        '/api/ping',
        '/api/echo',
    ]
    
    found = []
    
    for path in api_paths:
        try:
            resp = requests.get(f"{BASE_URL}{path}", timeout=5, allow_redirects=False)
            if resp.status_code not in [404, 405]:
                print(f"\n[+] {path}:")
                print(f"  Status: {resp.status_code}")
                print(f"  Length: {len(resp.text)}")
                if len(resp.text) < 1000:
                    print(f"  Content: {resp.text}")
                found.append(path)
        except Exception as e:
            pass
        time.sleep(0.3)
    
    return found

def try_api_methods(path):
    """Try different HTTP methods on an endpoint"""
    print(f"\n[*] Testing methods on {path}...")
    
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
    
    for method in methods:
        try:
            resp = requests.request(method, f"{BASE_URL}{path}", timeout=5)
            if resp.status_code not in [404, 405]:
                print(f"  {method}: {resp.status_code} - {resp.text[:100]}")
        except:
            pass

def try_api_with_params():
    """Try API with various parameters"""
    print("\n[*] Trying API with parameters...")
    
    params_list = [
        {'debug': '1'},
        {'debug': 'true'},
        {'verbose': '1'},
        {'admin': '1'},
        {'test': '1'},
        {'format': 'json'},
        {'format': 'xml'},
        {'id': '1'},
        {'user': 'admin'},
        {'token': 'test'},
    ]
    
    for params in params_list:
        try:
            resp = requests.get(f"{BASE_URL}/api/health", params=params, timeout=5)
            if resp.text != '{"status":"operational","version":"3.0.1"}':
                print(f"  [!] Different response with {params}:")
                print(f"      {resp.text[:200]}")
        except:
            pass

def check_api_headers():
    """Check if API responds differently to headers"""
    print("\n[*] Checking API with different headers...")
    
    headers_list = [
        {'X-Admin': 'true'},
        {'X-Debug': '1'},
        {'X-Test': '1'},
        {'X-API-Key': 'test'},
        {'Authorization': 'Bearer test'},
        {'X-Forwarded-For': '127.0.0.1'},
        {'X-Real-IP': '127.0.0.1'},
        {'X-Original-URL': '/admin'},
        {'X-Rewrite-URL': '/admin'},
        {'Content-Type': 'application/json'},
    ]
    
    for headers in headers_list:
        try:
            resp = requests.get(f"{BASE_URL}/api/health", headers=headers, timeout=5)
            if resp.text != '{"status":"operational","version":"3.0.1"}':
                print(f"  [!] Different response with {headers}:")
                print(f"      {resp.text[:200]}")
        except:
            pass

def fuzz_api_paths():
    """Fuzz for hidden API paths"""
    print("\n[*] Fuzzing for hidden paths...")
    
    # Common words
    words = [
        'admin', 'test', 'debug', 'dev', 'internal', 'private', 'secret',
        'hidden', 'backup', 'old', 'new', 'v1', 'v2', 'v3', 'beta', 'alpha',
        'staging', 'prod', 'production', 'development'
    ]
    
    for word in words:
        path = f"/api/{word}"
        try:
            resp = requests.get(f"{BASE_URL}{path}", timeout=3, allow_redirects=False)
            if resp.status_code not in [404, 405]:
                print(f"  [+] {path}: {resp.status_code} - {resp.text[:100]}")
        except:
            pass

if __name__ == "__main__":
    print("="*60)
    print("API Exploration")
    print("="*60)
    
    found = explore_api()
    
    print("\n" + "="*60)
    print(f"Found {len(found)} interesting endpoints")
    print("="*60)
    
    if found:
        for path in found:
            try_api_methods(path)
            time.sleep(1)
    
    try_api_with_params()
    check_api_headers()
    fuzz_api_paths()
    
    print("\n[*] API exploration complete!")
