#!/usr/bin/env python3
"""
Fetch and analyze the JavaScript file
"""

import requests

BASE_URL = "https://ctfchallange-1.onrender.com"

def fetch_javascript():
    """Fetch app.js"""
    print("[*] Fetching app.js")
    print("=" * 80)
    
    response = requests.get(BASE_URL + '/app.js')
    print(f"Status: {response.status_code}")
    print(f"\nJavaScript content:\n")
    print(response.text)
    print("\n" + "=" * 80)
    
    return response.text

def fetch_css():
    """Fetch style.css for completeness"""
    print("\n[*] Fetching style.css")
    print("=" * 80)
    
    try:
        response = requests.get(BASE_URL + '/style.css')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"\nCSS content (first 500 chars):\n")
            print(response.text[:500])
    except Exception as e:
        print(f"Error: {e}")

def main():
    js_content = fetch_javascript()
    fetch_css()
    
    # Analyze the JavaScript
    if '/status' in js_content:
        print("\n[*] Found /status endpoint reference in JavaScript")
    
    if 'fetch' in js_content:
        print("[*] JavaScript uses fetch API")

if __name__ == "__main__":
    main()
