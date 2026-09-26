#!/usr/bin/env python3
"""
Explore SECTOR-7 web service for clues
"""

import requests
import re

TARGET = "http://13.206.58.35:8080"

def explore_paths():
    """Try various paths to find clues"""
    print("[*] Exploring web service...")
    
    paths = [
        '/', '/kaal', '/KAAL', '/sector-7', '/SECTOR-7',
        '/challenge', '/download', '/binary', '/flag',
        '/imei', '/phone', '/9000', '/elite', '/1337',
        '/dtmf', '/knock', '/gate', '/enter', '/access',
        '/robots.txt', '/sitemap.xml', '/.git', '/admin',
        '/api', '/status', '/health', '/info'
    ]
    
    for path in paths:
        try:
            r = requests.get(f"{TARGET}{path}", timeout=3)
            if r.status_code == 200:
                print(f"\n[+] {path} - Status: {r.status_code}")
                print(f"    Content: {r.text[:500]}")
            elif r.status_code != 404:
                print(f"\n[?] {path} - Status: {r.status_code}")
        except Exception as e:
            pass

def check_headers():
    """Check response headers for clues"""
    print("\n[*] Checking headers...")
    try:
        r = requests.get(TARGET, timeout=3)
        print(f"Headers: {dict(r.headers)}")
        
        # Check for custom headers
        for key, value in r.headers.items():
            if key.lower().startswith('x-') or 'kaal' in key.lower():
                print(f"[!] Custom header: {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")

def try_post_requests():
    """Try POST requests with various data"""
    print("\n[*] Trying POST requests...")
    
    payloads = [
        {'knock': '9000'},
        {'kaal': 'true'},
        {'imei': '123456789012345'},
        {'sequence': '9000,9001,9002'},
        {'password': 'KAAL'},
    ]
    
    for payload in payloads:
        try:
            r = requests.post(TARGET, data=payload, timeout=3)
            if r.status_code != 405:  # Method not allowed
                print(f"[+] POST with {payload}: {r.status_code}")
                if r.text:
                    print(f"    Response: {r.text[:200]}")
        except:
            pass

def check_source_code():
    """Look for hidden clues in HTML source"""
    print("\n[*] Analyzing HTML source...")
    try:
        r = requests.get(TARGET, timeout=3)
        
        # Look for comments
        comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
        if comments:
            print("[+] Found HTML comments:")
            for comment in comments:
                print(f"    {comment.strip()}")
        
        # Look for hidden elements
        hidden = re.findall(r'<[^>]*hidden[^>]*>(.*?)</[^>]*>', r.text, re.DOTALL)
        if hidden:
            print("[+] Found hidden elements:")
            for h in hidden:
                print(f"    {h.strip()}")
        
        # Look for data attributes
        data_attrs = re.findall(r'data-[a-z-]+="([^"]*)"', r.text)
        if data_attrs:
            print("[+] Found data attributes:")
            for attr in data_attrs:
                print(f"    {attr}")
                
    except Exception as e:
        print(f"Error: {e}")

def main():
    print(f"[*] SECTOR-7 Web Service Explorer")
    print(f"[*] Target: {TARGET}\n")
    
    check_source_code()
    check_headers()
    explore_paths()
    try_post_requests()

if __name__ == "__main__":
    main()
