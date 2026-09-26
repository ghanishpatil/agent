#!/usr/bin/env python3
"""
Check site status after Cloudflare block - maybe this IS the crash condition
"""

import requests
import time

base_url = "http://fresh-start-267.emergent.host"

print("="*70)
print("CHECKING SITE AFTER CLOUDFLARE BLOCK")
print("="*70)

# Try different endpoints without aggressive behavior
endpoints_to_check = [
    '/',
    '/flag',
    '/api/flag',
    '/crashed',
    '/admin/flag',
    '/api/admin/flag',
    '/api/status',
    '/status',
    '/health',
    '/api/health'
]

print("\n[1] Checking various endpoints...")
for endpoint in endpoints_to_check:
    try:
        # Use a clean session with normal headers
        resp = requests.get(
            f"{base_url}{endpoint}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
            allow_redirects=True
        )
        print(f"\n{endpoint}:")
        print(f"  Status: {resp.status_code}")
        
        # Check for flag in response
        if "flag" in resp.text.lower() or "ctf{" in resp.text or "FLAG{" in resp.text:
            print(f"  *** POTENTIAL FLAG FOUND ***")
            print(f"  Response preview: {resp.text[:500]}")
            
            # Try to extract flag
            import re
            flags = re.findall(r'[Ff][Ll][Aa][Gg]\{[^}]+\}', resp.text)
            flags += re.findall(r'[Cc][Tt][Ff]\{[^}]+\}', resp.text)
            if flags:
                print(f"\n  EXTRACTED FLAGS: {flags}")
        
        # Show first 200 chars if interesting status code
        if resp.status_code not in [403, 404]:
            print(f"  Preview: {resp.text[:200]}")
            
    except Exception as e:
        print(f"{endpoint}: Error - {e}")
    
    time.sleep(1)  # Be polite

# Try with a fresh session and the old token
print("\n[2] Trying with authentication token...")
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTcyMWZjYzEtMTk5OS00NGViLWJjOTQtMDU0YjU4N2E2MDUzIiwiZW1haWwiOiJhZG1pbkBldGhhcmEuYWkiLCJuYW1lIjoiU3lzdGVtIEFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc3NTMzMTI2fQ.Lu6aYqa4j4EQHX463APGH0n73p_ziCQn3luWUSi-61U"

for endpoint in ['/api/users', '/api/tasks', '/api/flag', '/api/admin']:
    try:
        time.sleep(2)  # Wait between requests
        resp = requests.get(
            f"{base_url}{endpoint}",
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )
        print(f"\n{endpoint} (authenticated):")
        print(f"  Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"  Response: {resp.text[:300]}")
            
            # Check for flag
            if "flag" in resp.text.lower():
                print(f"  *** FLAG KEYWORD FOUND ***")
                print(f"  Full response: {resp.text}")
                
    except Exception as e:
        print(f"{endpoint}: {e}")

# Check if the "crash" created an error page with flag
print("\n[3] Checking for error pages...")
try:
    resp = requests.get(base_url, timeout=10)
    print(f"Main page status: {resp.status_code}")
    
    # Look for any flag-like patterns
    import re
    text = resp.text.lower()
    
    if "congratulations" in text or "you crashed" in text or "flag" in text:
        print("\n*** INTERESTING CONTENT FOUND ***")
        print(resp.text)
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
print("CHECK COMPLETE")
print("="*70)
print("\nNote: If Cloudflare is blocking, the 'crash' might have succeeded.")
print("The flag might appear after the block clears or on a specific endpoint.")
