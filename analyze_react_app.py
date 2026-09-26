#!/usr/bin/env python3
"""
Analyze the React app to find API endpoints
"""

import requests
import re

BASE_URL = "https://learning-vault-15.emergent.host"

session = requests.Session()

print("="*70)
print("ANALYZING REACT APP FOR API ENDPOINTS")
print("="*70)

# Get the main JS bundle
print("\n[*] Fetching main JavaScript bundle...")
resp = session.get(f"{BASE_URL}/static/js/main.eded80be.js", timeout=10)

if resp.status_code == 200:
    js_content = resp.text
    print(f"[+] Got JS bundle ({len(js_content)} bytes)")
    
    # Save for analysis
    with open("main_bundle.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    
    # Find API endpoints
    print("\n[*] Searching for API endpoints...")
    
    # Common patterns
    api_patterns = [
        r'"/api/[^"]+',
        r"'/api/[^']+",
        r'axios\.(get|post|put|delete)\(["\']([^"\']+)',
        r'fetch\(["\']([^"\']+)',
    ]
    
    endpoints = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, js_content)
        for match in matches:
            if isinstance(match, tuple):
                endpoints.add(match[-1])
            else:
                endpoints.add(match)
    
    print(f"\n[+] Found {len(endpoints)} potential API endpoints:")
    for endpoint in sorted(endpoints):
        if '/api/' in endpoint:
            print(f"    {endpoint}")
    
    # Look for password reset logic
    print("\n[*] Searching for password reset logic...")
    reset_patterns = [
        r'reset.*password',
        r'forgot.*password',
        r'birthdate',
        r'date.*birth',
        r'verification',
    ]
    
    for pattern in reset_patterns:
        matches = re.findall(f'.{{0,100}}{pattern}.{{0,100}}', js_content, re.IGNORECASE)
        if matches:
            print(f"\n[+] Found '{pattern}' references:")
            for match in matches[:3]:  # Show first 3
                clean = match.replace('\n', ' ').strip()
                if len(clean) > 150:
                    clean = clean[:150] + "..."
                print(f"    {clean}")

else:
    print(f"[-] Failed to get JS bundle: {resp.status_code}")

print("\n[*] Analysis complete. Check main_bundle.js for full content")
