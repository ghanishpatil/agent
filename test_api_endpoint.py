#!/usr/bin/env python3
"""
Test API endpoint to find correct registration path
"""

import requests
import json

API_BASE = "https://api.cyberspacevr.in"

def test_endpoints():
    """Test various endpoint patterns"""
    
    test_data = {
        'username': 'testuser_probe',
        'email': 'testprobe@example.com',
        'password': 'TestPass123!@#'
    }
    
    endpoints = [
        '/register',
        '/auth/register',
        '/api/register',
        '/api/auth/register',
        '/v1/register',
        '/v1/auth/register',
        '/signup',
        '/auth/signup',
    ]
    
    print(f"[*] Testing API endpoints at {API_BASE}")
    print()
    
    for endpoint in endpoints:
        url = f"{API_BASE}{endpoint}"
        print(f"Testing: {url}")
        
        try:
            # Test with JSON
            resp = requests.post(url, json=test_data, timeout=10)
            print(f"  JSON -> Status: {resp.status_code}")
            if resp.status_code != 404:
                print(f"  Response: {resp.text[:300]}")
                if resp.status_code in [200, 201]:
                    print(f"  ✓ SUCCESS! Use this endpoint: {endpoint}")
                    return endpoint
            
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
        
        print()
    
    return None

if __name__ == "__main__":
    endpoint = test_endpoints()
    if endpoint:
        print(f"\n[+] Found working endpoint: {endpoint}")
    else:
        print("\n[-] No working endpoint found - check API documentation")
