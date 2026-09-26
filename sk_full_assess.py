import requests
import re
import json

BASE_URL = "https://smartkopargaonhackathon.vercel.app"
session = requests.Session()

print("="*80)
print("SMART KOPARGAON - COMPREHENSIVE SECURITY ASSESSMENT")
print("="*80)

# Fetch main JS bundle
print("\n[1] Fetching JavaScript bundle...")
resp = session.get(f"{BASE_URL}/assets/index-UN4y_Obw.js", timeout=15)
if resp.status_code == 200:
    js_content = resp.text
    print(f"[+] Got JS bundle ({len(js_content)} bytes)")
    
    with open("sk_bundle.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    
    # Find API endpoints
    print("\n[2] Extracting API endpoints...")
    api_patterns = [
        r'"/api/[^"]+',
        r"'/api/[^']+",
        r'`/api/[^`]+',
    ]
    
    endpoints = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, js_content)
        endpoints.update(matches)
    
    print(f"[+] Found {len(endpoints)} API endpoints:")
    for ep in sorted(endpoints):
        print(f"    {ep}")
    
    # Look for Firebase config
    print("\n[3] Searching for Firebase configuration...")
    firebase_patterns = [
        r'apiKey["\s:]+([A-Za-z0-9_-]+)',
        r'authDomain["\s:]+([^"\']+)',
        r'projectId["\s:]+([^"\']+)',
        r'storageBucket["\s:]+([^"\']+)',
    ]
    
    for pattern in firebase_patterns:
        matches = re.findall(pattern, js_content)
        if matches:
            print(f"    Found: {pattern[:20]}... = {matches[0]}")
    
    # Look for hardcoded secrets
    print("\n[4] Searching for potential secrets...")
    secret_patterns = [
        (r'password["\s:]+["\']([^"\']{8,})["\']', "Password"),
        (r'secret["\s:]+["\']([^"\']{8,})["\']', "Secret"),
        (r'token["\s:]+["\']([^"\']{20,})["\']', "Token"),
        (r'key["\s:]+["\']([A-Za-z0-9_-]{20,})["\']', "API Key"),
    ]
    
    for pattern, name in secret_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            print(f"    [!] Potential {name} found: {len(matches)} instances")
    
    # Save endpoints to file
    with open("sk_endpoints.json", "w") as f:
        json.dump({"endpoints": sorted(list(endpoints))}, f, indent=2)
    print("\n[+] Endpoints saved to sk_endpoints.json")

else:
    print(f"[-] Failed to fetch JS bundle: {resp.status_code}")

print("\n[5] Testing API endpoints...")
test_endpoints = [
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/logout",
    "/api/users",
    "/api/admin",
    "/api/config",
]

for ep in test_endpoints:
    try:
        r = session.get(f"{BASE_URL}{ep}", timeout=5)
        print(f"    {ep}: {r.status_code}")
        if r.status_code == 200 and len(r.text) < 500:
            print(f"        Response: {r.text[:200]}")
    except Exception as e:
        pass

print("\n[*] Initial reconnaissance complete")
